"""
Comment ViewSet.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from posts.models import Comment
from posts.serializers import CommentSerializer
from posts.permissions import IsAuthorOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para comentários.
    
    list: Lista todos os comentários
    retrieve: Detalhes de um comentário
    create: Cria novo comentário
    update: Atualiza comentário (apenas autor)
    destroy: Deleta comentário (apenas autor)
    """
    queryset = Comment.objects.all().select_related('user', 'post')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        """Define o usuário como o usuário autenticado."""
        serializer.save(user=self.request.user)
    