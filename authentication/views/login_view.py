"""
Login view.
"""

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from authentication.serializers import LoginSerializer
from users.serializers import UserSerializer


class LoginView(generics.GenericAPIView):
    """
    View para login de usuários.

    POST /api/auth/login/
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Valida credenciais e retorna token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Obter ou criar token
        token, created = Token.objects.get_or_create(user=user)

        # Retornar dados do usuário + token
        user_serializer = UserSerializer(user)

        return Response(
            {"user": user_serializer.data, "token": token.key},
            status=status.HTTP_200_OK,
        )
