from django.contrib.auth import get_user_model

import pytest

from posts.models import Like, Post

User = get_user_model()


@pytest.mark.django_db
class TestLikeModel:
    """Testes para o model Like."""

    def test_create_like(self):
        """Testa criação de curtida."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        like = Like.objects.create(user=liker, post=post)

        assert like.user == liker
        assert like.post == post

    def test_like_str(self):
        """Testa representação string da curtida."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        like = Like.objects.create(user=liker, post=post)

        like_str = str(like)
        assert "liker" in like_str
        assert "curtiu" in like_str or "like" in like_str.lower()

    def test_unique_like(self):
        """Testa que não pode curtir o mesmo post 2 vezes."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        # Primeiro like
        Like.objects.create(user=liker, post=post)

        # Tentar criar duplicado
        with pytest.raises(Exception):
            Like.objects.create(user=liker, post=post)

    def test_user_can_like_multiple_posts(self):
        """Testa que usuário pode curtir vários posts diferentes."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")

        post1 = Post.objects.create(author=author, content="Post 1")
        post2 = Post.objects.create(author=author, content="Post 2")
        post3 = Post.objects.create(author=author, content="Post 3")

        Like.objects.create(user=liker, post=post1)
        Like.objects.create(user=liker, post=post2)
        Like.objects.create(user=liker, post=post3)

        assert Like.objects.filter(user=liker).count() == 3
