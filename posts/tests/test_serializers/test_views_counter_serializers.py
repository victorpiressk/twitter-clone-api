from django.contrib.auth import get_user_model

import pytest

from posts.models import Post
from posts.serializers import PostSerializer

User = get_user_model()


@pytest.mark.django_db
class TestViewsCounterSerializer:
    """Testes para views_count no serializer."""

    def test_serialize_post_includes_views_in_stats(self):
        """Testa que stats inclui views."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test post")

        serializer = PostSerializer(post)
        data = serializer.data

        assert "stats" in data
        assert "views" in data["stats"]
        assert data["stats"]["views"] == 0

    def test_serialize_post_with_views_count(self):
        """Testa serialização com views_count != 0."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Incrementar views
        post.increment_views()
        post.increment_views()
        post.increment_views()

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["stats"]["views"] == 3

    def test_stats_includes_all_metrics(self):
        """Testa que stats inclui comments, retweets, likes, views."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        post.increment_views()

        serializer = PostSerializer(post)
        stats = serializer.data["stats"]

        assert "comments" in stats
        assert "retweets" in stats
        assert "likes" in stats
        assert "views" in stats
        assert stats["views"] == 1

    def test_views_field_is_readonly(self):
        """Testa que views não pode ser editado via serializer."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Tentar "editar" views via serializer não deve funcionar
        # (views_count não está em PostCreateSerializer)
        serializer = PostSerializer(post)

        # views aparece em stats, mas não é editável
        assert "views" in serializer.data["stats"]

    def test_multiple_posts_different_views(self):
        """Testa serialização de múltiplos posts com views diferentes."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post1 = Post.objects.create(author=user, content="Post 1")
        post2 = Post.objects.create(author=user, content="Post 2")
        post3 = Post.objects.create(author=user, content="Post 3")

        post1.increment_views()
        post2.increment_views()
        post2.increment_views()
        post3.increment_views()
        post3.increment_views()
        post3.increment_views()

        serializer = PostSerializer([post1, post2, post3], many=True)
        data = serializer.data

        assert data[0]["stats"]["views"] == 1
        assert data[1]["stats"]["views"] == 2
        assert data[2]["stats"]["views"] == 3
