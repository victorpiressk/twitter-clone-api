"""
Register serializer.
"""

from datetime import date
from rest_framework import serializers

from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.
    """

    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    birth_date = serializers.DateField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "birth_date",
        ]

    def validate_username(self, value):
        """Valida se o username já existe."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def validate_email(self, value):
        """Valida se o email já existe."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value

    def validate(self, data):
        """Valida se as senhas coincidem."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem."}
            )
        return data
    
    def validate_birth_date(self, value):
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

    def create(self, validated_data):
        """Cria usuário com senha encriptada."""
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user
