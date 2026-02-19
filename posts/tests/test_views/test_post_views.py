from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from rest_framework import status

from posts.models import Post
from users.models import Follow

User = get_user_model()


@pytest.mark.django_db
class TestPostViewSet:
    """Testes para o PostViewSet."""

    def test_list_posts(self, api_client, user):
        """Testa listagem de posts (público)."""
        Post.objects.create(author=user, content="Post 1")
        Post.objects.create(author=user, content="Post 2")

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_retrieve_post(self, api_client, user):
        """Testa obter detalhes de post."""
        post = Post.objects.create(author=user, content="Test post")

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["content"] == "Test post"
        assert response.data["author"]["username"] == "testuser"

    def test_create_post_authenticated(self, authenticated_client, user):
        """Testa criação de post autenticado."""
        url = reverse("post-list")
        response = authenticated_client.post(
            url, {"content": "New post"}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(content="New post", author=user).exists()

    def test_create_post_unauthenticated(self, api_client):
        """Testa criação de post sem autenticação."""
        url = reverse("post-list")
        response = api_client.post(url, {"content": "New post"}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_own_post(self, authenticated_client, user):
        """Testa atualização do próprio post."""
        post = Post.objects.create(author=user, content="Original")

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.patch(
            url, {"content": "Updated"}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.content == "Updated"

    def test_cannot_update_others_post(self, authenticated_client, another_user):
        """Testa que não pode atualizar post de outro usuário."""
        post = Post.objects.create(author=another_user, content="Original")

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.patch(
            url, {"content": "Updated"}, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        post.refresh_from_db()
        assert post.content == "Original"

    def test_delete_own_post(self, authenticated_client, user):
        """Testa deletar próprio post."""
        post = Post.objects.create(author=user, content="To delete")

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(pk=post.pk).exists()

    def test_cannot_delete_others_post(self, authenticated_client, another_user):
        """Testa que não pode deletar post de outro usuário."""
        post = Post.objects.create(author=another_user, content="Protected")

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Post.objects.filter(pk=post.pk).exists()

    def test_feed_endpoint_authenticated(
        self, authenticated_client, user, another_user
    ):
        """Testa endpoint de feed."""

        # user segue another_user
        Follow.objects.create(follower=user, following=another_user)

        # Posts de quem user segue
        Post.objects.create(author=another_user, content="Post from followed")
        # Post do próprio user
        Post.objects.create(author=user, content="Own post")
        # Post de alguém que user não segue
        third_user = User.objects.create_user(username="third", password="pass123")
        Post.objects.create(author=third_user, content="Not in feed")

        url = reverse("post-feed")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Apenas posts de quem segue + próprios
