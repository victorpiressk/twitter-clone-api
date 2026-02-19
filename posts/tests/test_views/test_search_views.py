from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework import status

from posts.models import Hashtag, Post

User = get_user_model()


@pytest.mark.django_db
class TestSearchViewSet:
    """Testes para SearchViewSet."""

    def test_search_posts_by_content(self, api_client, user):
        """Testa busca de posts por conteúdo."""
        Post.objects.create(author=user, content="Python é incrível")
        Post.objects.create(author=user, content="Django framework")
        Post.objects.create(author=user, content="JavaScript também é legal")

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) == 1
        assert "Python" in response.data["posts"][0]["content"]

    def test_search_posts_by_hashtag(self, api_client, user):
        """Testa busca de posts por hashtag."""
        hashtag = Hashtag.objects.create(name="python")
        post = Post.objects.create(author=user, content="Post sobre programação")
        post.hashtags.add(hashtag)

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) == 1
        assert response.data["posts"][0]["id"] == post.id

    def test_search_users_by_username(self, api_client, user):
        """Testa busca de usuários por username."""
        User.objects.create_user(username="python_dev", password="pass")
        User.objects.create_user(username="django_master", password="pass")
        User.objects.create_user(username="javascript_guru", password="pass")

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["users"]) == 1
        assert response.data["users"][0]["username"] == "python_dev"

    def test_search_users_by_bio(self, api_client, user):
        """Testa busca de usuários por bio."""
        user1 = User.objects.create_user(username="alice", password="pass")
        user1.bio = "Python developer"
        user1.save()

        user2 = User.objects.create_user(username="bob", password="pass")
        user2.bio = "JavaScript expert"
        user2.save()

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["users"]) == 1
        assert response.data["users"][0]["username"] == "alice"

    def test_search_hashtags(self, api_client):
        """Testa busca de hashtags."""
        Hashtag.objects.create(name="python", posts_count=100)
        Hashtag.objects.create(name="pytorch", posts_count=50)
        Hashtag.objects.create(name="django", posts_count=80)

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["hashtags"]) == 1
        assert response.data["hashtags"][0]["name"] == "python"

    def test_search_all_types(self, api_client, user):
        """Testa busca retornando todos os tipos."""
        # Criar post
        Post.objects.create(author=user, content="Tutorial de Python")

        # Criar usuário
        User.objects.create_user(username="python_dev", password="pass")

        # Criar hashtag
        Hashtag.objects.create(name="python", posts_count=50)

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) == 1
        assert len(response.data["users"]) == 1
        assert len(response.data["hashtags"]) == 1

        # Verificar meta
        assert response.data["meta"]["query"] == "python"
        assert response.data["meta"]["total_results"] == 3

    def test_search_without_query(self, api_client):
        """Testa busca sem parâmetro q."""
        url = reverse("search-all")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "obrigatório" in str(response.data["detail"]).lower()

    def test_search_with_short_query(self, api_client):
        """Testa busca com query muito curta."""
        url = reverse("search-all")
        response = api_client.get(url, {"q": "a"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "mínimo 2 caracteres" in str(response.data["detail"]).lower()

    def test_search_case_insensitive(self, api_client, user):
        """Testa que busca é case-insensitive."""
        Post.objects.create(author=user, content="Python Programming")

        url = reverse("search-all")

        # Buscar com lowercase
        response1 = api_client.get(url, {"q": "python"})
        assert len(response1.data["posts"]) == 1

        # Buscar com uppercase
        response2 = api_client.get(url, {"q": "PYTHON"})
        assert len(response2.data["posts"]) == 1

        # Buscar com mixed case
        response3 = api_client.get(url, {"q": "PyThOn"})
        assert len(response3.data["posts"]) == 1

    def test_search_with_limit(self, api_client, user):
        """Testa parâmetro limit."""
        # Criar 10 posts
        for i in range(10):
            Post.objects.create(author=user, content=f"Python tutorial {i}")

        url = reverse("search-all")

        # Buscar com limit=3
        response = api_client.get(url, {"q": "python", "limit": 3})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) == 3

    def test_search_max_limit(self, api_client, user):
        """Testa que limit máximo é 20."""
        # Criar 30 posts
        for i in range(30):
            Post.objects.create(author=user, content=f"Python tutorial {i}")

        url = reverse("search-all")

        # Tentar limit=50 (deve retornar max 20)
        response = api_client.get(url, {"q": "python", "limit": 50})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) <= 20

    def test_search_excludes_scheduled_posts(self, api_client, user):
        """Testa que posts agendados não aparecem na busca."""

        # Post publicado
        Post.objects.create(author=user, content="Python publicado")

        # Post agendado
        future = timezone.now() + timedelta(hours=2)
        Post.objects.create(
            author=user, content="Python agendado", scheduled_for=future
        )

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) == 1
        assert "publicado" in response.data["posts"][0]["content"]

    def test_search_no_results(self, api_client, user):
        """Testa busca sem resultados."""
        Post.objects.create(author=user, content="Django framework")

        url = reverse("search-all")
        response = api_client.get(url, {"q": "termoinexistente"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) == 0
        assert len(response.data["users"]) == 0
        assert len(response.data["hashtags"]) == 0
        assert response.data["meta"]["total_results"] == 0

    def test_search_partial_match(self, api_client, user):
        """Testa busca com match parcial."""
        Post.objects.create(author=user, content="Python programming")
        Post.objects.create(author=user, content="PyTorch deep learning")

        url = reverse("search-all")
        response = api_client.get(url, {"q": "py"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) == 2

    def test_search_ordering(self, api_client, user):
        """Testa ordenação dos resultados."""

        # Posts em ordem cronológica
        post1 = Post.objects.create(author=user, content="Python antigo")
        post1.created_at = timezone.now() - timedelta(days=2)
        post1.save()

        post2 = Post.objects.create(author=user, content="Python recente")

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK

        # Mais recente deve vir primeiro
        assert response.data["posts"][0]["id"] == post2.id
        assert response.data["posts"][1]["id"] == post1.id

    def test_search_unauthenticated(self, api_client, user):
        """Testa que busca funciona para não autenticados."""
        Post.objects.create(author=user, content="Python tutorial")

        url = reverse("search-all")
        response = api_client.get(url, {"q": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["posts"]) == 1
