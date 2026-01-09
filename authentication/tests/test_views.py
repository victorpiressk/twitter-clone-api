"""
Testes para as views de autenticação.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture para cliente da API."""
    return APIClient()


@pytest.fixture
def user_data():
    """Fixture com dados de usuário para testes."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.mark.django_db
class TestRegisterView:
    """Testes para o endpoint de registro."""

    def test_register_success(self, api_client, user_data):
        """Testa registro com dados válidos."""
        url = reverse("auth-register")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "user" in response.data
        assert "token" in response.data
        assert response.data["user"]["username"] == "testuser"
        assert response.data["user"]["email"] == "test@example.com"
        assert User.objects.filter(username="testuser").exists()

    def test_register_password_mismatch(self, api_client, user_data):
        """Testa registro com senhas diferentes."""
        user_data["password_confirm"] = "differentpass"
        url = reverse("auth-register")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "password_confirm" in response.data or "non_field_errors" in response.data
        )

    def test_register_duplicate_username(self, api_client, user_data):
        """Testa registro com username já existente."""
        User.objects.create_user(
            username="testuser", email="other@example.com", password="pass123"
        )

        url = reverse("auth-register")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_register_duplicate_email(self, api_client, user_data):
        """Testa registro com email já existente."""
        User.objects.create_user(
            username="otheruser", email="test@example.com", password="pass123"
        )

        url = reverse("auth-register")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_missing_fields(self, api_client):
        """Testa registro com campos faltando."""
        url = reverse("auth-register")
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data
        assert "password" in response.data


@pytest.mark.django_db
class TestLoginView:
    """Testes para o endpoint de login."""

    @pytest.fixture
    def existing_user(self):
        """Fixture com usuário já cadastrado."""
        return User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_login_success(self, api_client, existing_user):
        """Testa login com credenciais válidas."""
        url = reverse("auth-login")
        response = api_client.post(
            url, {"username": "testuser", "password": "testpass123"}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "user" in response.data
        assert "token" in response.data
        assert response.data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, api_client, existing_user):
        """Testa login com senha incorreta."""
        url = reverse("auth-login")
        response = api_client.post(
            url, {"username": "testuser", "password": "wrongpass"}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self, api_client):
        """Testa login com usuário inexistente."""
        url = reverse("auth-login")
        response = api_client.post(
            url, {"username": "nonexistent", "password": "testpass123"}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_fields(self, api_client):
        """Testa login com campos faltando."""
        url = reverse("auth-login")
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutView:
    """Testes para o endpoint de logout."""

    @pytest.fixture
    def authenticated_client(self, api_client):
        """Fixture com cliente autenticado."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        api_client.force_authenticate(user=user)
        return api_client, user

    def test_logout_success(self, authenticated_client):
        """Testa logout com usuário autenticado."""
        api_client, user = authenticated_client
        url = reverse("auth-logout")
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data

    def test_logout_unauthenticated(self, api_client):
        """Testa logout sem estar autenticado."""
        url = reverse("auth-logout")
        response = api_client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
