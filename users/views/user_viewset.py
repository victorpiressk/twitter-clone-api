"""
User ViewSet.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.permissions import IsOwnerOrReadOnly
from users.serializers import (
    ChangePasswordSerializer,
    UserAccountSerializer,
    UserCreateSerializer,
    UserSerializer,
)


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
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "update_account":
            return UserAccountSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        if self.action in ["list", "retrieve", "followers", "following"]:
            return [AllowAny()]
        if self.action in [
            "update",
            "partial_update",
            "destroy",
            "update_account",
            "change_password",
        ]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Retorna dados do usuário autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        """Lista seguidores de um usuário."""
        user = self.get_object()
        followers = user.followers.all()

        # Pegar os usuários que seguem (follower)
        follower_users = [follow.follower for follow in followers]
        serializer = UserSerializer(follower_users, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def following(self, request, pk=None):
        """Lista usuários que um usuário segue."""
        user = self.get_object()
        following = user.following.all()

        # Pegar os usuários sendo seguidos (following)
        following_users = [follow.following for follow in following]
        serializer = UserSerializer(following_users, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="account")
    def update_account(self, request, pk=None):
        """
        Atualiza dados sensíveis da conta (email, phone, username).
        Requer senha atual para confirmar.
        """
        user = self.get_object()
        serializer = UserAccountSerializer(
            user, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="change-password")
    def change_password(self, request, pk=None):
        """
        Altera a senha do usuário.
        Requer senha atual + nova senha + confirmação.
        """
        self.get_object()  # garante permissão IsOwnerOrReadOnly
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Senha alterada com sucesso."},
            status=status.HTTP_200_OK,
        )
