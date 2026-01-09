"""
Comment model - Comentários em posts.
"""

from django.conf import settings
from django.db import models


class Comment(models.Model):
    """
    Modelo para comentários em posts.

    Permite que usuários comentem nas postagens.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Usuário",
    )

    post = models.ForeignKey(
        "posts.Post",
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Post",
    )

    content = models.TextField(
        max_length=280,
        verbose_name="Conteúdo",
        help_text="Conteúdo do comentário (máximo 280 caracteres)",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} comentou em {self.post.id}"
