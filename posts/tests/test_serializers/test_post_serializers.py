from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from PIL import Image
from rest_framework.test import APIRequestFactory

from posts.models import Like, Post
from posts.serializers import PostCreateSerializer, PostSerializer

User = get_user_model()


@pytest.mark.django_db
class TestPostSerializer:
    """Testes para o PostSerializer."""

    def test_serialize_post(self):
        """Testa serialização de post."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test post content")

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["content"] == "Test post content"
        assert data["author"]["username"] == "author"
        assert "created_at" in data

    # TESTE - Stats como objeto
    def test_serialize_post_stats_object(self):
        """Testa que stats é retornado como objeto."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test")

        serializer = PostSerializer(post)
        data = serializer.data

        assert "stats" in data
        assert isinstance(data["stats"], dict)
        assert data["stats"]["replies"] == 0
        assert data["stats"]["retweets"] == 0
        assert data["stats"]["likes"] == 0
        assert data["stats"]["views"] == 0

    def test_serialize_post_with_counts(self):
        """Testa serialização com contadores."""
        author = User.objects.create_user(username="author", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        post = Post.objects.create(author=author, content="Test")

        # Criar likes e replies
        Like.objects.create(user=user2, post=post)
        Like.objects.create(user=user3, post=post)
        Post.objects.create(author=user2, content="Reply 1", in_reply_to=post)
        Post.objects.create(author=user3, content="Reply 2", in_reply_to=post)
        Post.objects.create(author=user3, content="Reply 3", in_reply_to=post)

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["stats"]["likes"] == 2
        assert data["stats"]["replies"] == 3

    def test_is_liked_false_without_auth(self):
        """Testa que is_liked retorna False sem usuário autenticado."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test")

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["is_liked"] is False
        assert data["like_id"] is None

    def test_is_liked_true(self):
        """Testa que is_liked retorna True se usuário curtiu."""
        author = User.objects.create_user(username="author", password="pass123")
        user = User.objects.create_user(username="user", password="pass123")
        post = Post.objects.create(author=author, content="Test")
        like = Like.objects.create(user=user, post=post)

        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        serializer = PostSerializer(post, context={"request": request})
        data = serializer.data

        assert data["is_liked"] is True
        assert data["like_id"] == like.id

    def test_is_liked_false(self):
        """Testa que is_liked retorna False se usuário não curtiu."""
        author = User.objects.create_user(username="author", password="pass123")
        user = User.objects.create_user(username="user", password="pass123")
        post = Post.objects.create(author=author, content="Test")

        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        serializer = PostSerializer(post, context={"request": request})
        data = serializer.data

        assert data["is_liked"] is False
        assert data["like_id"] is None

    # TESTES - Retweets
    def test_serialize_retweet(self):
        """Testa serialização de retweet."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original")
        retweet = Post.objects.create(
            author=retweeter, content="", is_retweet=True, retweet_of=original_post
        )

        serializer = PostSerializer(retweet)
        data = serializer.data

        assert data["is_retweet"] is True
        assert data["retweet_of"] == original_post.id
        assert data["author"]["username"] == "retweeter"

    def test_serialize_quote_retweet(self):
        """Testa serialização de quote retweet."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original")
        quote_retweet = Post.objects.create(
            author=retweeter,
            content="Concordo!",
            is_retweet=True,
            retweet_of=original_post,
        )

        serializer = PostSerializer(quote_retweet)
        data = serializer.data

        assert data["is_retweet"] is True
        assert data["retweet_of"] == original_post.id
        assert data["content"] == "Concordo!"

    def test_is_retweeted_true(self):
        """Testa que is_retweeted retorna True se usuário retweetou."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original")

        # Criar retweet
        Post.objects.create(
            author=retweeter, content="", is_retweet=True, retweet_of=original_post
        )

        # Criar request mock com usuário autenticado
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = retweeter

        serializer = PostSerializer(original_post, context={"request": request})
        data = serializer.data

        assert data["is_retweeted"] is True

    def test_is_retweeted_false(self):
        """Testa que is_retweeted retorna False se usuário não retweetou."""
        author = User.objects.create_user(username="author", password="pass123")
        user = User.objects.create_user(username="user", password="pass123")

        post = Post.objects.create(author=author, content="Test")

        # Criar request mock com usuário autenticado
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        serializer = PostSerializer(post, context={"request": request})
        data = serializer.data

        assert data["is_retweeted"] is False

    def test_retweets_count_in_stats(self):
        """Testa que retweets_count aparece em stats."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test")

        # Manualmente incrementar contador
        post.retweets_count = 5
        post.save()

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["stats"]["retweets"] == 5

    # TESTES - Replies
    def test_serialize_reply(self):
        """Testa serialização de reply."""
        author = User.objects.create_user(username="author", password="pass123")
        replier = User.objects.create_user(username="replier", password="pass123")

        original = Post.objects.create(author=author, content="Original")
        reply = Post.objects.create(
            author=replier, content="This is a reply", in_reply_to=original
        )

        serializer = PostSerializer(reply)
        data = serializer.data

        assert data["in_reply_to"] == original.id
        assert data["content"] == "This is a reply"
        assert data["author"]["username"] == "replier"

    def test_serialize_post_without_reply(self):
        """Testa que in_reply_to é None para posts normais."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Normal post")

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["in_reply_to"] is None


