"""
Permission: IsAuthorOrReadOnly

Permite que qualquer usuário leia (GET),
mas apenas o autor do recurso pode editar/deletar.
"""
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada para permitir apenas o autor editar/deletar.
    
    - Qualquer um pode ler (GET, HEAD, OPTIONS)
    - Apenas o autor pode editar/deletar (PUT, PATCH, DELETE)
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário tem permissão para acessar o objeto.
        
        Args:
            request: Requisição HTTP
            view: View sendo acessada
            obj: Objeto sendo acessado (Post, Comment, etc)
        
        Returns:
            bool: True se tem permissão, False caso contrário
        """
        # Permitir métodos seguros (leitura) para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escrever: apenas se for o autor
        # Funciona para Post (obj.author) e Comment (obj.user)
        author = getattr(obj, 'author', None) or getattr(obj, 'user', None)
        return author == request.user
    