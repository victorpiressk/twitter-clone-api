"""
Location model - Geolocalização de posts.
"""

from django.db import models


class Location(models.Model):
    """
    Modelo para localizações geográficas.

    Armazena locais que podem ser anexados a posts.
    Locais com mesmas coordenadas são reutilizados.
    """

    name = models.CharField(
        max_length=200,
        verbose_name="Nome",
        help_text="Nome do local (ex: 'São Paulo, Brasil')",
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitude",
        help_text="Coordenada de latitude (-90 a 90)",
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitude",
        help_text="Coordenada de longitude (-180 a 180)",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Localização"
        verbose_name_plural = "Localizações"
        ordering = ["name"]
        unique_together = ("latitude", "longitude")
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        if self.latitude and self.longitude:
            return f"{self.name} ({self.latitude}, {self.longitude})"
        return self.name

    @property
    def has_coordinates(self):
        """Verifica se a localização tem coordenadas."""
        return self.latitude is not None and self.longitude is not None
