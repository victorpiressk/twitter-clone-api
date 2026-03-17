from django.urls import reverse

import pytest
from rest_framework import status

from posts.models import Post


@pytest.mark.django_db
class TestRetweetViewSet:
    """Testes para actions de retweets."""

    def test_retweet_post(self, authenticated_client, user, another_user):
        """Testa retweetar um post."""
        post = Post.objects.create(author=another_user, content="Original post")

        url = reverse("post-retweet", kwargs={"pk": post.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(
            author=user, is_retweet=True, retweet_of=post
        ).exists()

        post.refresh_from_db()
        assert post.retweets_count == 1

    def test_retweet_unauthenticated(self, api_client, user):
        """Testa retweetar sem autenticação."""
        post = Post.objects.create(author=user, content="Test")

        url = reverse("post-retweet", kwargs={"pk": post.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_retweet_twice(self, authenticated_client, user, another_user):
        """Testa que não pode retweetar o mesmo post duas vezes."""
        post = Post.objects.create(author=another_user, content="Original")

        # Primeiro retweet
        Post.objects.create(author=user, content="", is_retweet=True, retweet_of=post)

        # Tentar retweetar novamente
        url = reverse("post-retweet", kwargs={"pk": post.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já retweetou" in response.data["detail"].lower()

    def test_quote_retweet(self, authenticated_client, user, another_user):
        """Testa quote retweet (retweet com comentário)."""
        post = Post.objects.create(author=another_user, content="Original")

        url = reverse("post-quote-retweet", kwargs={"pk": post.pk})
        response = authenticated_client.post(
            url, {"content": "Concordo totalmente!"}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED

        quote_retweet = Post.objects.get(author=user, is_retweet=True, retweet_of=post)
        assert quote_retweet.content == "Concordo totalmente!"

        post.refresh_from_db()
        assert post.retweets_count == 1

    def test_quote_retweet_empty_content(
        self, authenticated_client, user, another_user
    ):
        """Testa que quote retweet sem comentário retorna erro."""
        post = Post.objects.create(author=another_user, content="Original")

        url = reverse("post-quote-retweet", kwargs={"pk": post.pk})
        response = authenticated_client.post(url, {"content": ""}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "comentário" in response.data["detail"].lower()

    def test_quote_retweet_too_long(self, authenticated_client, user, another_user):
        """Testa que quote retweet com mais de 280 caracteres retorna erro."""
        post = Post.objects.create(author=another_user, content="Original")
        long_content = "a" * 281  # 281 caracteres

        url = reverse("post-quote-retweet", kwargs={"pk": post.pk})
        response = authenticated_client.post(
            url, {"content": long_content}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "280" in response.data["detail"]

    def test_unretweet(self, authenticated_client, user, another_user):
        """Testa desfazer retweet."""
        post = Post.objects.create(author=another_user, content="Original")
        post.retweets_count = 1
        post.save()

        # Criar retweet
        Post.objects.create(author=user, content="", is_retweet=True, retweet_of=post)

        url = reverse("post-unretweet", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(
            author=user, is_retweet=True, retweet_of=post
        ).exists()

        post.refresh_from_db()
        assert post.retweets_count == 0

    def test_unretweet_not_retweeted(self, authenticated_client, user, another_user):
        """Testa desfazer retweet de post que não foi retweetado."""
        post = Post.objects.create(author=another_user, content="Original")

        url = reverse("post-unretweet", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "não retweetou" in response.data["detail"].lower()

    def test_retweet_increments_counter(self, authenticated_client, user, another_user):
        """Testa que retweet incrementa contador."""
        post = Post.objects.create(author=another_user, content="Original")
        assert post.retweets_count == 0

        url = reverse("post-retweet", kwargs={"pk": post.pk})
        authenticated_client.post(url)

        post.refresh_from_db()
        assert post.retweets_count == 1

    def test_unretweet_decrements_counter(
        self, authenticated_client, user, another_user
    ):
        """Testa que unretweet decrementa contador."""
        post = Post.objects.create(author=another_user, content="Original")
        post.retweets_count = 5
        post.save()

        # Criar retweet
        Post.objects.create(author=user, content="", is_retweet=True, retweet_of=post)

        url = reverse("post-unretweet", kwargs={"pk": post.pk})
        authenticated_client.delete(url)

        post.refresh_from_db()
        assert post.retweets_count == 4

    def test_can_simple_retweet_after_quote_retweet(
        self, authenticated_client, user, another_user
    ):
        """Testa que pode fazer retweet simples mesmo após quote retweet."""
        post = Post.objects.create(author=another_user, content="Original")

        # Criar quote retweet primeiro
        Post.objects.create(
            author=user, content="Meu comentário", is_retweet=True, retweet_of=post
        )

        # Retweet simples deve funcionar
        url = reverse("post-retweet", kwargs={"pk": post.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(
            author=user, is_retweet=True, retweet_of=post, content=""
        ).exists()

    def test_cannot_simple_retweet_twice(
        self, authenticated_client, user, another_user
    ):
        """Testa que não pode fazer dois retweets simples do mesmo post."""
        post = Post.objects.create(author=another_user, content="Original")

        # Retweet simples já existe
        Post.objects.create(author=user, content="", is_retweet=True, retweet_of=post)

        url = reverse("post-retweet", kwargs={"pk": post.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_multiple_quotes_same_post(
        self, authenticated_client, user, another_user
    ):
        """Testa que pode fazer múltiplos quote retweets do mesmo post."""
        post = Post.objects.create(author=another_user, content="Original")

        url = reverse("post-quote-retweet", kwargs={"pk": post.pk})

        response1 = authenticated_client.post(
            url, {"content": "Primeiro comentário"}, format="json"
        )
        response2 = authenticated_client.post(
            url, {"content": "Segundo comentário"}, format="json"
        )

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert (
            Post.objects.filter(author=user, is_retweet=True, retweet_of=post).count()
            == 2
        )

    def test_unretweet_only_removes_simple_retweet(
        self, authenticated_client, user, another_user
    ):
        """Testa que unretweet remove apenas o retweet simples, não o quote retweet."""
        post = Post.objects.create(author=another_user, content="Original")
        post.retweets_count = 2
        post.save()

        # Criar quote retweet e retweet simples
        Post.objects.create(
            author=user, content="Meu comentário", is_retweet=True, retweet_of=post
        )
        Post.objects.create(author=user, content="", is_retweet=True, retweet_of=post)

        url = reverse("post-unretweet", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Quote retweet deve permanecer
        assert Post.objects.filter(
            author=user, is_retweet=True, retweet_of=post, content="Meu comentário"
        ).exists()

        # Retweet simples deve ter sido removido
        assert not Post.objects.filter(
            author=user, is_retweet=True, retweet_of=post, content=""
        ).exists()

        post.refresh_from_db()
        assert post.retweets_count == 1
