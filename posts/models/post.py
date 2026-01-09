"""
Post model - Postagens do sistema.
"""

from django.conf import settings
from django.db import models


class Post(models.Model):
    """
    Modelo para postagens (tweets).

    Representa uma publicação feita por um usuário.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="posts",
        on_delete=models.CASCADE,
        verbose_name="Autor",
    )

    content = models.TextField(
        max_length=280,
        verbose_name="Conteúdo",
        help_text="Conteúdo do post (máximo 280 caracteres)",
    )

    image = models.ImageField(
        upload_to="post_images/",
        blank=True,
        null=True,
        verbose_name="Imagem",
        help_text="Imagem anexada ao post (opcional)",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"

    @property
    def likes_count(self):
        """Retorna quantidade de curtidas."""
        return self.likes.count()

    @property
    def comments_count(self):
        """Retorna quantidade de comentários."""
        return self.comments.count()
