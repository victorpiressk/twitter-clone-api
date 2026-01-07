"""
User ViewSet.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.models import User
from users.serializers import UserSerializer, UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações com usuários.
    
    list: Lista todos os usuários
    retrieve: Detalhes de um usuário
    create: Cria novo usuário (registro)
    update: Atualiza usuário
    destroy: Deleta usuário
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        """Retorna serializer apropriado para cada ação."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Define permissões por ação."""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna dados do usuário autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """Lista seguidores de um usuário."""
        user = self.get_object()
        followers = user.followers.all()
        
        # Pegar os usuários que seguem (follower)
        follower_users = [follow.follower for follow in followers]
        serializer = UserSerializer(follower_users, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """Lista usuários que um usuário segue."""
        user = self.get_object()
        following = user.following.all()
        
        # Pegar os usuários sendo seguidos (following)
        following_users = [follow.following for follow in following]
        serializer = UserSerializer(following_users, many=True)
        
        return Response(serializer.data)
    