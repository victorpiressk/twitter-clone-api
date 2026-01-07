"""
Like serializer.
"""
from rest_framework import serializers
from posts.models import Like


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer para curtidas.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Like
        fields = [
            'id',
            'user',
            'post',
            'user_username',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']
        