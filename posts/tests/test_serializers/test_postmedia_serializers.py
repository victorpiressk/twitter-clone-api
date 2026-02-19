from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from PIL import Image
from rest_framework.test import APIRequestFactory

from posts.models import Post, PostMedia
from posts.serializers import PostMediaSerializer, PostSerializer

User = get_user_model()


@pytest.mark.django_db
class TestPostMediaSerializer:
    """Testes para PostMediaSerializer - MÚLTIPLAS MÍDIAS."""

    def test_serialize_post_with_media(self):
        """Testa serialização de post com mídias."""

        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Post with media")

        def create_test_image(name):
            file = BytesIO()
            image = Image.new("RGB", (100, 100), color="red")
            image.save(file, "JPEG")
            file.seek(0)
            return SimpleUploadedFile(
                name=name, content=file.read(), content_type="image/jpeg"
            )

        PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img1.jpg"), order=0
        )
        PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img2.jpg"), order=1
        )

        serializer = PostSerializer(post)
        data = serializer.data

        assert "media" in data
        assert len(data["media"]) == 2
        assert data["media"][0]["type"] == "image"
        assert data["media"][0]["order"] == 0
        assert "url" in data["media"][0]

    def test_media_url_generation(self):
        """Testa geração de URL da mídia."""

        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        file = BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(file, "JPEG")
        file.seek(0)
        test_image = SimpleUploadedFile(
            name="test.jpg", content=file.read(), content_type="image/jpeg"
        )

        media = PostMedia.objects.create(
            post=post, type="image", file=test_image, order=0
        )

        # Criar request mock para context
        factory = APIRequestFactory()
        request = factory.get("/")

        serializer = PostMediaSerializer(media, context={"request": request})
        data = serializer.data

        assert "url" in data
        assert data["url"] is not None
