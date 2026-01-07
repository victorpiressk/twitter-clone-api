"""
Follow ViewSet.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import Follow
from users.serializers import FollowSerializer


class FollowViewSet(viewsets.ModelViewSet):
    """
    ViewSet para sistema de seguir/deixar de seguir.
    
    list: Lista todos os follows
    create: Seguir um usuário
    destroy: Deixar de seguir
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Seguir um usuário.
        """
        # Automaticamente define o follower como o usuário autenticado
        data = request.data.copy()
        data['follower'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar se já não está seguindo
        if Follow.objects.filter(
            follower=request.user,
            following=serializer.validated_data['following']
        ).exists():
            return Response(
                {'detail': 'Você já segue este usuário.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """
        Deixar de seguir um usuário.
        """
        instance = self.get_object()
        
        # Verificar se o usuário autenticado é o follower
        if instance.follower != request.user:
            return Response(
                {'detail': 'Você não tem permissão para esta ação.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    