@pytest.mark.django_db
class TestPostCreateSerializer:
    """Testes para o PostCreateSerializer."""

    def test_create_post_valid(self):
        """Testa criação de post com dados válidos."""
        data = {"content": "New post content"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_post_empty_content(self):
        """Testa criação com conteúdo vazio."""
        data = {"content": "   "}  # Apenas espaços

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "content" in serializer.errors

    def test_create_post_missing_content(self):
        """Testa criação sem conteúdo."""
        data = {}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "content" in serializer.errors

    # TESTES - Replies no create
    def test_create_reply_valid(self):
        """Testa criação de reply com in_reply_to válido."""
        author = User.objects.create_user(username="author", password="pass123")
        original = Post.objects.create(author=author, content="Original")

        data = {"content": "This is a reply", "in_reply_to": original.id}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_reply_invalid_post(self):
        """Testa que in_reply_to com post inexistente retorna erro."""
        data = {
            "content": "Reply to nothing",
            "in_reply_to": 99999,  # Post que não existe
        }

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "in_reply_to" in serializer.errors

    def test_create_post_without_reply(self):
        """Testa que in_reply_to é opcional."""
        data = {"content": "Normal post"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()
        assert (
            "in_reply_to" not in serializer.validated_data
            or serializer.validated_data.get("in_reply_to") is None
        )

    # TESTES - Múltiplas Mídias (Validações)
    def test_validate_media_files_max_4(self):
        """Testa validação de máximo 4 mídias."""

        def create_test_image(name):
            file = BytesIO()
            image = Image.new("RGB", (100, 100), color="red")
            image.save(file, "JPEG")
            file.seek(0)
            return SimpleUploadedFile(
                name=name, content=file.read(), content_type="image/jpeg"
            )

        # 5 imagens (excede limite)
        media_files = [create_test_image(f"img{i}.jpg") for i in range(5)]

        data = {"content": "Post with too many images", "media_files": media_files}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "media_files" in serializer.errors
        assert "4" in str(serializer.errors["media_files"][0])

    def test_validate_image_size(self):
        """Testa validação de tamanho de imagem (máx 5MB)."""

        # Imagem de 6MB (excede limite)
        large_content = b"0" * (6 * 1024 * 1024)
        large_image = SimpleUploadedFile(
            name="large.jpg", content=large_content, content_type="image/jpeg"
        )

        data = {"content": "Post with large image", "media_files": [large_image]}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "media_files" in serializer.errors
        assert "5MB" in str(serializer.errors["media_files"][0])

    def test_validate_video_size(self):
        """Testa validação de tamanho de vídeo (máx 50MB)."""

        # Vídeo de 60MB (excede limite)
        large_content = b"0" * (60 * 1024 * 1024)
        large_video = SimpleUploadedFile(
            name="large.mp4", content=large_content, content_type="video/mp4"
        )

        data = {"content": "Post with large video", "media_files": [large_video]}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "media_files" in serializer.errors
        assert "50MB" in str(serializer.errors["media_files"][0])

    def test_validate_unsupported_file_type(self):
        """Testa validação de tipo de arquivo não suportado."""

        txt_file = SimpleUploadedFile(
            name="document.txt", content=b"Hello world", content_type="text/plain"
        )

        data = {"content": "Post with txt file", "media_files": [txt_file]}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "media_files" in serializer.errors
        assert "suportado" in str(serializer.errors["media_files"][0]).lower()
