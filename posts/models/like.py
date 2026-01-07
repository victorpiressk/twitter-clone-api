"""
Like model - Curtidas em posts.
"""
from django.db import models
from django.conf import settings


class Like(models.Model):
    """
    Modelo para curtidas em posts.
    
    Registra quando um usuário curte um post.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='likes',
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )
    
    post = models.ForeignKey(
        'posts.Post',
        related_name='likes',
        on_delete=models.CASCADE,
        verbose_name='Post'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    class Meta:
        verbose_name = 'Curtida'
        verbose_name_plural = 'Curtidas'
        ordering = ['-created_at']
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user', 'post']),
            models.Index(fields=['post', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} curtiu post {self.post.id}"
    