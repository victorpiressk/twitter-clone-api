"""
Configuração do pytest para testes.
"""

from django.conf import settings

import pytest


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
