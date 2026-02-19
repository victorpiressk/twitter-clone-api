from django.contrib.auth import get_user_model

import pytest

from posts.models import Notification, Post
from posts.serializers import NotificationSerializer

User = get_user_model()


@pytest.mark.django_db
class TestNotificationSerializer:
    """Testes para NotificationSerializer."""

    def test_serialize_notification_with_post(self):
        """Testa serialização de notificação com post."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Meu post")

        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="like", post=post
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        assert data["actor"]["username"] == "bob"
        assert data["notification_type"] == "like"
        assert data["notification_type_display"] == "Curtida"
        assert data["post"] == post.id
        assert data["is_read"] is False

    def test_serialize_notification_post_preview(self):
        """Testa campo post_preview."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Conteúdo do post")

        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="like", post=post
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        assert "post_preview" in data
        assert data["post_preview"]["id"] == post.id
        assert data["post_preview"]["content"] == "Conteúdo do post"
        assert data["post_preview"]["author"]["username"] == "alice"

    def test_serialize_notification_without_post(self):
        """Testa serialização de notificação sem post (follow)."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="follow", post=None
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        assert data["post"] is None
        assert data["post_preview"] is None

    def test_serialize_notification_truncates_long_content(self):
        """Testa que post_preview trunca conteúdo longo."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        long_content = "A" * 150  # 150 caracteres
        post = Post.objects.create(author=alice, content=long_content)

        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="like", post=post
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        # Deve truncar em 100 caracteres
        assert len(data["post_preview"]["content"]) == 100
