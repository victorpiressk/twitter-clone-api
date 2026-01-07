"""
Comment serializer.
"""
from rest_framework import serializers
from posts.models import Comment
from users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer para comentários.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'post',
            'content',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_content(self, value):
        """Valida se o conteúdo não está vazio."""
        if not value.strip():
            raise serializers.ValidationError(
                'O conteúdo não pode estar vazio.'
            )
        return value
    