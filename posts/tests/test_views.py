"""
Testes para as views do app posts.
"""

from datetime import timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

import pytest
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from posts.models import (
    Comment,
    Hashtag,
    Like,
    Location,
    Poll,
    PollOption,
    PollVote,
    Post,
)

User = get_user_model()


# Helpers para criar arquivos de teste
def create_test_image(name="test.jpg", size=(100, 100), format="JPEG"):
    """
    Helper para criar imagem de teste.

    Args:
        name: Nome do arquivo
        size: Tupla (width, height)
        format: Formato da imagem (JPEG, PNG, GIF)

    Returns:
        SimpleUploadedFile com imagem
    """
    file = BytesIO()
    image = Image.new("RGB", size, color="red")
    image.save(file, format)
    file.seek(0)

    content_type_map = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "GIF": "image/gif",
    }

    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type=content_type_map.get(format, "image/jpeg"),
    )


def create_test_video(name="test.mp4", size_mb=1):
    """
    Helper para criar vídeo de teste.

    Args:
        name: Nome do arquivo
        size_mb: Tamanho em MB

    Returns:
        SimpleUploadedFile com vídeo fake
    """
    # Criar arquivo fake de vídeo com tamanho específico
    size_bytes = size_mb * 1024 * 1024
    content = b"0" * size_bytes

    return SimpleUploadedFile(name=name, content=content, content_type="video/mp4")


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


