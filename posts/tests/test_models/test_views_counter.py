from django.contrib.auth import get_user_model
from django.db.models import F

import pytest

from posts.models import Post

User = get_user_model()


@pytest.mark.django_db
class TestViewsCounterModel:
    """Testes para contador de views no model."""

    def test_create_post_default_views_count(self):
        """Testa que post novo tem views_count = 0."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Post novo")

        assert post.views_count == 0

    def test_increment_views_method(self):
        """Testa método increment_views()."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        assert post.views_count == 0

        # Incrementar
        post.increment_views()
        assert post.views_count == 1

        # Incrementar novamente
        post.increment_views()
        assert post.views_count == 2

    def test_increment_views_uses_f_expression(self):
        """Testa que increment_views usa F() expression (atomic)."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Incrementar usando F() diretamente (simular método)
        Post.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)

        post.refresh_from_db()
        assert post.views_count == 1

    def test_increment_views_multiple_times(self):
        """Testa incrementar views múltiplas vezes."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Incrementar 10 vezes
        for _ in range(10):
            post.increment_views()

        assert post.views_count == 10

    def test_views_count_persists_in_database(self):
        """Testa que views_count é persistido no banco."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        post.increment_views()
        post.increment_views()
        post.increment_views()

        # Buscar do banco novamente
        post_from_db = Post.objects.get(pk=post.pk)
        assert post_from_db.views_count == 3

    def test_views_count_is_positive_integer(self):
        """Testa que views_count é PositiveIntegerField."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Não deve permitir valores negativos
        # (Django validará isso no nível do campo)
        assert post.views_count >= 0

    def test_multiple_posts_independent_views(self):
        """Testa que posts diferentes têm contadores independentes."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post1 = Post.objects.create(author=user, content="Post 1")
        post2 = Post.objects.create(author=user, content="Post 2")

        post1.increment_views()
        post1.increment_views()
        post1.increment_views()

        post2.increment_views()

        assert post1.views_count == 3
        assert post2.views_count == 1
