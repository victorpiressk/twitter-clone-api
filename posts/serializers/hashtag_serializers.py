"""
Serializers para Hashtag.
"""

from rest_framework import serializers

from posts.models import Hashtag


class HashtagSerializer(serializers.ModelSerializer):
    """
    Serializer para exibição de hashtags.

    Usado para mostrar hashtags nos posts e em listagens.
    """

    class Meta:
        model = Hashtag
        fields = ["id", "name", "slug", "posts_count", "created_at"]
        read_only_fields = ["id", "slug", "posts_count", "created_at"]
