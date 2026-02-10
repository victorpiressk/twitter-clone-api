"""
Post model - Postagens do sistema.
"""

from django.conf import settings
from django.db import models

from posts.models import Location

class Post(models.Model):
    """
    Modelo para postagens (tweets).

    Representa uma publicação feita por um usuário.
    Pode ser um post normal, um retweet de outro post, ou uma resposta a outro post.
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

    # Campos de Retweet
    is_retweet = models.BooleanField(
        default=False,
        verbose_name="É retweet",
        help_text="Indica se este post é um retweet de outro post",
    )

    retweet_of = models.ForeignKey(
        "self",
        related_name="retweets",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Retweet de",
        help_text="Post original sendo retweetado (se aplicável)",
    )

    retweets_count = models.IntegerField(
        default=0,
        verbose_name="Quantidade de retweets",
        help_text="Contador de quantas vezes este post foi retweetado",
    )

    # CAMPO - Reply
    in_reply_to = models.ForeignKey(
        "self",
        related_name="replies",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Em resposta a",
        help_text="Post ao qual este post está respondendo (se aplicável)",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    location = models.ForeignKey(
        Location,
        related_name="posts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Localização",
        help_text="Local onde o post foi criado"
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "-created_at"]),
            models.Index(fields=["is_retweet"]),
            models.Index(fields=["retweet_of"]),
            models.Index(fields=["in_reply_to"]),  # NOVO ÍNDICE
        ]

    def __str__(self):
        if self.is_retweet and self.retweet_of:
            return f"{self.author.username} retweetou: {self.retweet_of.content[:50]}"
        return f"{self.author.username}: {self.content[:50]}"

    @property
    def likes_count(self):
        """Retorna quantidade de curtidas."""
        return self.likes.count()

    @property
    def comments_count(self):
        """Retorna quantidade de comentários."""
        return self.comments.count()
