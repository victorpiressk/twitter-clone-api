"""
Testes para as views do app users.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from io import BytesIO
from PIL import Image

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Follow

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
def authenticated_client(api_client, user):
    """Fixture com cliente autenticado."""
    api_client.force_authenticate(user=user)
    return api_client


def create_test_image():
    """Cria uma imagem de teste."""
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'PNG')
    file.seek(0)
    return SimpleUploadedFile('test.png', file.read(), content_type='image/png')


@pytest.mark.django_db
class TestUserViewSet:
    """Testes para o UserViewSet."""

    def test_list_users(self, api_client):
        """Testa listagem de usuários (público)."""
        User.objects.create_user(username="user1", password="pass123")
        User.objects.create_user(username="user2", password="pass123")

        url = reverse("user-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_retrieve_user(self, api_client, user):
        """Testa obter detalhes de usuário."""
        url = reverse("user-detail", kwargs={"pk": user.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"
        assert response.data["email"] == "test@example.com"

    def test_me_endpoint_authenticated(self, authenticated_client, user):
        """Testa endpoint /me com usuário autenticado."""
        url = reverse("user-me")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"

    def test_me_endpoint_unauthenticated(self, api_client):
        """Testa endpoint /me sem autenticação."""
        url = reverse("user-me")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # TESTES - Upload de banner
    def test_update_user_with_banner(self, authenticated_client, user):
        """Testa atualização de usuário com banner."""
        url = reverse("user-detail", kwargs={"pk": user.pk})
        
        banner = create_test_image()
        
        data = {
            "banner": banner,
            "location": "São Paulo, Brasil",
        }

        response = authenticated_client.patch(url, data, format='multipart')

        assert response.status_code == status.HTTP_200_OK
        assert response.data["location"] == "São Paulo, Brasil"
        assert "banner" in response.data
        
        user.refresh_from_db()
        assert user.banner is not None

    

    def test_update_user_profile_image_valid(self, authenticated_client, user):
        """Testa upload de profile_image válido."""
        url = reverse("user-detail", kwargs={"pk": user.pk})
        
        profile_image = create_test_image()
        
        data = {"profile_image": profile_image}

        response = authenticated_client.patch(url, data, format='multipart')

        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.profile_image is not None

    # TESTES - Novos campos de texto
    def test_update_user_location_website(self, authenticated_client, user):
        """Testa atualização de location e website."""
        url = reverse("user-detail", kwargs={"pk": user.pk})
        
        data = {
            "location": "Rio de Janeiro, Brasil",
            "website": "https://example.com",
        }

        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data["location"] == "Rio de Janeiro, Brasil"
        assert response.data["website"] == "https://example.com"

    def test_update_user_invalid_website(self, authenticated_client, user):
        """Testa que website inválido retorna erro."""
        url = reverse("user-detail", kwargs={"pk": user.pk})
        
        data = {"website": "invalid-url"}

        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "website" in response.data

    def test_update_user_birth_date_valid(self, authenticated_client, user):
        """Testa atualização de birth_date válida."""
        url = reverse("user-detail", kwargs={"pk": user.pk})
        
        birth_date = date.today() - timedelta(days=365 * 20)  # 20 anos
        
        data = {"birth_date": birth_date.isoformat()}

        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data["birth_date"] == birth_date.isoformat()

    # TESTE - Stats como objeto
    def test_user_stats_as_object(self, api_client, user):
        """Testa que stats é retornado como objeto."""
        url = reverse("user-detail", kwargs={"pk": user.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "stats" in response.data
        assert isinstance(response.data["stats"], dict)
        assert "posts" in response.data["stats"]
        assert "following" in response.data["stats"]
        assert "followers" in response.data["stats"]

    # TESTE - Outro usuário não pode editar
    def test_cannot_update_other_user(self, authenticated_client):
        """Testa que usuário não pode editar perfil de outro."""
        other_user = User.objects.create_user(username="other", password="pass123")
        
        url = reverse("user-detail", kwargs={"pk": other_user.pk})
        
        data = {"location": "Tentando editar outro usuário"}

        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_followers(self, api_client, user):
        """Testa endpoint de seguidores."""
        follower1 = User.objects.create_user(username="follower1", password="pass123")
        follower2 = User.objects.create_user(username="follower2", password="pass123")

        Follow.objects.create(follower=follower1, following=user)
        Follow.objects.create(follower=follower2, following=user)

        url = reverse("user-followers", kwargs={"pk": user.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_user_following(self, api_client, user):
        """Testa endpoint de quem o usuário segue."""
        following1 = User.objects.create_user(username="following1", password="pass123")
        following2 = User.objects.create_user(username="following2", password="pass123")

        Follow.objects.create(follower=user, following=following1)
        Follow.objects.create(follower=user, following=following2)

        url = reverse("user-following", kwargs={"pk": user.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


@pytest.mark.django_db
class TestFollowViewSet:
    """Testes para o FollowViewSet."""

    def test_create_follow_authenticated(self, authenticated_client, user):
        """Testa seguir usuário estando autenticado."""
        user_to_follow = User.objects.create_user(username="user2", password="pass123")

        url = reverse("follow-list")
        response = authenticated_client.post(
            url, {"following": user_to_follow.id}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Follow.objects.filter(follower=user, following=user_to_follow).exists()

    def test_create_follow_unauthenticated(self, api_client):
        """Testa seguir usuário sem autenticação."""
        user_to_follow = User.objects.create_user(username="user2", password="pass123")

        url = reverse("follow-list")
        response = api_client.post(url, {"following": user_to_follow.id}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_follow_twice(self, authenticated_client, user):
        """Testa que não pode seguir o mesmo usuário duas vezes."""
        user_to_follow = User.objects.create_user(username="user2", password="pass123")

        # Primeiro follow
        Follow.objects.create(follower=user, following=user_to_follow)

        # Tentar seguir novamente
        url = reverse("follow-list")
        response = authenticated_client.post(
            url, {"following": user_to_follow.id}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unfollow(self, authenticated_client, user):
        """Testa deixar de seguir."""
        user_to_follow = User.objects.create_user(username="user2", password="pass123")
        follow = Follow.objects.create(follower=user, following=user_to_follow)

        url = reverse("follow-detail", kwargs={"pk": follow.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Follow.objects.filter(
            follower=user, following=user_to_follow
        ).exists()

    def test_cannot_unfollow_others_follow(self, authenticated_client, user):
        """Testa que não pode desfazer follow de outro usuário."""
        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        # user2 segue user3
        follow = Follow.objects.create(follower=user2, following=user3)

        # user tenta desfazer o follow de user2
        url = reverse("follow-detail", kwargs={"pk": follow.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Follow.objects.filter(follower=user2, following=user3).exists()