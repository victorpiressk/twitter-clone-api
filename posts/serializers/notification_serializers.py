"""
Serializers para Notification.
"""

from rest_framework import serializers

from posts.models import Notification
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer para exibição de notificações.

    Inclui:
    - Informações completas do ator (quem fez a ação)
    - Preview do post relacionado (se houver)
    - Tipo de notificação em texto legível
    """

    actor = UserSerializer(read_only=True)

    # Informações resumidas do post (se houver)
    post_preview = serializers.SerializerMethodField()

    # Tipo de notificação legível
    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "actor",
            "notification_type",
            "notification_type_display",
            "post",
            "post_preview",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "actor",
            "notification_type",
            "notification_type_display",
            "post",
            "post_preview",
            "created_at",
        ]

    def get_post_preview(self, obj):
        """
        Retorna preview do post relacionado (se houver).

        Inclui: id, content (primeiros 100 chars), author
        """
        if not obj.post:
            return None

        return {
            "id": obj.post.id,
            "content": obj.post.content[:100],
            "author": {
                "id": obj.post.author.id,
                "username": obj.post.author.username,
            },
        }
