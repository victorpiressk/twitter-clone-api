"""
Testes para os serializers do app users.
"""

from datetime import date, timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from PIL import Image

from users.models import Follow
from users.serializers import FollowSerializer, UserCreateSerializer, UserSerializer

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializer:
    """Testes para o UserSerializer."""

    def test_serialize_user(self):
        """Testa serialização de usuário."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            bio="Test bio",
        )

        serializer = UserSerializer(user)
        data = serializer.data

        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["bio"] == "Test bio"
        assert "password" not in data  # Senha não deve aparecer

    def test_serialize_user_stats_object(self):
        """Testa que stats é retornado como objeto."""
        user = User.objects.create_user(username="user1", password="pass123")

        serializer = UserSerializer(user)
        data = serializer.data

        assert "stats" in data
        assert isinstance(data["stats"], dict)
        assert data["stats"]["posts"] == 0
        assert data["stats"]["following"] == 0
        assert data["stats"]["followers"] == 0

    def test_serialize_user_with_followers(self):
        """Testa serialização com contadores."""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        # user2 e user3 seguem user1
        Follow.objects.create(follower=user2, following=user1)
        Follow.objects.create(follower=user3, following=user1)

        serializer = UserSerializer(user1)
        data = serializer.data

        assert data["stats"]["followers"] == 2
        assert data["stats"]["following"] == 0

    def test_serialize_user_with_all_fields(self):
        """Testa serialização com todos os campos novos."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            location="São Paulo, Brasil",
            website="https://example.com",
            birth_date=date(1995, 5, 15),
        )

        serializer = UserSerializer(user)
        data = serializer.data

        assert data["location"] == "São Paulo, Brasil"
        assert data["website"] == "https://example.com"
        assert data["birth_date"] == "1995-05-15"
        assert "banner" in data

    def test_validate_banner_too_large(self):
        """Testa que banner acima de 5MB é rejeitado."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Cria um arquivo "fake" de 6MB
        file = BytesIO()
        Image.new("RGB", (100, 100)).save(file, "JPEG")
        file.write(b"\0" * (6 * 1024 * 1024))  # Adiciona 6MB de lixo
        file.seek(0)
        large_banner = SimpleUploadedFile(
            "large.jpg", file.read(), content_type="image/jpeg"
        )

        data = {"banner": large_banner}
        serializer = UserSerializer(user, data=data, partial=True)

        assert not serializer.is_valid()
        assert "banner" in serializer.errors
        assert "Imagem muito grande. Máximo: 5MB" in str(serializer.errors["banner"][0])

    def test_validate_image_invalid_format(self):
        """Testa que formatos não permitidos (ex: GIF) são rejeitados."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Cria um GIF (supondo que seu allowed_formats não tenha GIF)
        file = BytesIO()
        Image.new("RGB", (100, 100)).save(file, "GIF")
        file.seek(0)
        gif_file = SimpleUploadedFile("test.gif", file.read(), content_type="image/gif")

        data = {"profile_image": gif_file}
        serializer = UserSerializer(user, data=data, partial=True)

        assert not serializer.is_valid()
        assert "profile_image" in serializer.errors
        assert "Formato não aceito. Use JPEG, PNG ou WEBP." in str(
            serializer.errors["profile_image"][0]
        )

    def test_validate_website_invalid(self):
        """Testa validação de website inválido."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "website": "invalid-url",  # Sem http:// ou https://
        }

        serializer = UserSerializer(data=data, partial=True)
        assert not serializer.is_valid()
        assert "website" in serializer.errors

    def test_validate_website_valid(self):
        """Testa validação de website válido."""
        user = User.objects.create_user(username="testuser", password="pass123")

        data = {"website": "https://example.com"}

        serializer = UserSerializer(user, data=data, partial=True)
        assert serializer.is_valid()

    def test_validate_birth_date_under_13(self):
        """Testa que menor de 13 anos não pode se cadastrar."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Data de nascimento de alguém com 10 anos
        birth_date = date.today() - timedelta(days=365 * 10)

        data = {"birth_date": birth_date}

        serializer = UserSerializer(user, data=data, partial=True)
        assert not serializer.is_valid()
        assert "birth_date" in serializer.errors

    def test_validate_birth_date_future(self):
        """Testa que data de nascimento não pode ser no futuro."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Data futura
        birth_date = date.today() + timedelta(days=365)

        data = {"birth_date": birth_date}

        serializer = UserSerializer(user, data=data, partial=True)
        assert not serializer.is_valid()
        assert "birth_date" in serializer.errors

    def test_validate_birth_date_valid(self):
        """Testa data de nascimento válida (maior de 13 anos)."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Data de nascimento de alguém com 20 anos
        birth_date = date.today() - timedelta(days=365 * 20)

        data = {"birth_date": birth_date}

        serializer = UserSerializer(user, data=data, partial=True)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestUserCreateSerializer:
    """Testes para o UserCreateSerializer."""

    def test_create_user_valid(self):
        """Testa criação de usuário com dados válidos."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()

        user = serializer.save()

        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.check_password("newpass123")
        assert user.first_name == "New"
        assert user.last_name == "User"

    def test_create_user_password_mismatch(self):
        """Testa criação com senhas diferentes."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "password_confirm": "differentpass",
            "first_name": "New",
            "last_name": "User",
        }

        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert (
            "password_confirm" in serializer.errors
            or "non_field_errors" in serializer.errors
        )

    def test_create_user_missing_fields(self):
        """Testa criação com campos obrigatórios faltando."""
        data = {"username": "newuser"}

        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
        assert "password_confirm" in serializer.errors

    def test_password_min_length(self):
        """Testa validação de tamanho mínimo de senha."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "short",
            "password_confirm": "short",
        }

        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors


@pytest.mark.django_db
class TestFollowSerializer:
    """Testes para o FollowSerializer."""

    def test_serialize_follow(self):
        """Testa serialização de follow."""
        user1 = User.objects.create_user(username="follower", password="pass123")
        user2 = User.objects.create_user(username="following", password="pass123")

        follow = Follow.objects.create(follower=user1, following=user2)

        serializer = FollowSerializer(follow)
        data = serializer.data

        assert data["follower"] == user1.id
        assert data["following"] == user2.id
        assert data["follower_username"] == "follower"
        assert data["following_username"] == "following"

    def test_create_follow_valid(self):
        """Testa criação de follow válido."""
        user1 = User.objects.create_user(username="follower", password="pass123")
        user2 = User.objects.create_user(username="following", password="pass123")

        data = {"follower": user1.id, "following": user2.id}

        serializer = FollowSerializer(data=data)
        assert serializer.is_valid()

        follow = serializer.save()

        assert follow.follower == user1
        assert follow.following == user2

    def test_cannot_follow_self(self):
        """Testa que não pode seguir a si mesmo."""
        user = User.objects.create_user(username="user1", password="pass123")

        data = {"follower": user.id, "following": user.id}

        serializer = FollowSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
