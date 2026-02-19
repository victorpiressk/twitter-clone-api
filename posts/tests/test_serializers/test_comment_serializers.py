from django.contrib.auth import get_user_model

import pytest

from posts.models import Comment, Post
from posts.serializers import CommentSerializer

User = get_user_model()


@pytest.mark.django_db
class TestCommentSerializer:
    """Testes para o CommentSerializer."""

    def test_serialize_comment(self):
        """Testa serialização de comentário."""
        author = User.objects.create_user(username="author", password="pass123")
        commenter = User.objects.create_user(username="commenter", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        comment = Comment.objects.create(
            user=commenter, post=post, content="Test comment"
        )

        serializer = CommentSerializer(comment)
        data = serializer.data

        assert data["content"] == "Test comment"
        assert data["user"]["username"] == "commenter"
        assert data["post"] == post.id
        assert "created_at" in data

    def test_create_comment_valid(self):
        """Testa criação de comentário válido."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        data = {"post": post.id, "content": "New comment"}

        serializer = CommentSerializer(data=data)
        assert serializer.is_valid()

    def test_create_comment_empty_content(self):
        """Testa criação com conteúdo vazio."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        data = {"post": post.id, "content": "   "}

        serializer = CommentSerializer(data=data)
        assert not serializer.is_valid()
        assert "content" in serializer.errors
