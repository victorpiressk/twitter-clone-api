"""
Location serializer.
"""

from rest_framework import serializers

from posts.models import Location


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer para localizações.
    """

    has_coordinates = serializers.ReadOnlyField()

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "has_coordinates",
        ]
        read_only_fields = ["id", "has_coordinates"]


class LocationCreateSerializer(serializers.Serializer):
    """
    Serializer para criação/busca de localizações.

    Aceita dados de localização e retorna ou cria um Location.
    Reutiliza locations com mesmas coordenadas (unique_together).
    """

    name = serializers.CharField(
        max_length=200, help_text="Nome da localização (ex: 'Paris, França')"
    )

    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
        min_value=-90,
        max_value=90,
        help_text="Latitude (-90 a 90)",
    )

    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
        min_value=-180,
        max_value=180,
        help_text="Longitude (-180 a 180)",
    )

    def validate(self, data):
        """
        Valida que latitude e longitude vêm juntas.
        """
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # Se um foi fornecido, o outro também deve ser
        if (latitude is not None) != (longitude is not None):
            raise serializers.ValidationError(
                "Latitude e longitude devem ser fornecidas juntas ou ambas omitidas."
            )

        return data

    def create(self, validated_data):
        """
        Cria ou retorna Location existente.

        Se coordenadas forem fornecidas, busca por location com
        mesmas coordenadas (unique_together). Caso contrário,
        busca por nome exato.
        """
        latitude = validated_data.get("latitude")
        longitude = validated_data.get("longitude")
        name = validated_data["name"]

        if latitude is not None and longitude is not None:
            # Buscar por coordenadas (unique_together)
            location, created = Location.objects.get_or_create(
                latitude=latitude, longitude=longitude, defaults={"name": name}
            )
        else:
            # Buscar por nome exato ou criar novo
            location, created = Location.objects.get_or_create(
                name=name, defaults={"latitude": None, "longitude": None}
            )

        return location
