"""
Permission: IsOwnerOrReadOnly

Permite que qualquer usuário leia (GET),
mas apenas o dono do recurso pode editar/deletar.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada para permitir apenas o dono editar/deletar.
    
    - Qualquer um pode ler (GET, HEAD, OPTIONS)
    - Apenas o dono pode editar/deletar (PUT, PATCH, DELETE)
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário tem permissão para acessar o objeto.
        
        Args:
            request: Requisição HTTP
            view: View sendo acessada
            obj: Objeto sendo acessado (User neste caso)
        
        Returns:
            bool: True se tem permissão, False caso contrário
        """
        # Permitir métodos seguros (leitura) para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escrever: apenas se for o próprio usuário
        return obj == request.user
    