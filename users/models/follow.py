"""
Follow model - Relacionamento de seguir entre usuários.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Follow(models.Model):
    """
    Modelo para relacionamento de seguir entre usuários.

    Um usuário (follower) segue outro usuário (following).
    """

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="following",
        on_delete=models.CASCADE,
        verbose_name="Seguidor",
        help_text="Usuário que está seguindo",
    )

    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="followers",
        on_delete=models.CASCADE,
        verbose_name="Seguindo",
        help_text="Usuário que está sendo seguido",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Seguir"
        verbose_name_plural = "Seguidores"
        ordering = ["-created_at"]
        unique_together = ("follower", "following")
        indexes = [
            models.Index(fields=["follower", "following"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.follower.username} segue {self.following.username}"

    def clean(self):
        """Validação: usuário não pode seguir a si mesmo."""
        if self.follower == self.following:
            raise ValidationError("Usuário não pode seguir a si mesmo.")
