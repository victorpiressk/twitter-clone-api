"""
Login serializer.
"""

from django.contrib.auth import authenticate

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuários.
    """

    identifier = serializers.CharField()  # username, email ou phone
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        """Valida credenciais do usuário."""
        identifier = data.get("identifier")
        password = data.get("password")

        if not identifier or not password:
            raise serializers.ValidationError(
                "Identificador e senha são obrigatórios."
            )

        # Detecta tipo e busca usuário
        from django.db.models import Q
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.filter(
            Q(username=identifier) |
            Q(email=identifier) |
            Q(phone=identifier)
        ).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError(
                "Credenciais inválidas.", code="authorization"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Conta desativada.", code="authorization"
            )

        data["user"] = user
        return data