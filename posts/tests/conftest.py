"""
Configuração do pytest para testes.
"""

from django.conf import settings
from django.contrib.auth import get_user_model

import pytest
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture(scope="session", autouse=True)
def setup_test_media(tmp_path_factory):
    """
    Configura MEDIA_ROOT para usar diretório temporário durante testes.

    Evita criar a pasta 'medias' no diretório do projeto.
    Os arquivos são criados em /tmp e deletados automaticamente.
    """
    media_root = tmp_path_factory.mktemp("test_media")
    settings.MEDIA_ROOT = str(media_root)
    return media_root


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):  # A fixture 'db' é necessária para criar objetos no banco
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username="anotheruser", email="another@example.com", password="testpass123"
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
