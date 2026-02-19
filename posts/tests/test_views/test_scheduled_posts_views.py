from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework import status

from posts.models import Post

User = get_user_model()


@pytest.mark.django_db
class TestScheduledPostsViews:
    """Testes para views de posts agendados."""

    def test_create_scheduled_post(self, authenticated_client, user):
        """Testa criação de post agendado."""
        url = reverse("post-list")

        future = timezone.now() + timedelta(hours=2)
        data = {
            "content": "Post agendado para daqui 2 horas",
            "scheduled_for": future.isoformat(),
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["scheduled_for"] is not None
        assert response.data["is_published"] is False

        # Verificar que foi salvo no banco
        post = Post.objects.get(id=response.data["id"])
        assert post.scheduled_for is not None
        assert post.is_published is False

    def test_create_post_without_scheduled_for(self, authenticated_client, user):
        """Testa criação de post normal (sem agendamento)."""
        url = reverse("post-list")

        data = {"content": "Post publicado agora"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["scheduled_for"] is None
        assert response.data["is_published"] is True

    def test_create_scheduled_post_in_past_fails(self, authenticated_client, user):
        """Testa que não pode agendar para o passado."""
        url = reverse("post-list")

        past = timezone.now() - timedelta(hours=1)
        data = {"content": "Post no passado", "scheduled_for": past.isoformat()}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "scheduled_for" in response.data

    def test_list_posts_excludes_scheduled(self, api_client, user):
        """Testa que listagem NÃO inclui posts agendados."""
        # Criar post normal (publicado)
        Post.objects.create(author=user, content="Post publicado")

        # Criar post agendado
        future = timezone.now() + timedelta(hours=2)
        Post.objects.create(author=user, content="Post agendado", scheduled_for=future)

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["content"] == "Post publicado"

    def test_list_posts_includes_past_scheduled(self, api_client, user):
        """Testa que listagem inclui posts com scheduled_for passado."""
        # Post com scheduled_for no passado (já publicado)
        past = timezone.now() - timedelta(hours=1)
        Post.objects.create(author=user, content="Post passado", scheduled_for=past)

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["is_published"] is True

    def test_feed_excludes_scheduled_posts(self, authenticated_client, user):
        """Testa que feed NÃO inclui posts agendados."""
        # Post normal
        Post.objects.create(author=user, content="Post publicado")

        # Post agendado
        future = timezone.now() + timedelta(hours=2)
        Post.objects.create(author=user, content="Post agendado", scheduled_for=future)

        url = reverse("post-feed")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["content"] == "Post publicado"

    def test_scheduled_endpoint_lists_user_scheduled_posts(
        self, authenticated_client, user
    ):
        """Testa endpoint /api/posts/scheduled/ lista posts agendados."""
        # Post normal (não deve aparecer)
        Post.objects.create(author=user, content="Post normal")

        # Posts agendados (devem aparecer)
        future1 = timezone.now() + timedelta(hours=1)
        future2 = timezone.now() + timedelta(hours=2)

        post1 = Post.objects.create(
            author=user, content="Post 1", scheduled_for=future1
        )
        post2 = Post.objects.create(
            author=user, content="Post 2", scheduled_for=future2
        )

        url = reverse("post-scheduled")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        ids = [item["id"] for item in response.data]
        assert post1.id in ids
        assert post2.id in ids

    def test_scheduled_endpoint_only_own_posts(self, authenticated_client, user):
        """Testa que scheduled() retorna apenas posts do usuário."""
        other_user = User.objects.create_user(username="other", password="pass123")

        # Post agendado do usuário autenticado
        future = timezone.now() + timedelta(hours=1)
        my_post = Post.objects.create(
            author=user, content="Meu post", scheduled_for=future
        )

        # Post agendado de outro usuário
        Post.objects.create(
            author=other_user, content="Post do outro", scheduled_for=future
        )

        url = reverse("post-scheduled")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == my_post.id

    def test_scheduled_endpoint_requires_authentication(self, api_client):
        """Testa que scheduled() requer autenticação."""
        url = reverse("post-scheduled")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_scheduled_endpoint_excludes_published_posts(
        self, authenticated_client, user
    ):
        """Testa que scheduled() não inclui posts já publicados."""
        # Post com scheduled_for passado (já publicado)
        past = timezone.now() - timedelta(hours=1)
        Post.objects.create(author=user, content="Post passado", scheduled_for=past)

        # Post agendado futuro
        future = timezone.now() + timedelta(hours=1)
        scheduled_post = Post.objects.create(
            author=user, content="Post futuro", scheduled_for=future
        )

        url = reverse("post-scheduled")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == scheduled_post.id

    def test_scheduled_posts_ordered_by_scheduled_for(self, authenticated_client, user):
        """Testa que posts agendados são ordenados por scheduled_for."""
        future1 = timezone.now() + timedelta(hours=3)
        future2 = timezone.now() + timedelta(hours=1)
        future3 = timezone.now() + timedelta(hours=2)

        Post.objects.create(author=user, content="Post 3h", scheduled_for=future1)
        post2 = Post.objects.create(
            author=user, content="Post 1h", scheduled_for=future2
        )
        Post.objects.create(author=user, content="Post 2h", scheduled_for=future3)

        url = reverse("post-scheduled")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Primeiro deve ser o post com menor scheduled_for (mais próximo)
        assert response.data[0]["id"] == post2.id
        assert response.data[0]["content"] == "Post 1h"

    def test_retrieve_scheduled_post_as_author(self, authenticated_client, user):
        """Testa que autor pode ver detalhes do próprio post agendado."""
        future = timezone.now() + timedelta(hours=1)
        post = Post.objects.create(
            author=user, content="Post agendado", scheduled_for=future
        )

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == post.id
        assert response.data["is_published"] is False

    def test_create_post_with_scheduled_for_and_location(
        self, authenticated_client, user
    ):
        """Testa criar post agendado com localização."""
        url = reverse("post-list")

        future = timezone.now() + timedelta(hours=2)
        data = {
            "content": "Post agendado com local",
            "scheduled_for": future.isoformat(),
            "location": {
                "name": "Paris, França",
                "latitude": "48.8566",
                "longitude": "2.3522",
            },
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["scheduled_for"] is not None
        assert response.data["location"] is not None
        assert response.data["is_published"] is False
