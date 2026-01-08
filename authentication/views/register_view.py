"""
Register view.
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from authentication.serializers import RegisterSerializer
from users.serializers import UserSerializer


class RegisterView(generics.GenericAPIView):
    """
    View para registro de novos usuários.
    
    POST /api/auth/register/
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Cria novo usuário e retorna token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Criar token para o usuário
        token, created = Token.objects.get_or_create(user=user)
        
        # Retornar dados do usuário + token
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    