"""
Post serializers.
"""

from rest_framework import serializers

from posts.models import Post
from users.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer para exibição de posts.
    """

    author = UserSerializer(read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "image",
            "likes_count",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de posts.
    """

    class Meta:
        model = Post
        fields = [
            "content",
            "image",
        ]

    def validate_content(self, value):
        """Valida se o conteúdo não está vazio."""
        if not value.strip():
            raise serializers.ValidationError("O conteúdo não pode estar vazio.")
        return value
