"""
Comment ViewSet.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from posts.models import Comment
from posts.serializers import CommentSerializer


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
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        """Define o usuário como o usuário autenticado."""
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Atualiza comentário (apenas autor pode atualizar)."""
        comment = self.get_object()
        
        if comment.user != request.user:
            return Response(
                {'detail': 'Você não tem permissão para editar este comentário.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Deleta comentário (apenas autor pode deletar)."""
        comment = self.get_object()
        
        if comment.user != request.user:
            return Response(
                {'detail': 'Você não tem permissão para deletar este comentário.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    