"""
Testes para as views do app posts.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from posts.models import Comment, Like, Post

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture para cliente da API."""
    return APIClient()


@pytest.fixture
def user():
    """Fixture com usuário."""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def another_user():
    """Fixture com outro usuário."""
    return User.objects.create_user(
        username="anotheruser", email="another@example.com", password="testpass123"
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Fixture com cliente autenticado."""
    api_client.force_authenticate(user=user)
    return api_client


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
        from users.models import Follow

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

    # TESTES - Retweets

    def test_retweet_post(self, authenticated_client, user, another_user):
        """Testa retweetar um post."""
        post = Post.objects.create(author=another_user, content="Original post")

        url = reverse("post-retweet", kwargs={"pk": post.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(
            author=user,
            is_retweet=True,
            retweet_of=post
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
        Post.objects.create(
            author=user,
            content="",
            is_retweet=True,
            retweet_of=post
        )

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
        
        quote_retweet = Post.objects.get(
            author=user,
            is_retweet=True,
            retweet_of=post
        )
        assert quote_retweet.content == "Concordo totalmente!"
        
        post.refresh_from_db()
        assert post.retweets_count == 1

    def test_quote_retweet_empty_content(self, authenticated_client, user, another_user):
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
        Post.objects.create(
            author=user,
            content="",
            is_retweet=True,
            retweet_of=post
        )

        url = reverse("post-unretweet", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(
            author=user,
            is_retweet=True,
            retweet_of=post
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

    def test_unretweet_decrements_counter(self, authenticated_client, user, another_user):
        """Testa que unretweet decrementa contador."""
        post = Post.objects.create(author=another_user, content="Original")
        post.retweets_count = 5
        post.save()

        # Criar retweet
        Post.objects.create(
            author=user,
            content="",
            is_retweet=True,
            retweet_of=post
        )

        url = reverse("post-unretweet", kwargs={"pk": post.pk})
        authenticated_client.delete(url)

        post.refresh_from_db()
        assert post.retweets_count == 4


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
