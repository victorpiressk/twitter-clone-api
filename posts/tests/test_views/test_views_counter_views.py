from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework import status

from posts.models import Post


@pytest.mark.django_db
class TestViewsCounterViews:
    """Testes para contador de views nas views."""

    def test_retrieve_post_increments_views(self, api_client, user):
        """Testa que GET /posts/{id}/ incrementa views."""
        post = Post.objects.create(author=user, content="Test post")

        assert post.views_count == 0

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verificar que views foi incrementado
        post.refresh_from_db()
        assert post.views_count == 1

        # Verificar que resposta inclui views
        assert response.data["stats"]["views"] == 1

    def test_retrieve_post_multiple_times_increments_each_time(self, api_client, user):
        """Testa que views incrementa a cada GET."""
        post = Post.objects.create(author=user, content="Test")

        url = reverse("post-detail", kwargs={"pk": post.pk})

        # Primeira visualização
        response = api_client.get(url)
        assert response.data["stats"]["views"] == 1

        # Segunda visualização
        response = api_client.get(url)
        assert response.data["stats"]["views"] == 2

        # Terceira visualização
        response = api_client.get(url)
        assert response.data["stats"]["views"] == 3

    def test_list_posts_does_not_increment_views(self, api_client, user):
        """Testa que GET /posts/ NÃO incrementa views."""
        post = Post.objects.create(author=user, content="Test")

        assert post.views_count == 0

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Views NÃO deve ter incrementado
        post.refresh_from_db()
        assert post.views_count == 0

    def test_create_post_starts_with_zero_views(self, authenticated_client, user):
        """Testa que post novo tem views = 0."""
        url = reverse("post-list")

        data = {"content": "New post"}
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["stats"]["views"] == 0

    def test_trending_endpoint_orders_by_views(self, api_client, user):
        """Testa que /posts/trending/ ordena por views."""
        # Criar posts com diferentes views
        post1 = Post.objects.create(author=user, content="Post 1")
        post2 = Post.objects.create(author=user, content="Post 2")
        post3 = Post.objects.create(author=user, content="Post 3")

        # Dar views diferentes
        for _ in range(5):
            post1.increment_views()
        for _ in range(10):
            post2.increment_views()
        for _ in range(3):
            post3.increment_views()

        # post2 (10 views) > post1 (5 views) > post3 (3 views)

        url = reverse("post-trending")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verificar ordem (mais vistos primeiro)
        assert response.data[0]["id"] == post2.id
        assert response.data[0]["stats"]["views"] == 10

        assert response.data[1]["id"] == post1.id
        assert response.data[1]["stats"]["views"] == 5

        assert response.data[2]["id"] == post3.id
        assert response.data[2]["stats"]["views"] == 3

    def test_trending_endpoint_limit_parameter(self, api_client, user):
        """Testa parâmetro limit em /trending/."""
        # Criar 10 posts
        for i in range(10):
            post = Post.objects.create(author=user, content=f"Post {i}")
            for _ in range(10 - i):
                post.increment_views()

        url = reverse("post-trending")

        # Pedir top 5
        response = api_client.get(url, {"limit": 5})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_trending_endpoint_period_filter(self, api_client, user):
        """Testa filtro de período em /trending/."""
        # Post antigo (2 meses atrás)
        old_post = Post.objects.create(author=user, content="Old post")
        old_post.created_at = timezone.now() - timedelta(days=60)
        old_post.save()
        old_post.increment_views()
        old_post.increment_views()
        old_post.increment_views()

        # Post recente (hoje)
        new_post = Post.objects.create(author=user, content="New post")
        new_post.increment_views()

        url = reverse("post-trending")

        # Trending do mês (não deve incluir old_post)
        response = api_client.get(url, {"period": "month"})

        assert response.status_code == status.HTTP_200_OK

        post_ids = [p["id"] for p in response.data]
        assert new_post.id in post_ids
        assert old_post.id not in post_ids

    def test_trending_endpoint_max_limit(self, api_client, user):
        """Testa que limit máximo é 50."""
        # Criar 60 posts
        for i in range(60):
            Post.objects.create(author=user, content=f"Post {i}")

        url = reverse("post-trending")

        # Pedir 100 (deve retornar max 50)
        response = api_client.get(url, {"limit": 100})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) <= 50

    def test_unauthenticated_can_view_post_increments_views(self, api_client, user):
        """Testa que usuário não autenticado também incrementa views."""
        post = Post.objects.create(author=user, content="Public post")

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        post.refresh_from_db()
        assert post.views_count == 1

    def test_author_viewing_own_post_increments_views(self, authenticated_client, user):
        """Testa que autor vendo próprio post também incrementa views."""
        post = Post.objects.create(author=user, content="My post")

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        post.refresh_from_db()
        assert post.views_count == 1
