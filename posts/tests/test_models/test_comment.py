from django.contrib.auth import get_user_model

import pytest

from posts.models import Comment, Post

User = get_user_model()


@pytest.mark.django_db
class TestCommentModel:
    """Testes para o model Comment."""

    def test_create_comment(self):
        """Testa criação de comentário."""
        author = User.objects.create_user(username="author", password="pass123")
        commenter = User.objects.create_user(username="commenter", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        comment = Comment.objects.create(
            user=commenter, post=post, content="Test comment"
        )

        assert comment.user == commenter
        assert comment.post == post
        assert comment.content == "Test comment"

    def test_comment_str(self):
        """Testa representação string do comentário."""
        author = User.objects.create_user(username="author", password="pass123")
        commenter = User.objects.create_user(username="commenter", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        comment = Comment.objects.create(
            user=commenter, post=post, content="Test comment"
        )

        comment_str = str(comment)
        assert "commenter" in comment_str
        assert "comentou" in comment_str or "comment" in comment_str.lower()
