"""
Signals para notificações de likes e follows.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Like, Notification
from users.models import Follow


@receiver(post_save, sender=Like)
def create_notification_on_like(sender, instance, created, **kwargs):
    """
    Cria notificação quando alguém curte um post.

    Não notifica se curtir próprio post.
    """
    if not created:
        return

    # Não notificar se curtir próprio post
    if instance.user != instance.post.author:
        Notification.objects.get_or_create(
            recipient=instance.post.author,
            actor=instance.user,
            notification_type="like",
            post=instance.post,
        )


@receiver(post_save, sender=Follow)
def create_notification_on_follow(sender, instance, created, **kwargs):
    """
    Cria notificação quando alguém segue um usuário.
    """
    if not created:
        return

    Notification.objects.get_or_create(
        recipient=instance.following,
        actor=instance.follower,
        notification_type="follow",
        post=None,  # Follow não tem post relacionado
    )
