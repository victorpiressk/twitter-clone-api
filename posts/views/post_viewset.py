"""
Post ViewSet.
"""

from django.db import models, transaction
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from posts.models import Post
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import (
    PollCreateSerializer,
    PostCreateSerializer,
    PostSerializer,
    ScheduledPostSerializer,
)


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
    thread: Retorna thread completa
    """

    queryset = Post.objects.all().select_related("author").prefetch_related("media")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

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
        in_reply_to = serializer.validated_data.get("in_reply_to")

        # Salvar o post
        post = serializer.save(author=self.request.user)

        # Se é uma resposta, incrementar contador do post pai
        if in_reply_to:
            in_reply_to.refresh_from_db()
            Post.objects.filter(in_reply_to=post).count()

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve create para retornar PostSerializer na resposta.

        Isso garante que a resposta contenha todos os campos (id, author, media, etc)
        em vez de apenas os campos de input do PostCreateSerializer.

        Suporta criação de posts com enquetes.
        """
        # Se tem poll no body, usar método específico
        if "poll" in request.data:
            return self.create_with_poll(request, *args, **kwargs)

        # Lógica normal (já existente)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Usar PostSerializer para retornar resposta completa
        instance = serializer.instance
        output_serializer = PostSerializer(instance, context={"request": request})
        headers = self.get_success_headers(output_serializer.data)

        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def create_with_poll(self, request, *args, **kwargs):
        """
        Criar post com enquete.

        Body:
        {
            "content": "Qual sua linguagem favorita?",
            "poll": {
                "question": "",  // opcional
                "duration_hours": 24,
                "options": ["Python", "JavaScript", "Go", "Rust"]
            }
        }
        """

        # Validar e criar post
        post_data = request.data.copy()
        poll_data = post_data.pop("poll", None)

        serializer = self.get_serializer(data=post_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        post = serializer.instance

        # Criar enquete se fornecida
        if poll_data:
            poll_serializer = PollCreateSerializer(
                data=poll_data, context={"post": post}
            )
            poll_serializer.is_valid(raise_exception=True)
            poll_serializer.save(post=post)

        # Retornar post completo com enquete
        output_serializer = PostSerializer(post, context={"request": request})
        headers = self.get_success_headers(output_serializer.data)

        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_queryset(self):
        """
        Retorna queryset de posts.

        - Listagens (list, feed): apenas posts publicados
        - Retrieve: posts publicados + posts agendados do próprio usuário
        """
        queryset = (
            Post.objects.all()
            .select_related("author")
            .prefetch_related("media", "poll", "location")
        )

        # Se for retrieve (detalhe de um post específico), permitir autor ver agendado
        if self.action == "retrieve":
            if self.request.user.is_authenticated:
                # Posts publicados OU posts agendados do usuário
                queryset = queryset.filter(
                    models.Q(scheduled_for__isnull=True)
                    | models.Q(scheduled_for__lte=timezone.now())
                    | models.Q(author=self.request.user)
                )
            else:
                # Não autenticado: apenas publicados
                queryset = queryset.filter(
                    models.Q(scheduled_for__isnull=True)
                    | models.Q(scheduled_for__lte=timezone.now())
                )
        elif self.action != "scheduled":
            # Listagens: apenas publicados
            queryset = queryset.filter(
                models.Q(scheduled_for__isnull=True)
                | models.Q(scheduled_for__lte=timezone.now())
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Retorna detalhes de um post.
        
        ATUALIZADO: Incrementa contador de views automaticamente.
        """
        instance = self.get_object()
        
        # Incrementar views_count
        instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def scheduled(self, request):
        """
        Lista posts agendados do usuário autenticado.

        Endpoint: GET /api/posts/scheduled/

        Retorna posts que estão agendados para publicação futura.
        Apenas o próprio usuário pode ver seus posts agendados.
        """
        # Buscar posts agendados do usuário
        scheduled_posts = (
            Post.objects.scheduled()
            .filter(author=request.user)
            .select_related("author")
            .order_by("scheduled_for")
        )

        serializer = ScheduledPostSerializer(scheduled_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def feed(self, request):
        """
        Feed personalizado: posts de usuários que o usuário segue.
        """
        # Pegar IDs dos usuários que o usuário segue
        following_ids = request.user.following.values_list("following_id", flat=True)

        # Posts dos usuários seguidos + posts do próprio usuário
        posts = (
            Post.objects.published()
            .filter(author_id__in=list(following_ids) + [request.user.id])
            .select_related("author")
            .prefetch_related("media", "poll", "location")
        )

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
            author=request.user, is_retweet=True, retweet_of=original_post
        ).exists()

        if already_retweeted:
            return Response(
                {"detail": "Você já retweetou este post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Criar retweet e incrementar contador atomicamente
        with transaction.atomic():
            retweet = Post.objects.create(
                author=request.user,
                content="",
                is_retweet=True,
                retweet_of=original_post,
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
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar tamanho do comentário
        if len(comment) > 280:
            return Response(
                {"detail": "Comentário não pode exceder 280 caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Criar quote retweet e incrementar contador atomicamente
        with transaction.atomic():
            quote_retweet = Post.objects.create(
                author=request.user,
                content=comment,
                is_retweet=True,
                retweet_of=original_post,
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
                author=request.user, is_retweet=True, retweet_of=original_post
            )
        except Post.DoesNotExist:
            return Response(
                {"detail": "Você não retweetou este post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Deletar retweet e decrementar contador atomicamente
        with transaction.atomic():
            retweet.delete()

            # Decrementar contador (garantir que não fique negativo)
            if original_post.retweets_count > 0:
                original_post.retweets_count -= 1
                original_post.save(update_fields=["retweets_count"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    # REPLIES

    @action(detail=True, methods=["get"])
    def replies(self, request, pk=None):
        """
        Lista todas as respostas (replies) de um post.
        """
        post = self.get_object()

        # Buscar posts que são respostas deste post
        replies = (
            Post.objects.filter(in_reply_to=post)
            .select_related("author")
            .prefetch_related("media")
            .order_by("created_at")
        )

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
            thread_posts.insert(0, current_post)
            current_post = current_post.in_reply_to

        serializer = self.get_serializer(thread_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Lista posts mais vistos (trending).
        
        Endpoint: GET /api/posts/trending/
        
        Query params:
        - limit: número de posts (padrão: 10, máximo: 50)
        - period: período (today, week, month, all - padrão: all)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Pegar limite (padrão 10, máximo 50)
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)  # Máximo 50
        
        # Pegar período
        period = request.query_params.get('period', 'all')
        
        # Filtrar por período
        queryset = Post.objects.published()
        
        if period == 'today':
            start_date = timezone.now() - timedelta(days=1)
            queryset = queryset.filter(created_at__gte=start_date)
        elif period == 'week':
            start_date = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(created_at__gte=start_date)
        elif period == 'month':
            start_date = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=start_date)
        # 'all': sem filtro de data
        
        # Ordenar por views (mais vistos primeiro)
        trending_posts = queryset.order_by('-views_count')[:limit]
        
        serializer = self.get_serializer(trending_posts, many=True)
        return Response(serializer.data)
