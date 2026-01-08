"""
Post ViewSet.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from posts.permissions import IsAuthorOrReadOnly

from posts.models import Post
from posts.serializers import PostSerializer, PostCreateSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações com posts.
    
    list: Lista todos os posts
    retrieve: Detalhes de um post
    create: Cria novo post
    update: Atualiza post (apenas autor)
    destroy: Deleta post (apenas autor)
    """
    queryset = Post.objects.all().select_related('author')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    def get_serializer_class(self):
        """Retorna serializer apropriado para cada ação."""
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Define o autor como o usuário autenticado."""
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        """
        Feed personalizado: posts de usuários que o usuário segue.
        """
        # Pegar IDs dos usuários que o usuário segue
        following_ids = request.user.following.values_list('following_id', flat=True)
        
        # Posts dos usuários seguidos + posts do próprio usuário
        posts = Post.objects.filter(
            author_id__in=list(following_ids) + [request.user.id]
        ).select_related('author')
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    