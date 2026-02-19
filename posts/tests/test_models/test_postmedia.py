from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from PIL import Image

from posts.models import Post, PostMedia

User = get_user_model()


@pytest.mark.django_db
class TestPostMediaModel:
    """Testes para o model PostMedia - MÚLTIPLAS MÍDIAS."""

    def test_create_post_media(self):
        """Testa criação de PostMedia."""

        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test post")

        # Criar imagem fake
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

        assert media.post == post
        assert media.type == "image"
        assert media.order == 0
        assert media.file is not None

    def test_post_media_str(self):
        """Testa representação string de PostMedia."""

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
            post=post, type="video", file=test_image, order=1
        )

        media_str = str(media)
        assert "Vídeo" in media_str or "Video" in media_str
        assert str(post.id) in media_str
        assert "1" in media_str  # ordem

    def test_post_media_ordering(self):
        """Testa ordenação de mídias por order e created_at."""

        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        def create_test_image(name):
            file = BytesIO()
            image = Image.new("RGB", (100, 100), color="red")
            image.save(file, "JPEG")
            file.seek(0)
            return SimpleUploadedFile(
                name=name, content=file.read(), content_type="image/jpeg"
            )

        media2 = PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img2.jpg"), order=2
        )
        media1 = PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img1.jpg"), order=1
        )
        media3 = PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img3.jpg"), order=3
        )

        media_list = list(post.media.all())

        assert media_list[0] == media1
        assert media_list[1] == media2
        assert media_list[2] == media3
