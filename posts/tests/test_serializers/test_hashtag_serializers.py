from django.contrib.auth import get_user_model

import pytest

from posts.models import Hashtag, Post
from posts.serializers import HashtagSerializer, PostCreateSerializer, PostSerializer

User = get_user_model()


@pytest.mark.django_db
class TestHashtagSerializer:
    """Testes para HashtagSerializer."""

    def test_serialize_hashtag(self):
        """Testa serialização de hashtag."""
        hashtag = Hashtag.objects.create(name="python", posts_count=5)

        serializer = HashtagSerializer(hashtag)
        data = serializer.data

        assert data["name"] == "python"
        assert data["slug"] == "python"
        assert data["posts_count"] == 5
        assert "created_at" in data

    def test_hashtag_fields_readonly(self):
        """Testa que campos são read-only."""
        hashtag = Hashtag.objects.create(name="python")

        serializer = HashtagSerializer(hashtag)

        # Todos os campos devem ser read-only
        assert "id" in serializer.data
        assert "slug" in serializer.data


@pytest.mark.django_db
class TestPostSerializerWithHashtags:
    """Testes para PostSerializer com hashtags."""

    def test_post_includes_hashtags(self):
        """Testa que PostSerializer inclui hashtags."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test #python")
        tag = Hashtag.objects.create(name="python")
        post.hashtags.add(tag)

        serializer = PostSerializer(post)
        data = serializer.data

        assert "hashtags" in data
        assert len(data["hashtags"]) == 1
        assert data["hashtags"][0]["name"] == "python"

    def test_post_with_multiple_hashtags(self):
        """Testa post com múltiplas hashtags."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test")
        tag1 = Hashtag.objects.create(name="python")
        tag2 = Hashtag.objects.create(name="django")
        post.hashtags.add(tag1, tag2)

        serializer = PostSerializer(post)
        data = serializer.data

        assert len(data["hashtags"]) == 2
        names = [h["name"] for h in data["hashtags"]]
        assert "python" in names
        assert "django" in names


@pytest.mark.django_db
class TestPostCreateSerializerHashtagExtraction:
    """Testes para extração automática de hashtags no PostCreateSerializer."""

    def test_create_post_extracts_hashtags(self):
        """Testa que hashtags são extraídas automaticamente."""
        user = User.objects.create_user(username="testuser", password="pass123")

        data = {"content": "Adorei #python e #django!"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        post = serializer.save(author=user)

        # Verificar que hashtags foram extraídas
        assert post.hashtags.count() == 2

        hashtag_names = [h.name for h in post.hashtags.all()]
        assert "python" in hashtag_names
        assert "django" in hashtag_names

    def test_create_post_creates_new_hashtags(self):
        """Testa que hashtags novas são criadas."""
        user = User.objects.create_user(username="testuser", password="pass123")

        assert Hashtag.objects.count() == 0

        data = {"content": "Test #newtag"}
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        serializer.save(author=user)

        # Verificar que hashtag foi criada
        assert Hashtag.objects.count() == 1
        hashtag = Hashtag.objects.get(name="newtag")
        assert hashtag.posts_count == 1

    def test_create_post_reuses_existing_hashtags(self):
        """Testa que hashtags existentes são reutilizadas."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Criar hashtag existente
        existing_tag = Hashtag.objects.create(name="python", posts_count=5)

        data = {"content": "Test #python"}
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        serializer.save(author=user)

        # Verificar que não criou nova hashtag
        assert Hashtag.objects.count() == 1

        # Verificar que posts_count foi incrementado
        existing_tag.refresh_from_db()
        assert existing_tag.posts_count == 6

    def test_create_post_without_hashtags(self):
        """Testa criação de post sem hashtags."""
        user = User.objects.create_user(username="testuser", password="pass123")

        data = {"content": "Post sem hashtags"}
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        post = serializer.save(author=user)

        assert post.hashtags.count() == 0

    def test_create_post_normalizes_hashtags(self):
        """Testa normalização de hashtags (lowercase, sem duplicatas)."""
        user = User.objects.create_user(username="testuser", password="pass123")

        data = {"content": "#Python #PYTHON #python"}
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        post = serializer.save(author=user)

        # Deve ter apenas uma hashtag
        assert post.hashtags.count() == 1
        assert post.hashtags.first().name == "python"
