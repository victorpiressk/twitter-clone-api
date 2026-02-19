from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework import status

from posts.models import Hashtag, Post


@pytest.mark.django_db
class TestHashtagViewSet:
    """Testes para HashtagViewSet."""

    def test_list_hashtags(self, api_client):
        """Testa listagem de hashtags."""
        Hashtag.objects.create(name="python", posts_count=10)
        Hashtag.objects.create(name="django", posts_count=5)

        url = reverse("hashtag-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_hashtags_ordered_by_posts_count(self, api_client):
        """Testa que hashtags são ordenadas por posts_count."""
        Hashtag.objects.create(name="python", posts_count=10)
        Hashtag.objects.create(name="django", posts_count=25)
        Hashtag.objects.create(name="javascript", posts_count=5)

        url = reverse("hashtag-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Primeira deve ser 'django' (mais posts)
        assert response.data["results"][0]["name"] == "django"
        assert response.data["results"][1]["name"] == "python"
        assert response.data["results"][2]["name"] == "javascript"

    def test_retrieve_hashtag(self, api_client):
        """Testa obter detalhes de uma hashtag."""
        hashtag = Hashtag.objects.create(name="python", posts_count=10)

        url = reverse("hashtag-detail", kwargs={"pk": hashtag.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "python"
        assert response.data["posts_count"] == 10

    def test_hashtag_posts_endpoint(self, api_client, user):
        """Testa endpoint de posts por hashtag."""
        hashtag = Hashtag.objects.create(name="python")

        post1 = Post.objects.create(author=user, content="Post 1 #python")
        post2 = Post.objects.create(author=user, content="Post 2 #python")

        post1.hashtags.add(hashtag)
        post2.hashtags.add(hashtag)

        url = reverse("hashtag-posts", kwargs={"pk": hashtag.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_hashtag_posts_excludes_scheduled(self, api_client, user):
        """Testa que posts agendados não aparecem."""

        hashtag = Hashtag.objects.create(name="python")

        # Post publicado
        post1 = Post.objects.create(author=user, content="Post 1")
        post1.hashtags.add(hashtag)

        # Post agendado
        future = timezone.now() + timedelta(hours=2)
        post2 = Post.objects.create(author=user, content="Post 2", scheduled_for=future)
        post2.hashtags.add(hashtag)

        url = reverse("hashtag-posts", kwargs={"pk": hashtag.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # Apenas post1

    def test_hashtag_posts_limit_parameter(self, api_client, user):
        """Testa parâmetro limit."""
        hashtag = Hashtag.objects.create(name="python")

        # Criar 10 posts
        for i in range(10):
            post = Post.objects.create(author=user, content=f"Post {i}")
            post.hashtags.add(hashtag)

        url = reverse("hashtag-posts", kwargs={"pk": hashtag.pk})
        response = api_client.get(url, {"limit": 5})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_trending_hashtags(self, api_client):
        """Testa endpoint de trending hashtags."""
        Hashtag.objects.create(name="python", posts_count=100)
        Hashtag.objects.create(name="javascript", posts_count=50)
        Hashtag.objects.create(name="django", posts_count=25)

        url = reverse("hashtag-trending")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verificar estrutura do response
        assert "meta" in response.data
        assert "results" in response.data

        # Verificar metadados
        assert response.data["meta"]["period"] == "all"
        assert response.data["meta"]["total"] == 3

        # Deve estar ordenado por posts_count
        results = response.data["results"]
        assert results[0]["name"] == "python"
        assert results[1]["name"] == "javascript"
        assert results[2]["name"] == "django"

    def test_trending_hashtags_limit(self, api_client):
        """Testa limite de trending hashtags."""
        for i in range(20):
            Hashtag.objects.create(name=f"tag{i}", posts_count=i)

        url = reverse("hashtag-trending")
        response = api_client.get(url, {"limit": 5})

        assert response.status_code == status.HTTP_200_OK

        # Verificar estrutura
        assert "meta" in response.data
        assert "results" in response.data

        # Verificar limite
        assert response.data["meta"]["limit"] == 5
        assert len(response.data["results"]) == 5

    def test_search_hashtags(self, api_client):
        """Testa busca de hashtags."""
        Hashtag.objects.create(name="python", posts_count=10)
        Hashtag.objects.create(name="pytorch", posts_count=5)
        Hashtag.objects.create(name="django", posts_count=8)

        url = reverse("hashtag-search")
        response = api_client.get(url, {"q": "py"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        names = [h["name"] for h in response.data]
        assert "python" in names
        assert "pytorch" in names

    def test_search_hashtags_without_query(self, api_client):
        """Testa busca sem parâmetro q."""
        url = reverse("hashtag-search")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "obrigatório" in str(response.data["detail"]).lower()

    def test_search_hashtags_case_insensitive(self, api_client):
        """Testa que busca é case-insensitive."""
        Hashtag.objects.create(name="python")

        url = reverse("hashtag-search")
        response = api_client.get(url, {"q": "PYTHON"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "python"


@pytest.mark.django_db
class TestPostViewSetWithHashtags:
    """Testes para PostViewSet com hashtags."""

    def test_create_post_with_hashtags_via_api(self, authenticated_client, user):
        """Testa criar post com hashtags via API."""
        url = reverse("post-list")

        data = {"content": "Adorei #python e #django!"}
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verificar que hashtags foram extraídas
        assert "hashtags" in response.data
        assert len(response.data["hashtags"]) == 2

        hashtag_names = [h["name"] for h in response.data["hashtags"]]
        assert "python" in hashtag_names
        assert "django" in hashtag_names

    def test_get_post_includes_hashtags(self, api_client, user):
        """Testa que GET /posts/{id}/ inclui hashtags."""
        post = Post.objects.create(author=user, content="Test #python")
        tag = Hashtag.objects.create(name="python")
        post.hashtags.add(tag)

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "hashtags" in response.data
        assert len(response.data["hashtags"]) == 1

    def test_list_posts_includes_hashtags(self, api_client, user):
        """Testa que GET /posts/ inclui hashtags."""
        post = Post.objects.create(author=user, content="Test #python")
        tag = Hashtag.objects.create(name="python")
        post.hashtags.add(tag)

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        post_data = response.data["results"][0]
        assert "hashtags" in post_data


@pytest.mark.django_db
class TestTrendsEnhancements:
    """Testes para melhorias no trending."""

    def test_trending_returns_metadata(self, api_client):
        """Testa que trending retorna metadados."""
        Hashtag.objects.create(name="python", posts_count=10)

        url = reverse("hashtag-trending")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verificar estrutura meta
        meta = response.data["meta"]
        assert "period" in meta
        assert "limit" in meta
        assert "total" in meta
        assert "generated_at" in meta

    def test_trending_with_recent_posts_count(self, api_client, user):
        """Testa que trending com período retorna recent_posts_count."""

        hashtag = Hashtag.objects.create(name="python", posts_count=100)

        # Criar post recente
        recent_post = Post.objects.create(author=user, content="#python")
        recent_post.hashtags.add(hashtag)

        url = reverse("hashtag-trending")
        response = api_client.get(url, {"period": "week"})

        assert response.status_code == status.HTTP_200_OK

        # Verificar que recent_posts_count está presente
        results = response.data["results"]
        if len(results) > 0:
            assert "recent_posts_count" in results[0]

    def test_trending_period_filters(self, api_client):
        """Testa diferentes períodos de trending."""
        Hashtag.objects.create(name="python", posts_count=10)

        url = reverse("hashtag-trending")

        # Testar cada período
        for period in ["all", "today", "week", "month"]:
            response = api_client.get(url, {"period": period})

            assert response.status_code == status.HTTP_200_OK
            assert response.data["meta"]["period"] == period
