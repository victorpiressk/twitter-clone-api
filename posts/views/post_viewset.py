"""
Post ViewSet.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from posts.models import Post
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import PostCreateSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações com posts.

    list: Lista todos os posts
    retrieve: Detalhes de um post
    create: Cria novo post
    update: Atualiza post (apenas autor)
    destroy: Deleta post (apenas autor)
    retweet: Retweeta um post
    quote_retweet: Retweeta com comentário
    unretweet: Desfaz retweet
    replies: Lista respostas de um post
    thread: Retorna thread completa (post + ancestrais)
    """

    queryset = Post.objects.all().select_related("author")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        """Retorna serializer apropriado para cada ação."""
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        """
        Define o autor como o usuário autenticado.
        Se in_reply_to for fornecido, incrementa comments_count do post pai.
        """
        in_reply_to = serializer.validated_data.get('in_reply_to')
        
        # Salvar o post
        post = serializer.save(author=self.request.user)
        
        # Se é uma resposta, incrementar contador do post pai
        if in_reply_to:
            in_reply_to.refresh_from_db()
            # Nota: comments_count é uma @property que conta Comment model
            # Replies são posts normais com in_reply_to, não Comments
            # Então não incrementamos aqui. Se quiser contar replies:
            # Adicione um campo replies_count ao modelo ou use Post.objects.filter(in_reply_to=post).count()

    @action(detail=False, methods=["get"])
    def feed(self, request):
        """
        Feed personalizado: posts de usuários que o usuário segue.
        """
        # Pegar IDs dos usuários que o usuário segue
        following_ids = request.user.following.values_list("following_id", flat=True)

        # Posts dos usuários seguidos + posts do próprio usuário
        posts = Post.objects.filter(
            author_id__in=list(following_ids) + [request.user.id]
        ).select_related("author")

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    # RETWEETS

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def retweet(self, request, pk=None):
        """
        Retweeta um post (retweet simples, sem comentário).
        """
        original_post = self.get_object()

        # Verificar se já retweetou
        already_retweeted = Post.objects.filter(
            author=request.user,
            is_retweet=True,
            retweet_of=original_post
        ).exists()

        if already_retweeted:
            return Response(
                {"detail": "Você já retweetou este post."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Criar retweet e incrementar contador atomicamente
        with transaction.atomic():
            retweet = Post.objects.create(
                author=request.user,
                content="",  # Retweet simples não tem conteúdo
                is_retweet=True,
                retweet_of=original_post
            )

            # Incrementar contador do post original
            original_post.retweets_count += 1
            original_post.save(update_fields=["retweets_count"])

        serializer = self.get_serializer(retweet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def quote_retweet(self, request, pk=None):
        """
        Retweeta um post com comentário (quote tweet).
        """
        original_post = self.get_object()
        comment = request.data.get("content", "").strip()

        # Validar que há comentário
        if not comment:
            return Response(
                {"detail": "Quote retweet deve conter um comentário."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar tamanho do comentário
        if len(comment) > 280:
            return Response(
                {"detail": "Comentário não pode exceder 280 caracteres."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Criar quote retweet e incrementar contador atomicamente
        with transaction.atomic():
            quote_retweet = Post.objects.create(
                author=request.user,
                content=comment,
                is_retweet=True,
                retweet_of=original_post
            )

            # Incrementar contador do post original
            original_post.retweets_count += 1
            original_post.save(update_fields=["retweets_count"])

        serializer = self.get_serializer(quote_retweet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def unretweet(self, request, pk=None):
        """
        Desfaz retweet de um post.
        """
        original_post = self.get_object()

        # Buscar retweet do usuário
        try:
            retweet = Post.objects.get(
                author=request.user,
                is_retweet=True,
                retweet_of=original_post
            )
        except Post.DoesNotExist:
            return Response(
                {"detail": "Você não retweetou este post."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deletar retweet e decrementar contador atomicamente
        with transaction.atomic():
            retweet.delete()

            # Decrementar contador (garantir que não fique negativo)
            if original_post.retweets_count > 0:
                original_post.retweets_count -= 1
                original_post.save(update_fields=["retweets_count"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    # ACTIONS - REPLIES

    @action(detail=True, methods=["get"])
    def replies(self, request, pk=None):
        """
        Lista todas as respostas (replies) de um post.
        """
        post = self.get_object()
        
        # Buscar posts que são respostas deste post
        replies = Post.objects.filter(
            in_reply_to=post
        ).select_related("author").order_by("created_at")

        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def thread(self, request, pk=None):
        """
        Retorna a thread completa (post + todos os ancestrais).
        Útil para ver a conversa inteira.
        """
        post = self.get_object()
        thread_posts = []

        # Percorrer para trás pegando posts pais
        current_post = post
        while current_post:
            thread_posts.insert(0, current_post)  # Adiciona no início
            current_post = current_post.in_reply_to

        serializer = self.get_serializer(thread_posts, many=True)
        return Response(serializer.data)
