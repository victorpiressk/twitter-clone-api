from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

from posts.models import Post
from posts.serializers import (
    PostCreateSerializer,
    PostSerializer,
    ScheduledPostSerializer,
)

User = get_user_model()


@pytest.mark.django_db
class TestScheduledPostsSerializer:
    """Testes para serializers de posts agendados."""

    def test_serialize_post_with_scheduled_for(self):
        """Testa serialização de post agendado."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future = timezone.now() + timedelta(hours=2)
        post = Post.objects.create(
            author=user, content="Post agendado", scheduled_for=future
        )

        serializer = PostSerializer(post)
        data = serializer.data

        assert "scheduled_for" in data
        assert data["scheduled_for"] is not None
        assert "is_published" in data
        assert data["is_published"] is False

    def test_serialize_post_without_scheduled_for(self):
        """Testa serialização de post sem agendamento."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Post normal")

        serializer = PostSerializer(post)
        data = serializer.data

        assert "scheduled_for" in data
        assert data["scheduled_for"] is None
        assert "is_published" in data
        assert data["is_published"] is True

    def test_is_published_field_readonly(self):
        """Testa que is_published é read-only."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test")

        serializer = PostSerializer(post)
        assert "is_published" in serializer.data
        assert serializer.data["is_published"] is True

    def test_create_post_with_scheduled_for_valid(self):
        """Testa criação de post com scheduled_for válido."""
        future = timezone.now() + timedelta(hours=2)

        data = {"content": "Post agendado", "scheduled_for": future.isoformat()}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_post_with_scheduled_for_in_past_fails(self):
        """Testa que scheduled_for no passado retorna erro."""
        past = timezone.now() - timedelta(hours=1)

        data = {"content": "Post no passado", "scheduled_for": past.isoformat()}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "scheduled_for" in serializer.errors
        assert "passado" in str(serializer.errors["scheduled_for"][0]).lower()

    def test_create_post_with_scheduled_for_near_past_allowed(self):
        """Testa margem de erro de 5 minutos no passado."""
        # 3 minutos atrás (dentro da margem de 5 min)
        near_past = timezone.now() - timedelta(minutes=3)

        data = {"content": "Post 3 min atrás", "scheduled_for": near_past.isoformat()}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_post_with_scheduled_for_null(self):
        """Testa criação com scheduled_for = null."""
        data = {"content": "Post normal", "scheduled_for": None}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_post_without_scheduled_for_field(self):
        """Testa criação sem fornecer scheduled_for (campo opcional)."""
        data = {"content": "Post sem scheduled_for"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_scheduled_post_serializer_fields(self):
        """Testa campos do ScheduledPostSerializer."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future = timezone.now() + timedelta(hours=2)
        post = Post.objects.create(
            author=user, content="Post agendado", scheduled_for=future
        )

        serializer = ScheduledPostSerializer(post)
        data = serializer.data

        assert "id" in data
        assert "content" in data
        assert "scheduled_for" in data
        assert "is_published" in data
        assert "created_at" in data
        assert "author" in data

    def test_scheduled_post_serializer_multiple_posts(self):
        """Testa serialização de múltiplos posts agendados."""
        user = User.objects.create_user(username="testuser", password="pass123")

        posts = []
        for i in range(3):
            future = timezone.now() + timedelta(hours=i + 1)
            post = Post.objects.create(
                author=user, content=f"Post {i}", scheduled_for=future
            )
            posts.append(post)

        serializer = ScheduledPostSerializer(posts, many=True)
        data = serializer.data

        assert len(data) == 3
        assert all("scheduled_for" in item for item in data)
