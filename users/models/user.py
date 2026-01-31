"""
User model - Usuário customizado do sistema.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo de usuário customizado estendendo AbstractUser.

    Adiciona campos específicos para a rede social:
    - bio: biografia do usuário
    - profile_image: foto de perfil
    - banner: imagem de capa do perfil
    - location: localização do usuário
    - website: site pessoal
    - birth_date: data de nascimento
    - created_at: data de criação
    - updated_at: data da última atualização
    """

    # Campos adicionais
    bio = models.TextField(
        max_length=160,
        blank=True,
        default="",
        verbose_name="Biografia",
        help_text="Biografia do usuário (máximo 160 caracteres)",
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
        help_text="Imagem de perfil do usuário",
    )

    # NOVOS CAMPOS
    banner = models.ImageField(
        upload_to="banners/",
        blank=True,
        null=True,
        verbose_name="Banner do perfil",
        help_text="Imagem de capa do perfil do usuário",
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Localização",
        help_text="Localização do usuário (cidade, país, etc)",
    )

    website = models.URLField(
        blank=True,
        default="",
        verbose_name="Site pessoal",
        help_text="URL do site ou blog pessoal",
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de nascimento",
        help_text="Data de nascimento do usuário",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

    # Properties para contadores
    @property
    def followers_count(self):
        """Retorna quantidade de seguidores."""
        return self.followers.count()

    @property
    def following_count(self):
        """Retorna quantidade de pessoas que o usuário segue."""
        return self.following.count()

    @property
    def posts_count(self):
        """Retorna quantidade de posts do usuário."""
        return self.posts.count()
