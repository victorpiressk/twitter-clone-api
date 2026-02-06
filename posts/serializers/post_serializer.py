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

    # Stats como objeto aninhado
    stats = serializers.SerializerMethodField()

    # Estado de interação do usuário
    is_retweeted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "image",
            "is_retweet",
            "retweet_of",
            "in_reply_to",
            "stats",
            "is_retweeted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "is_retweet",
            "retweets_count",
            "stats",
            "is_retweeted",
            "created_at",
            "updated_at",
        ]

    def get_stats(self, obj):
        """Retorna estatísticas do post como objeto."""
        return {
            "comments": obj.comments_count,
            "retweets": obj.retweets_count,
            "likes": obj.likes_count,
            "views": 0,  # Será implementado depois
        }

    def get_is_retweeted(self, obj):
        """Verifica se o usuário autenticado retweetou este post."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Post.objects.filter(
                author=request.user, is_retweet=True, retweet_of=obj
            ).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de posts.
    """

    # Campo opcional para reply
    in_reply_to = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Post
        fields = [
            "content",
            "image",
            "in_reply_to",
        ]

    def validate_content(self, value):
        """Valida se o conteúdo não está vazio."""
        if not value.strip():
            raise serializers.ValidationError("O conteúdo não pode estar vazio.")
        return value

    def validate_in_reply_to(self, value):
        """Valida que o post pai existe."""
        if value and not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post pai não existe.")
        return value
