"""
Register serializer.
"""
from rest_framework import serializers
from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
        ]
    
    def validate_username(self, value):
        """Valida se o username já existe."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Este nome de usuário já está em uso.'
            )
        return value
    
    def validate_email(self, value):
        """Valida se o email já existe."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Este email já está em uso.'
            )
        return value
    
    def validate(self, data):
        """Valida se as senhas coincidem."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        return data
    
    def create(self, validated_data):
        """Cria usuário com senha encriptada."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
    