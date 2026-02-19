from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

from posts.models import Post

User = get_user_model()


@pytest.mark.django_db
class TestScheduledPostsModel:
    """Testes para posts agendados no model."""

    def test_create_post_without_scheduled_for(self):
        """Testa criação de post sem agendamento (publicado imediatamente)."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Post publicado agora")

        assert post.scheduled_for is None
        assert post.is_published is True

    def test_create_post_with_future_scheduled_for(self):
        """Testa criação de post agendado para o futuro."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future = timezone.now() + timedelta(hours=2)
        post = Post.objects.create(
            author=user, content="Post agendado", scheduled_for=future
        )

        assert post.scheduled_for is not None
        assert post.is_published is False

    def test_create_post_with_past_scheduled_for(self):
        """Testa post com scheduled_for no passado (já publicado)."""
        user = User.objects.create_user(username="testuser", password="pass123")

        past = timezone.now() - timedelta(hours=1)
        post = Post.objects.create(
            author=user, content="Post 'agendado' para o passado", scheduled_for=past
        )

        assert post.scheduled_for is not None
        assert post.is_published is True

    def test_is_published_property_with_null_scheduled_for(self):
        """Testa property is_published quando scheduled_for é None."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test")

        assert post.is_published is True

    def test_is_published_property_with_future_date(self):
        """Testa property is_published com data futura."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future = timezone.now() + timedelta(days=1)
        post = Post.objects.create(author=user, content="Test", scheduled_for=future)

        assert post.is_published is False

    def test_is_published_property_with_past_date(self):
        """Testa property is_published com data passada."""
        user = User.objects.create_user(username="testuser", password="pass123")

        past = timezone.now() - timedelta(hours=1)
        post = Post.objects.create(author=user, content="Test", scheduled_for=past)

        assert post.is_published is True

    def test_manager_published_returns_only_published(self):
        """Testa que Post.objects.published() retorna apenas posts publicados."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Post normal (publicado)
        post1 = Post.objects.create(author=user, content="Post 1")

        # Post agendado (futuro)
        future = timezone.now() + timedelta(hours=2)
        post2 = Post.objects.create(author=user, content="Post 2", scheduled_for=future)

        # Post com scheduled_for passado (publicado)
        past = timezone.now() - timedelta(hours=1)
        post3 = Post.objects.create(author=user, content="Post 3", scheduled_for=past)

        published = Post.objects.published()

        assert post1 in published
        assert post2 not in published  # Agendado (futuro)
        assert post3 in published
        assert published.count() == 2

    def test_manager_scheduled_returns_only_scheduled(self):
        """Testa que Post.objects.scheduled() retorna apenas posts agendados."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Post normal
        Post.objects.create(author=user, content="Post 1")

        # Post agendado (futuro)
        future = timezone.now() + timedelta(hours=2)
        post2 = Post.objects.create(author=user, content="Post 2", scheduled_for=future)

        # Post com scheduled_for passado
        past = timezone.now() - timedelta(hours=1)
        Post.objects.create(author=user, content="Post 3", scheduled_for=past)

        scheduled = Post.objects.scheduled()

        assert scheduled.count() == 1
        assert post2 in scheduled

    def test_manager_scheduled_with_multiple_future_posts(self):
        """Testa scheduled() com múltiplos posts futuros."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future1 = timezone.now() + timedelta(hours=1)
        future2 = timezone.now() + timedelta(hours=2)
        future3 = timezone.now() + timedelta(days=1)

        post1 = Post.objects.create(
            author=user, content="Post 1", scheduled_for=future1
        )
        post2 = Post.objects.create(
            author=user, content="Post 2", scheduled_for=future2
        )
        post3 = Post.objects.create(
            author=user, content="Post 3", scheduled_for=future3
        )

        scheduled = Post.objects.scheduled()

        assert scheduled.count() == 3
        assert post1 in scheduled
        assert post2 in scheduled
        assert post3 in scheduled

    def test_manager_published_excludes_future_posts(self):
        """Testa que published() exclui posts futuros."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Criar 5 posts futuros
        for i in range(5):
            future = timezone.now() + timedelta(hours=i + 1)
            Post.objects.create(
                author=user, content=f"Future post {i}", scheduled_for=future
            )

        # Criar 3 posts publicados
        for i in range(3):
            Post.objects.create(author=user, content=f"Published post {i}")

        assert Post.objects.all().count() == 8
        assert Post.objects.published().count() == 3
        assert Post.objects.scheduled().count() == 5
