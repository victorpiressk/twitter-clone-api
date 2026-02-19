from django.urls import reverse

import pytest
from rest_framework import status

from posts.models import Like, Post


@pytest.mark.django_db
class TestLikeViewSet:
    """Testes para o LikeViewSet."""

    def test_list_likes(self, api_client, user):
        """Testa listagem de likes."""
        post = Post.objects.create(author=user, content="Post")
        Like.objects.create(user=user, post=post)

        url = reverse("like-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_create_like_authenticated(self, authenticated_client, user):
        """Testa curtir post."""
        post = Post.objects.create(author=user, content="Post")

        url = reverse("like-list")
        response = authenticated_client.post(url, {"post": post.id}, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Like.objects.filter(user=user, post=post).exists()

    def test_create_like_unauthenticated(self, api_client, user):
        """Testa curtir sem autenticação."""
        post = Post.objects.create(author=user, content="Post")

        url = reverse("like-list")
        response = api_client.post(url, {"post": post.id}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_like_twice(self, authenticated_client, user):
        """Testa que não pode curtir o mesmo post duas vezes."""
        post = Post.objects.create(author=user, content="Post")
        Like.objects.create(user=user, post=post)

        url = reverse("like-list")
        response = authenticated_client.post(url, {"post": post.id}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unlike_post(self, authenticated_client, user):
        """Testa descurtir post."""
        post = Post.objects.create(author=user, content="Post")
        like = Like.objects.create(user=user, post=post)

        url = reverse("like-detail", kwargs={"pk": like.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Like.objects.filter(user=user, post=post).exists()

    def test_cannot_unlike_others_like(self, authenticated_client, user, another_user):
        """Testa que não pode desfazer curtida de outro usuário."""
        post = Post.objects.create(author=user, content="Post")
        like = Like.objects.create(user=another_user, post=post)

        url = reverse("like-detail", kwargs={"pk": like.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Like.objects.filter(user=another_user, post=post).exists()
