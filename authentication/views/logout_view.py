"""
Logout view.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class LogoutView(APIView):
    """
    View para logout de usuários.
    
    POST /api/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Deleta o token do usuário."""
        # Deletar token do usuário
        request.user.auth_token.delete()
        
        return Response(
            {'detail': 'Logout realizado com sucesso.'},
            status=status.HTTP_200_OK
        )
    