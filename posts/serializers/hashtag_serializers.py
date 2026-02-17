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

    # Campo dinâmico que aparece quando há annotation
    recent_posts_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Hashtag
        fields = [
            "id",
            "name",
            "slug",
            "posts_count",
            "recent_posts_count",
            "created_at"
        ]
        read_only_fields = ["id", "slug", "posts_count", "created_at"]
