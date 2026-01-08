"""
Follow serializer.
"""
from rest_framework import serializers
from users.models import Follow


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer para sistema de seguir.
    """
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)
    
    class Meta:
        model = Follow
        fields = [
            'id',
            'follower',
            'following',
            'follower_username',
            'following_username',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """Valida se usuário não está tentando seguir a si mesmo."""
        if data['follower'] == data['following']:
            raise serializers.ValidationError(
                'Você não pode seguir a si mesmo.'
            )
        return data
    