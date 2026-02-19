from django.contrib.auth import get_user_model

import pytest

from posts.models import Like, Post
from posts.serializers import LikeSerializer

User = get_user_model()


@pytest.mark.django_db
class TestLikeSerializer:
    """Testes para o LikeSerializer."""

    def test_serialize_like(self):
        """Testa serialização de like."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        like = Like.objects.create(user=liker, post=post)

        serializer = LikeSerializer(like)
        data = serializer.data

        assert data["user"] == liker.id
        assert data["post"] == post.id
        assert data["user_username"] == "liker"
        assert "created_at" in data

    def test_create_like_valid(self):
        """Testa validação de like válido."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        data = {"user": liker.id, "post": post.id}

        serializer = LikeSerializer(data=data)
        assert serializer.is_valid()

        # Nota: Na prática, o user é definido pelo viewset (request.user)
        # Aqui só validamos que os dados são válidos