@pytest.mark.django_db
class TestPostRepliesActions:
    """Testes para actions de replies do PostViewSet."""

    def test_create_reply(self, authenticated_client, user, another_user):
        """Testa criar reply de um post."""
        original = Post.objects.create(author=another_user, content="Original post")

        url = reverse("post-list")
        response = authenticated_client.post(
            url,
            {"content": "This is a reply", "in_reply_to": original.id},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        reply = Post.objects.get(author=user, in_reply_to=original)
        assert reply.content == "This is a reply"

    def test_get_replies_of_post(self, api_client, user):
        """Testa buscar replies de um post."""
        original = Post.objects.create(author=user, content="Original")

        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        reply1 = Post.objects.create(
            author=user2, content="Reply 1", in_reply_to=original
        )
        reply2 = Post.objects.create(
            author=user3, content="Reply 2", in_reply_to=original
        )

        url = reverse("post-replies", kwargs={"pk": original.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        reply_ids = [r["id"] for r in response.data]
        assert reply1.id in reply_ids
        assert reply2.id in reply_ids

    def test_get_thread(self, api_client):
        """Testa buscar thread completa."""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        # Criar thread: A -> B -> C
        post_a = Post.objects.create(author=user1, content="Post A")
        post_b = Post.objects.create(
            author=user2, content="Reply to A", in_reply_to=post_a
        )
        post_c = Post.objects.create(
            author=user3, content="Reply to B", in_reply_to=post_b
        )

        # Buscar thread a partir do post C
        url = reverse("post-thread", kwargs={"pk": post_c.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

        # Verifica ordem: A, B, C
        assert response.data[0]["id"] == post_a.id
        assert response.data[1]["id"] == post_b.id
        assert response.data[2]["id"] == post_c.id

    def test_get_thread_single_post(self, api_client, user):
        """Testa thread de post sem ancestrais."""
        post = Post.objects.create(author=user, content="Single post")

        url = reverse("post-thread", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == post.id

    def test_replies_empty(self, api_client, user):
        """Testa que post sem replies retorna lista vazia."""
        post = Post.objects.create(author=user, content="No replies")

        url = reverse("post-replies", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_reply_to_reply(self, authenticated_client, user, another_user):
        """Testa criar reply de um reply."""
        post_a = Post.objects.create(author=another_user, content="Post A")
        post_b = Post.objects.create(
            author=another_user, content="Reply to A", in_reply_to=post_a
        )

        url = reverse("post-list")
        response = authenticated_client.post(
            url, {"content": "Reply to B", "in_reply_to": post_b.id}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED

        reply = Post.objects.get(author=user, content="Reply to B")
        assert reply.in_reply_to == post_b


@pytest.mark.django_db
class TestPostMediaUpload:
    """Testes para upload de múltiplas mídias - MÚLTIPLAS MÍDIAS."""

    def test_upload_single_image(self, authenticated_client, user):
        """Testa upload de 1 imagem."""

        url = reverse("post-list")

        image = create_test_image("test1.jpg")

        response = authenticated_client.post(
            url,
            {
                "content": "Post with 1 image",
                "media_files": [image],
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.media.count() == 1
        assert post.media.first().type == "image"

    def test_upload_multiple_images(self, authenticated_client, user):
        """Testa upload de múltiplas imagens (2-3)."""

        url = reverse("post-list")

        images = [
            create_test_image("img1.jpg"),
            create_test_image("img2.jpg"),
            create_test_image("img3.jpg"),
        ]

        response = authenticated_client.post(
            url,
            {
                "content": "Post with 3 images",
                "media_files": images,
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.media.count() == 3

        # Verificar ordem
        media_list = list(post.media.all())
        assert media_list[0].order == 0
        assert media_list[1].order == 1
        assert media_list[2].order == 2

    def test_upload_4_images_max(self, authenticated_client, user):
        """✅ ROADMAP 1/4: Upload de exatamente 4 imagens (limite máximo)."""

        url = reverse("post-list")

        images = [
            create_test_image("img1.jpg"),
            create_test_image("img2.jpg"),
            create_test_image("img3.jpg"),
            create_test_image("img4.jpg"),
        ]

        response = authenticated_client.post(
            url,
            {
                "content": "Post with 4 images (max)",
                "media_files": images,
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.media.count() == 4

    def test_upload_more_than_4_images_fails(self, authenticated_client, user):
        """✅ ROADMAP 2/4: Upload de mais de 4 imagens retorna erro 400."""
        url = reverse("post-list")

        images = [create_test_image(f"img{i}.jpg") for i in range(5)]  # 5 imagens

        response = authenticated_client.post(
            url,
            {
                "content": "Post with too many images",
                "media_files": images,
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "media_files" in response.data
        assert "4" in str(response.data["media_files"][0])

    def test_upload_mixed_media_types(self, authenticated_client, user):
        """Testa upload de tipos mistos (JPEG + GIF + PNG)."""

        url = reverse("post-list")

        files = [
            create_test_image("img1.jpg", format="JPEG"),
            create_test_image("img2.gif", format="GIF"),
            create_test_image("img3.png", format="PNG"),
        ]

        response = authenticated_client.post(
            url,
            {
                "content": "Mixed media types",
                "media_files": files,
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.media.count() == 3

        media_types = [m.type for m in post.media.all()]
        assert "image" in media_types
        assert "gif" in media_types

    def test_image_too_large_fails(self, authenticated_client, user):
        """✅ ROADMAP 4/4: Imagem maior que 5MB retorna erro 400."""
        url = reverse("post-list")

        # Criar imagem muito grande (simular 6MB)
        large_content = b"0" * (6 * 1024 * 1024)  # 6MB
        large_image = SimpleUploadedFile(
            name="large.jpg", content=large_content, content_type="image/jpeg"
        )

        response = authenticated_client.post(
            url,
            {
                "content": "Post with large image",
                "media_files": [large_image],
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "media_files" in response.data
        assert "5MB" in str(response.data["media_files"][0])

    def test_video_within_limit_succeeds(self, authenticated_client, user):
        """Testa vídeo dentro do limite (50MB)."""

        url = reverse("post-list")

        video = create_test_video("video.mp4", size_mb=10)  # 10MB (ok)

        response = authenticated_client.post(
            url,
            {
                "content": "Post with video",
                "media_files": [video],
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.media.count() == 1
        assert post.media.first().type == "video"

    def test_video_too_large_fails(self, authenticated_client, user):
        """✅ ROADMAP 4/4: Vídeo maior que 50MB retorna erro 400."""
        url = reverse("post-list")

        large_video = create_test_video("large.mp4", size_mb=60)  # 60MB

        response = authenticated_client.post(
            url,
            {
                "content": "Post with large video",
                "media_files": [large_video],
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "media_files" in response.data
        assert "50MB" in str(response.data["media_files"][0])

    def test_unsupported_file_type_fails(self, authenticated_client, user):
        """Testa arquivo não suportado retorna erro."""
        url = reverse("post-list")

        # Arquivo .txt (não suportado)
        txt_file = SimpleUploadedFile(
            name="document.txt", content=b"Hello world", content_type="text/plain"
        )

        response = authenticated_client.post(
            url,
            {
                "content": "Post with txt file",
                "media_files": [txt_file],
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "media_files" in response.data
        assert "suportado" in str(response.data["media_files"][0]).lower()

    def test_list_posts_includes_media(self, api_client, user):
        """Testa que listagem de posts inclui mídias."""
        from posts.models import PostMedia

        post = Post.objects.create(author=user, content="Post with media")

        PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img1.jpg"), order=0
        )
        PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img2.jpg"), order=1
        )

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        post_data = response.data["results"][0]
        assert "media" in post_data
        assert len(post_data["media"]) == 2

    def test_retrieve_post_includes_media(self, api_client, user):
        """Testa que detalhes do post incluem mídias."""
        from posts.models import PostMedia

        post = Post.objects.create(author=user, content="Post with media")

        PostMedia.objects.create(
            post=post, type="video", file=create_test_video(), order=0
        )

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "media" in response.data
        assert len(response.data["media"]) == 1
        assert response.data["media"][0]["type"] == "video"

    def test_feed_includes_media(self, authenticated_client, user):
        """Testa que feed inclui mídias dos posts."""
        from posts.models import PostMedia

        post = Post.objects.create(author=user, content="Post in feed")

        PostMedia.objects.create(
            post=post, type="image", file=create_test_image(), order=0
        )

        url = reverse("post-feed")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert "media" in response.data[0]

    def test_delete_post_cascades_media(self, authenticated_client, user):
        """Testa que deletar post deleta mídias associadas (CASCADE)."""
        from posts.models import PostMedia

        post = Post.objects.create(author=user, content="Post to delete")

        media1 = PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img1.jpg"), order=0
        )
        media2 = PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img2.jpg"), order=1
        )

        media_ids = [media1.id, media2.id]

        # Deletar post
        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que mídias foram deletadas
        assert not PostMedia.objects.filter(id__in=media_ids).exists()

    def test_create_post_without_media(self, authenticated_client, user):
        """Testa criar post sem mídias (campo opcional)."""
        url = reverse("post-list")

        response = authenticated_client.post(
            url, {"content": "Post without media"}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.media.count() == 0

    def test_backward_compatibility_with_image_field(self, authenticated_client, user):
        """Testa compatibilidade com campo 'image' antigo."""
        url = reverse("post-list")

        image = create_test_image()

        response = authenticated_client.post(
            url,
            {
                "content": "Post with old image field",
                "image": image,
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.image is not None  # Campo antigo ainda funciona

    def test_debug_upload_response(self, authenticated_client, user):
        """Teste temporário para debug."""
        url = reverse("post-list")

        image = create_test_image("test.jpg")

        response = authenticated_client.post(
            url,
            {
                "content": "Test post",
                "media_files": [image],
            },
            format="multipart",
        )

        print(f"\nStatus: {response.status_code}")
        print(f"Data: {response.data}\n")

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestPollViewSet:
    """Testes para o PollViewSet."""

    def test_list_polls(self, api_client, user):
        """Testa listagem de polls."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        PollOption.objects.create(poll=poll, text="Opt 1", order=0)
        PollOption.objects.create(poll=poll, text="Opt 2", order=1)

        url = reverse("poll-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_retrieve_poll(self, api_client, user):
        """Testa obter detalhes de uma poll."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(
            post=post, question="Test question", duration_hours=24
        )
        PollOption.objects.create(poll=poll, text="Python", order=0)
        PollOption.objects.create(poll=poll, text="JavaScript", order=1)

        url = reverse("poll-detail", kwargs={"pk": poll.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["question"] == "Test question"
        assert len(response.data["options"]) == 2

    def test_vote_in_poll(self, authenticated_client, user):
        """Testa votar em uma poll."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})
        response = authenticated_client.post(url, {"option_id": option.id})

        assert response.status_code == status.HTTP_200_OK

        # Verificar que voto foi registrado
        assert PollVote.objects.filter(poll=poll, user=user, option=option).exists()

        # Verificar que contador foi incrementado
        option.refresh_from_db()
        assert option.votes == 1

        # Verificar resposta contém user_voted_option_id
        assert response.data["user_voted_option_id"] == option.id

    def test_vote_unauthenticated(self, api_client, user):
        """Testa votar sem autenticação."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})
        response = api_client.post(url, {"option_id": option.id})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_vote_twice_fails(self, authenticated_client, user):
        """Testa que não pode votar duas vezes."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        opt1 = PollOption.objects.create(poll=poll, text="Opt 1", order=0)
        opt2 = PollOption.objects.create(poll=poll, text="Opt 2", order=1)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})

        # Primeiro voto
        response = authenticated_client.post(url, {"option_id": opt1.id})
        assert response.status_code == status.HTTP_200_OK

        # Segundo voto (deve falhar)
        response = authenticated_client.post(url, {"option_id": opt2.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já votou" in str(response.data).lower()

    def test_vote_ended_poll_fails(self, authenticated_client, user):
        """Testa voto em poll encerrada."""
        post = Post.objects.create(author=user, content="Test")

        # Poll que terminou ontem
        past_time = timezone.now() - timedelta(hours=24)
        poll = Poll.objects.create(post=post, duration_hours=1, ends_at=past_time)
        option = PollOption.objects.create(poll=poll, text="Opt", order=0)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})
        response = authenticated_client.post(url, {"option_id": option.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "encerrada" in str(response.data).lower()

    def test_vote_invalid_option(self, authenticated_client, user):
        """Testa voto com option_id inválido."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})
        response = authenticated_client.post(url, {"option_id": 99999})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_poll_results(self, api_client, user):
        """Testa obter resultados de uma poll."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        PollOption.objects.create(poll=poll, text="Opt 1", votes=30, order=0)
        PollOption.objects.create(poll=poll, text="Opt 2", votes=70, order=1)

        url = reverse("poll-results", kwargs={"pk": poll.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_votes"] == 100
        assert len(response.data["options"]) == 2
        assert response.data["options"][0]["percentage"] == 30.0
        assert response.data["options"][1]["percentage"] == 70.0

    def test_unvote_poll(self, authenticated_client, user):
        """Testa desfazer voto."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", votes=5, order=0)

        # Criar voto
        PollVote.objects.create(poll=poll, user=user, option=option)

        url = reverse("poll-unvote", kwargs={"pk": poll.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que voto foi deletado
        assert not PollVote.objects.filter(poll=poll, user=user).exists()

        # Verificar que contador foi decrementado
        option.refresh_from_db()
        assert option.votes == 4

    def test_unvote_not_voted(self, authenticated_client, user):
        """Testa desfazer voto quando não votou."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        url = reverse("poll-unvote", kwargs={"pk": poll.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "não votou" in str(response.data).lower()

    def test_unvote_ended_poll_fails(self, authenticated_client, user):
        """Testa que não pode desfazer voto em poll encerrada."""
        post = Post.objects.create(author=user, content="Test")

        past_time = timezone.now() - timedelta(hours=24)
        poll = Poll.objects.create(post=post, duration_hours=1, ends_at=past_time)
        option = PollOption.objects.create(poll=poll, text="Opt", order=0)

        # Criar voto
        PollVote.objects.create(poll=poll, user=user, option=option)

        url = reverse("poll-unvote", kwargs={"pk": poll.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "encerrada" in str(response.data).lower()


@pytest.mark.django_db
class TestPostWithPoll:
    """Testes para criação de posts com polls."""

    def test_create_post_with_poll(self, authenticated_client, user):
        """Testa criar post com poll."""
        url = reverse("post-list")

        data = {
            "content": "Qual sua linguagem favorita?",
            "poll": {
                "question": "",
                "duration_hours": 24,
                "options": ["Python", "JavaScript", "Go", "Rust"],
            },
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verificar que post foi criado
        post = Post.objects.get(id=response.data["id"])
        assert post.content == "Qual sua linguagem favorita?"

        # Verificar que poll foi criada
        assert hasattr(post, "poll")
        assert post.poll.duration_hours == 24
        assert post.poll.options.count() == 4

    def test_create_post_with_poll_minimum_options(self, authenticated_client, user):
        """Testa criar poll com mínimo de opções (2)."""
        url = reverse("post-list")

        data = {
            "content": "Concordam?",
            "poll": {"duration_hours": 24, "options": ["Sim", "Não"]},
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.poll.options.count() == 2

    def test_create_post_with_poll_invalid_options(self, authenticated_client, user):
        """Testa criar poll com número inválido de opções."""
        url = reverse("post-list")

        # Menos de 2 opções
        data = {
            "content": "Test",
            "poll": {"duration_hours": 24, "options": ["Única opção"]},
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Mais de 4 opções
        data["poll"]["options"] = ["A", "B", "C", "D", "E"]

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_post_with_poll_duplicate_options(self, authenticated_client, user):
        """Testa criar poll com opções duplicadas."""
        url = reverse("post-list")

        data = {
            "content": "Test",
            "poll": {
                "duration_hours": 24,
                "options": ["Python", "JavaScript", "Python", "Go"],
            },
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "duplicadas" in str(response.data).lower()

    def test_create_post_without_poll(self, authenticated_client, user):
        """Testa que post normal ainda funciona."""
        url = reverse("post-list")

        data = {"content": "Post sem poll"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert not hasattr(post, "poll")

    def test_get_post_with_poll(self, api_client, user):
        """Testa que GET /posts/ retorna poll."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        PollOption.objects.create(poll=poll, text="Opt 1", order=0)
        PollOption.objects.create(poll=poll, text="Opt 2", order=1)

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "poll" in response.data
        assert response.data["poll"] is not None
        assert len(response.data["poll"]["options"]) == 2

    def test_list_posts_includes_polls(self, api_client, user):
        """Testa que listagem de posts inclui polls."""
        post = Post.objects.create(author=user, content="Test with poll")
        poll = Poll.objects.create(post=post, duration_hours=24)
        PollOption.objects.create(poll=poll, text="Opt", order=0)

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        post_data = response.data["results"][0]
        assert "poll" in post_data
        assert post_data["poll"] is not None

    def test_delete_post_cascades_poll(self, authenticated_client, user):
        """Testa que deletar post deleta poll associada."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        poll_id = poll.id

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Poll deve ter sido deletada
        assert not Poll.objects.filter(id=poll_id).exists()


@pytest.mark.django_db
class TestLocationViewSet:
    """Testes para o LocationViewSet."""

    def test_list_locations(self, api_client):
        """Testa listagem de locations."""
        Location.objects.create(
            name="Paris, França", latitude=48.8566, longitude=2.3522
        )
        Location.objects.create(
            name="Londres, Reino Unido", latitude=51.5074, longitude=-0.1278
        )

        url = reverse("location-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_retrieve_location(self, api_client):
        """Testa obter detalhes de uma location."""
        location = Location.objects.create(
            name="Torre Eiffel, Paris",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )

        url = reverse("location-detail", kwargs={"pk": location.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Torre Eiffel, Paris"
        assert response.data["has_coordinates"] is True

    def test_search_locations(self, api_client):
        """Testa busca de locations por nome."""
        Location.objects.create(name="Paris, França")
        Location.objects.create(name="Parque Ibirapuera, São Paulo")
        Location.objects.create(name="Londres, Reino Unido")

        url = reverse("location-search")
        response = api_client.get(url, {"q": "par"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Paris e Parque

        # Verificar que Londres não está nos resultados
        names = [loc["name"] for loc in response.data]
        assert "Paris, França" in names
        assert "Parque Ibirapuera, São Paulo" in names
        assert "Londres, Reino Unido" not in names

    def test_search_locations_case_insensitive(self, api_client):
        """Testa busca case-insensitive."""
        Location.objects.create(name="Paris, França")

        url = reverse("location-search")
        response = api_client.get(url, {"q": "PARIS"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Paris, França"

    def test_search_locations_without_query(self, api_client):
        """Testa busca sem parâmetro q."""
        url = reverse("location-search")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "obrigatório" in str(response.data["detail"]).lower()

    def test_search_locations_limit_results(self, api_client):
        """Testa que busca limita a 10 resultados."""
        # Criar 15 locations com "City" no nome
        for i in range(15):
            Location.objects.create(name=f"City {i}")

        url = reverse("location-search")
        response = api_client.get(url, {"q": "City"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10  # Máximo 10

    def test_nearby_locations(self, api_client):
        """Testa busca de locations próximas."""
        # Torre Eiffel
        Location.objects.create(
            name="Torre Eiffel",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )
        # Louvre (próximo)
        Location.objects.create(
            name="Museu do Louvre",
            latitude=Decimal("48.860611"),
            longitude=Decimal("2.337644"),
        )
        # Londres (longe)
        Location.objects.create(
            name="Big Ben", latitude=Decimal("51.5007"), longitude=Decimal("-0.1246")
        )

        url = reverse("location-nearby")
        response = api_client.get(
            url, {"lat": "48.858844", "lng": "2.294351", "radius": "10"}  # 10 km
        )

        assert response.status_code == status.HTTP_200_OK

        # Torre Eiffel e Louvre devem estar nos resultados
        names = [loc["name"] for loc in response.data]
        assert "Torre Eiffel" in names
        assert "Museu do Louvre" in names
        # Big Ben não deve estar (muito longe)
        assert "Big Ben" not in names

    def test_nearby_locations_without_parameters(self, api_client):
        """Testa nearby sem parâmetros lat/lng."""
        url = reverse("location-nearby")

        # Sem parâmetros (usa 0,0 como padrão - comportamento válido)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Parâmetros inválidos (texto ao invés de número)
        response = api_client.get(url, {"lat": "abc", "lng": "xyz"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_nearby_locations_invalid_coordinates(self, api_client):
        """Testa nearby com coordenadas inválidas."""
        url = reverse("location-nearby")

        # Latitude inválida
        response = api_client.get(url, {"lat": "95.0", "lng": "10.0"})  # > 90
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Longitude inválida
        response = api_client.get(url, {"lat": "10.0", "lng": "185.0"})  # > 180
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_nearby_only_returns_locations_with_coordinates(self, api_client):
        """Testa que nearby só retorna locations com coordenadas."""
        Location.objects.create(
            name="Com coordenadas",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )
        Location.objects.create(name="Sem coordenadas")

        url = reverse("location-nearby")
        response = api_client.get(
            url, {"lat": "48.858844", "lng": "2.294351", "radius": "10"}
        )

        assert response.status_code == status.HTTP_200_OK

        names = [loc["name"] for loc in response.data]
        assert "Com coordenadas" in names
        assert "Sem coordenadas" not in names


@pytest.mark.django_db
class TestPostWithLocation:
    """Testes para posts com locations."""

    def test_create_post_with_location(self, authenticated_client, user):
        """Testa criar post com location."""
        url = reverse("post-list")

        data = {
            "content": "Visitando Paris!",
            "location": {
                "name": "Torre Eiffel, Paris",
                "latitude": "48.858844",
                "longitude": "2.294351",
            },
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verificar que post foi criado
        post = Post.objects.get(id=response.data["id"])
        assert post.content == "Visitando Paris!"

        # Verificar que location foi criada e associada
        assert post.location is not None
        assert post.location.name == "Torre Eiffel, Paris"
        assert post.location.latitude == Decimal("48.858844")

    def test_create_post_with_location_without_coordinates(
        self, authenticated_client, user
    ):
        """Testa criar post com location sem coordenadas."""
        url = reverse("post-list")

        data = {"content": "Visitando o Brasil!", "location": {"name": "Brasil"}}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.location is not None
        assert post.location.name == "Brasil"
        assert post.location.has_coordinates is False

    def test_create_post_without_location(self, authenticated_client, user):
        """Testa criar post sem location (campo opcional)."""
        url = reverse("post-list")

        data = {"content": "Post sem localização"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.location is None

    def test_create_post_reuses_existing_location(self, authenticated_client, user):
        """Testa que location existente é reutilizada."""
        # Criar location previamente
        existing_location = Location.objects.create(
            name="Paris", latitude=Decimal("48.858844"), longitude=Decimal("2.294351")
        )

        url = reverse("post-list")

        # Criar post com mesmas coordenadas
        data = {
            "content": "Post 1",
            "location": {
                "name": "Torre Eiffel",  # Nome diferente
                "latitude": "48.858844",
                "longitude": "2.294351",
            },
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])

        # Deve usar location existente
        assert post.location.id == existing_location.id
        assert post.location.name == "Paris"  # Nome original mantido

        # Verificar que não criou location duplicada
        assert Location.objects.count() == 1

    def test_get_post_includes_location(self, api_client, user):
        """Testa que GET /posts/{id}/ inclui location."""
        location = Location.objects.create(
            name="São Paulo, Brasil",
            latitude=Decimal("-23.550520"),
            longitude=Decimal("-46.633308"),
        )

        post = Post.objects.create(
            author=user, content="Visitando SP!", location=location
        )

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "location" in response.data
        assert response.data["location"] is not None
        assert response.data["location"]["name"] == "São Paulo, Brasil"
        assert response.data["location"]["has_coordinates"] is True

    def test_list_posts_includes_locations(self, api_client, user):
        """Testa que GET /posts/ inclui locations."""
        location = Location.objects.create(name="Paris")

        Post.objects.create(author=user, content="Post com location", location=location)

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        post_data = response.data["results"][0]
        assert "location" in post_data
        assert post_data["location"]["name"] == "Paris"

    def test_create_post_with_invalid_location_coordinates(
        self, authenticated_client, user
    ):
        """Testa criar post com coordenadas inválidas."""
        url = reverse("post-list")

        # Latitude inválida
        data = {
            "content": "Test",
            "location": {"name": "Local", "latitude": "95.0", "longitude": "10.0"},
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_post_with_incomplete_coordinates(self, authenticated_client, user):
        """Testa criar post com coordenadas incompletas."""
        url = reverse("post-list")

        # Só latitude
        data = {"content": "Test", "location": {"name": "Local", "latitude": "10.0"}}

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "juntas" in str(response.data).lower()


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
        from datetime import timedelta

        from django.utils import timezone

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
        from datetime import timedelta

        from django.utils import timezone

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

        # Deve estar ordenado por posts_count
        assert response.data[0]["name"] == "python"
        assert response.data[1]["name"] == "javascript"
        assert response.data[2]["name"] == "django"

    def test_trending_hashtags_limit(self, api_client):
        """Testa limite de trending hashtags."""
        for i in range(20):
            Hashtag.objects.create(name=f"tag{i}", posts_count=i)

        url = reverse("hashtag-trending")
        response = api_client.get(url, {"limit": 5})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

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
