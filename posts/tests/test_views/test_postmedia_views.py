from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

import pytest
from PIL import Image
from rest_framework import status

from posts.models import Post, PostMedia


def create_test_image(name="test.jpg", size=(100, 100), format="JPEG"):
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
    size_bytes = size_mb * 1024 * 1024
    content = b"0" * size_bytes
    return SimpleUploadedFile(name=name, content=content, content_type="video/mp4")


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
        """Upload de exatamente 4 imagens (limite máximo)."""

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
        """Upload de mais de 4 imagens retorna erro 400."""
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
        """Imagem maior que 5MB retorna erro 400."""
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
        """Vídeo maior que 50MB retorna erro 400."""
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
