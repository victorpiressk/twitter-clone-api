from django.urls import reverse

import pytest
from rest_framework import status

from posts.models import Comment, Post


@pytest.mark.django_db
class TestCommentViewSet:
    """Testes para o CommentViewSet."""

    def test_list_comments(self, api_client, user):
        """Testa listagem de comentários."""
        post = Post.objects.create(author=user, content="Post")
        Comment.objects.create(user=user, post=post, content="Comment 1")
        Comment.objects.create(user=user, post=post, content="Comment 2")

        url = reverse("comment-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_create_comment_authenticated(self, authenticated_client, user):
        """Testa criação de comentário autenticado."""
        post = Post.objects.create(author=user, content="Post")

        url = reverse("comment-list")
        response = authenticated_client.post(
            url, {"post": post.id, "content": "New comment"}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(content="New comment", user=user).exists()

    def test_create_comment_unauthenticated(self, api_client, user):
        """Testa criação de comentário sem autenticação."""
        post = Post.objects.create(author=user, content="Post")

        url = reverse("comment-list")
        response = api_client.post(
            url, {"post": post.id, "content": "New comment"}, format="json"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_own_comment(self, authenticated_client, user):
        """Testa atualização do próprio comentário."""
        post = Post.objects.create(author=user, content="Post")
        comment = Comment.objects.create(user=user, post=post, content="Original")

        url = reverse("comment-detail", kwargs={"pk": comment.pk})
        response = authenticated_client.patch(
            url, {"content": "Updated"}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.content == "Updated"

    def test_cannot_update_others_comment(
        self, authenticated_client, user, another_user
    ):
        """Testa que não pode atualizar comentário de outro."""
        post = Post.objects.create(author=user, content="Post")
        comment = Comment.objects.create(
            user=another_user, post=post, content="Original"
        )

        url = reverse("comment-detail", kwargs={"pk": comment.pk})
        response = authenticated_client.patch(
            url, {"content": "Updated"}, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_comment(self, authenticated_client, user):
        """Testa deletar próprio comentário."""
        post = Post.objects.create(author=user, content="Post")
        comment = Comment.objects.create(user=user, post=post, content="To delete")

        url = reverse("comment-detail", kwargs={"pk": comment.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(pk=comment.pk).exists()
