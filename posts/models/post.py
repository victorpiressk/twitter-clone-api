"""
Post model - Postagens do sistema.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from posts.models import Location


class PostManager(models.Manager):
    """Manager customizado para Post."""

    def published(self):
        """
        Retorna apenas posts publicados (não agendados para o futuro).
        """
        return self.filter(
            models.Q(scheduled_for__isnull=True)
            | models.Q(scheduled_for__lte=timezone.now())
        )

    def scheduled(self):
        """
        Retorna apenas posts agendados para o futuro.
        """
        return self.filter(
            scheduled_for__isnull=False, scheduled_for__gt=timezone.now()
        )


class Post(models.Model):
    """
    Modelo para postagens (tweets).

    Representa uma publicação feita por um usuário.
    Pode ser um post normal, um retweet de outro post, ou uma resposta a outro post.
    """

    objects = PostManager()

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
        help_text="Local onde o post foi criado",
    )

    hashtags = models.ManyToManyField(
        "Hashtag",
        related_name="posts",
        blank=True,
        verbose_name="Hashtags",
        help_text="Hashtags extraídas do conteúdo",
    )

    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Agendado para",
        help_text="Data e hora de publicação. Se null, publica imediatamente.",
    )

    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Visualizações",
        help_text="Número de vezes que o post foi visualizado",
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
            models.Index(fields=["in_reply_to"]),
            models.Index(fields=["scheduled_for"]),
            models.Index(fields=["views_count"]),  # (para ordenação por popularidade)
            models.Index(fields=["-views_count"]),  # (ordenação decrescente)
        ]

    def __str__(self):
        if self.is_retweet and self.retweet_of:
            return f"{self.author.username} retweetou: {self.retweet_of.content[:50]}"
        return f"{self.author.username}: {self.content[:50]}"

    def increment_views(self):
        """
        Incrementa o contador de visualizações.

        Usa F() expression para evitar race conditions.
        """
        from django.db.models import F

        Post.objects.filter(pk=self.pk).update(views_count=F("views_count") + 1)
        # Refresh para ter o valor atualizado
        self.refresh_from_db(fields=["views_count"])

    @property
    def likes_count(self):
        """Retorna quantidade de curtidas."""
        return self.likes.count()

    @property
    def replies_count(self):
        """Retorna quantidade de replies."""
        return self.replies.count()

    @property
    def is_published(self):
        """
        Verifica se o post está publicado (não agendado para o futuro).
        """
        if self.scheduled_for is None:
            return True
        return timezone.now() >= self.scheduled_for
