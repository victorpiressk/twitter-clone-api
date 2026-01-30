"""
User ViewSet.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from PIL import Image

from users.models import User
from users.permissions import IsOwnerOrReadOnly
from users.serializers import UserCreateSerializer, UserSerializer


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
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        """Define permissões por ação."""
        if self.action == "create":
            return [AllowAny()]
        if self.action in ["list", "retrieve", "followers", "following"]:
            return [AllowAny()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        """
        Valida upload de imagens antes de atualizar.
        """
        # Validar banner se fornecido
        banner = self.request.FILES.get('banner')
        if banner:
            self._validate_image(banner, max_size_mb=5, field_name='banner')
        
        # Validar profile_image se fornecido
        profile_image = self.request.FILES.get('profile_image')
        if profile_image:
            self._validate_image(profile_image, max_size_mb=5, field_name='profile_image')
        
        serializer.save()

    def _validate_image(self, image_file, max_size_mb=5, field_name='image'):
        """
        Valida tamanho e formato de imagem.
        
        Args:
            image_file: Arquivo de imagem
            max_size_mb: Tamanho máximo em MB
            field_name: Nome do campo (para mensagem de erro)
        
        Raises:
            ValidationError: Se imagem for inválida
        """
        from rest_framework.exceptions import ValidationError
        
        # Validar tamanho
        max_size_bytes = max_size_mb * 1024 * 1024
        if image_file.size > max_size_bytes:
            raise ValidationError({
                field_name: f"Imagem muito grande. Tamanho máximo: {max_size_mb}MB"
            })
        
        # Validar formato
        allowed_formats = ['JPEG', 'PNG', 'WEBP', 'JPG']
        try:
            img = Image.open(image_file)
            if img.format not in allowed_formats:
                raise ValidationError({
                    field_name: f"Formato inválido. Formatos aceitos: {', '.join(allowed_formats)}"
                })
        except Exception:
            raise ValidationError({
                field_name: "Arquivo de imagem inválido ou corrompido."
            })

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