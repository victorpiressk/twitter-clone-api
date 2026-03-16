"""
User serializers.
"""

from datetime import date

from PIL import Image
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para exibição de usuário.
    """

    # ✨ NOVO: Stats como objeto aninhado
    stats = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "profile_image",
            "banner",
            "location",
            "website",
            "birth_date",
            "stats",  # objeto aninhado
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "stats"]

    def get_stats(self, obj):
        """Retorna estatísticas do usuário como objeto."""
        return {
            "posts": obj.posts_count,
            "following": obj.following_count,
            "followers": obj.followers_count,
        }

    def _validate_image(self, image_file, max_size_mb=5):
        # Validação de tamanho
        if image_file.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"Imagem muito grande. Máximo: {max_size_mb}MB"
            )

        # Validação de formato — apenas pela extensão/content_type
        # Não usar Image.open() pois conflita com Cloudinary storage
        allowed_content_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        content_type = getattr(image_file, "content_type", "")
        if content_type and content_type not in allowed_content_types:
            raise serializers.ValidationError(
                f"Formato não aceito. Use JPEG, PNG ou WEBP."
            )

    def validate_profile_image(self, value):
        if value:
            self._validate_image(value, max_size_mb=5)
        return value

    def validate_banner(self, value):
        if value:
            self._validate_image(value, max_size_mb=5)
        return value

    def validate_profile_image(self, value):
        if value:
            self._validate_image(
                value, max_size_mb=2
            )  # Ex: Limite diferente para avatar
        return value

    def validate_website(self, value):
        """Valida formato da URL do website."""
        if value and not value.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                "URL deve começar com http:// ou https://"
            )
        return value

    def validate_birth_date(self, value):
        """Valida idade mínima de 13 anos."""
        if value:
            today = date.today()
            age = (
                today.year
                - value.year
                - ((today.month, today.day) < (value.month, value.day))
            )

            if age < 13:
                raise serializers.ValidationError(
                    "Você deve ter pelo menos 13 anos para se cadastrar."
                )

            if value > today:
                raise serializers.ValidationError(
                    "Data de nascimento não pode ser no futuro."
                )

        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de usuário.
    """

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        ]

    def validate(self, data):
        """Valida se as senhas coincidem."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem."}
            )
        return data

    def create(self, validated_data):
        """Cria usuário com senha encriptada."""
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user
