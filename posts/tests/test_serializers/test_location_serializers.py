from decimal import Decimal

from django.contrib.auth import get_user_model

import pytest

from posts.models import Location
from posts.serializers import LocationCreateSerializer, LocationSerializer

User = get_user_model()


@pytest.mark.django_db
class TestLocationSerializer:
    """Testes para LocationSerializer."""

    def test_serialize_location_with_coordinates(self):
        """Testa serialização de location com coordenadas."""
        location = Location.objects.create(
            name="Torre Eiffel, Paris",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )

        serializer = LocationSerializer(location)
        data = serializer.data

        assert data["name"] == "Torre Eiffel, Paris"
        assert data["latitude"] == "48.858844"
        assert data["longitude"] == "2.294351"
        assert data["has_coordinates"] is True

    def test_serialize_location_without_coordinates(self):
        """Testa serialização de location sem coordenadas."""
        location = Location.objects.create(name="Brasil")

        serializer = LocationSerializer(location)
        data = serializer.data

        assert data["name"] == "Brasil"
        assert data["latitude"] is None
        assert data["longitude"] is None
        assert data["has_coordinates"] is False

    def test_has_coordinates_field_readonly(self):
        """Testa que has_coordinates é read-only."""
        location = Location.objects.create(
            name="Local", latitude=Decimal("10.0"), longitude=Decimal("20.0")
        )

        serializer = LocationSerializer(location)
        assert "has_coordinates" in serializer.data
        assert serializer.data["has_coordinates"] is True


@pytest.mark.django_db
class TestLocationCreateSerializer:
    """Testes para LocationCreateSerializer."""

    def test_create_location_with_coordinates(self):
        """Testa criação de location com coordenadas."""
        data = {"name": "Paris, França", "latitude": "48.8566", "longitude": "2.3522"}

        serializer = LocationCreateSerializer(data=data)
        assert serializer.is_valid()

        location = serializer.save()

        assert location.name == "Paris, França"
        assert location.latitude == Decimal("48.8566")
        assert location.longitude == Decimal("2.3522")

    def test_create_location_without_coordinates(self):
        """Testa criação de location sem coordenadas."""
        data = {"name": "Algum lugar"}

        serializer = LocationCreateSerializer(data=data)
        assert serializer.is_valid()

        location = serializer.save()

        assert location.name == "Algum lugar"
        assert location.latitude is None
        assert location.longitude is None

    def test_validate_latitude_without_longitude(self):
        """Testa validação: latitude sem longitude."""
        data = {"name": "Local", "latitude": "10.0"}

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
        assert "juntas" in str(serializer.errors["non_field_errors"][0]).lower()

    def test_validate_longitude_without_latitude(self):
        """Testa validação: longitude sem latitude."""
        data = {"name": "Local", "longitude": "20.0"}

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_validate_latitude_range(self):
        """Testa validação: latitude fora do range (-90 a 90)."""
        # Latitude > 90
        data = {"name": "Local", "latitude": "95.0", "longitude": "10.0"}

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "latitude" in serializer.errors

        # Latitude < -90
        data["latitude"] = "-95.0"

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "latitude" in serializer.errors

    def test_validate_longitude_range(self):
        """Testa validação: longitude fora do range (-180 a 180)."""
        # Longitude > 180
        data = {"name": "Local", "latitude": "10.0", "longitude": "185.0"}

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "longitude" in serializer.errors

        # Longitude < -180
        data["longitude"] = "-185.0"

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "longitude" in serializer.errors

    def test_get_or_create_by_coordinates(self):
        """Testa reutilização de location por coordenadas (get_or_create)."""
        # Criar location inicial
        data = {
            "name": "Torre Eiffel",
            "latitude": "48.858844",
            "longitude": "2.294351",
        }

        serializer1 = LocationCreateSerializer(data=data)
        assert serializer1.is_valid()
        location1 = serializer1.save()

        # Tentar criar com mesmas coordenadas mas nome diferente
        data2 = {
            "name": "Eiffel Tower",
            "latitude": "48.858844",
            "longitude": "2.294351",
        }

        serializer2 = LocationCreateSerializer(data=data2)
        assert serializer2.is_valid()
        location2 = serializer2.save()

        # Deve retornar o mesmo location (unique_together)
        assert location1.id == location2.id
        assert location2.name == "Torre Eiffel"  # Nome original mantido

    def test_get_or_create_by_name(self):
        """Testa reutilização de location por nome (sem coordenadas)."""
        # Criar location sem coordenadas
        data = {"name": "Brasil"}

        serializer1 = LocationCreateSerializer(data=data)
        assert serializer1.is_valid()
        location1 = serializer1.save()

        # Tentar criar com mesmo nome
        serializer2 = LocationCreateSerializer(data=data)
        assert serializer2.is_valid()
        location2 = serializer2.save()

        # Deve retornar o mesmo location
        assert location1.id == location2.id

    def test_different_names_without_coordinates_create_multiple(self):
        """Testa que nomes diferentes sem coordenadas criam locations separadas."""
        data1 = {"name": "Brasil"}
        data2 = {"name": "Argentina"}

        serializer1 = LocationCreateSerializer(data=data1)
        serializer2 = LocationCreateSerializer(data=data2)

        assert serializer1.is_valid()
        assert serializer2.is_valid()

        location1 = serializer1.save()
        location2 = serializer2.save()

        assert location1.id != location2.id
        assert location1.name == "Brasil"
        assert location2.name == "Argentina"

    def test_create_with_null_coordinates(self):
        """Testa criação explícita com coordenadas null."""
        data = {"name": "Local", "latitude": None, "longitude": None}

        serializer = LocationCreateSerializer(data=data)
        assert serializer.is_valid()

        location = serializer.save()

        assert location.name == "Local"
        assert location.latitude is None
        assert location.longitude is None
