"""
Login serializer.
"""

from django.contrib.auth import authenticate

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuários.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        """Valida credenciais do usuário."""
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    "Credenciais inválidas.", code="authorization"
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    "Conta desativada.", code="authorization"
                )
        else:
            raise serializers.ValidationError(
                "Username e senha são obrigatórios.", code="authorization"
            )

        data["user"] = user
        return data
