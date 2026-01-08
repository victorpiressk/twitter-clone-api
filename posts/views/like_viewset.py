"""
Like ViewSet.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from posts.models import Like
from posts.serializers import LikeSerializer


class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para curtidas.
    
    list: Lista todas as curtidas
    create: Curtir um post
    destroy: Descurtir um post
    """
    queryset = Like.objects.all().select_related('user', 'post')
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    # Desabilitar métodos não utilizados
    http_method_names = ['get', 'post', 'delete']
    
    def get_permissions(self):
        """Define permissões por ação."""
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """
        Curtir um post.
        """
        # Automaticamente define o user como o usuário autenticado
        data = request.data.copy()
        data['user'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar se já não curtiu
        if Like.objects.filter(
            user=request.user,
            post=serializer.validated_data['post']
        ).exists():
            return Response(
                {'detail': 'Você já curtiu este post.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """
        Descurtir um post.
        """
        instance = self.get_object()
        
        # Verificar se o usuário autenticado é quem curtiu
        if instance.user != request.user:
            return Response(
                {'detail': 'Você não tem permissão para esta ação.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    