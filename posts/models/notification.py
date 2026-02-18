"""
Modelo de Notificação.
"""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    Notificações do sistema.

    Tipos: like, retweet, reply, follow, mention
    """

    NOTIFICATION_TYPES = (
        ("like", "Curtida"),
        ("retweet", "Retweet"),
        ("reply", "Resposta"),
        ("follow", "Seguidor"),
        ("mention", "Menção"),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        on_delete=models.CASCADE,
        verbose_name="Destinatário",
        help_text="Usuário que recebe a notificação",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications_sent",
        on_delete=models.CASCADE,
        verbose_name="Autor da ação",
        help_text="Usuário que gerou a notificação",
    )

    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, verbose_name="Tipo de notificação"
    )

    post = models.ForeignKey(
        "Post",
        related_name="notifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Post relacionado",
        help_text="Post relacionado à notificação (se aplicável)",
    )

    is_read = models.BooleanField(
        default=False, verbose_name="Lida", help_text="Indica se a notificação foi lida"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["actor"]),
            models.Index(fields=["notification_type"]),
        ]
        # Evitar notificações duplicadas
        unique_together = [["recipient", "actor", "notification_type", "post"]]

    def __str__(self):
        return (
            f"{self.actor.username} → {self.recipient.username}: "
            f"{self.get_notification_type_display()}"
        )

    def mark_as_read(self):
        """Marca notificação como lida."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])
