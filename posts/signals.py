"""
Signals para notificações de posts.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Notification, Post
from posts.utils import extract_mentions


@receiver(post_save, sender=Post)
def create_notification_on_post(sender, instance, created, **kwargs):
    """
    Cria notificações quando um post é criado.

    Casos:
    1. Reply: Notifica autor do post original
    2. Retweet: Notifica autor do post retweetado
    3. Mention: Notifica usuários mencionados
    """
    if not created:
        return

    # 1. NOTIFICAÇÃO DE REPLY
    if instance.in_reply_to:
        # Não notificar se responder a si mesmo
        if instance.author != instance.in_reply_to.author:
            Notification.objects.get_or_create(
                recipient=instance.in_reply_to.author,
                actor=instance.author,
                notification_type="reply",
                post=instance,
            )

    # 2. NOTIFICAÇÃO DE RETWEET
    if instance.is_retweet and instance.retweet_of:
        # Não notificar se retweet próprio
        if instance.author != instance.retweet_of.author:
            Notification.objects.get_or_create(
                recipient=instance.retweet_of.author,
                actor=instance.author,
                notification_type="retweet",
                post=instance.retweet_of,
            )

    # 3. NOTIFICAÇÃO DE MENTION
    usernames = extract_mentions(instance.content)
    if usernames:
        from django.contrib.auth import get_user_model

        User = get_user_model()

        for username in usernames:
            try:
                mentioned_user = User.objects.get(username__iexact=username)

                # Não notificar se mencionar a si mesmo
                if mentioned_user != instance.author:
                    Notification.objects.get_or_create(
                        recipient=mentioned_user,
                        actor=instance.author,
                        notification_type="mention",
                        post=instance,
                    )
            except User.DoesNotExist:
                # Usuário mencionado não existe, ignorar
                pass
