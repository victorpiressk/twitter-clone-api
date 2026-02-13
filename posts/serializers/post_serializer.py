"""
Post serializers.
"""

from rest_framework import serializers

from posts.models import Post, PostMedia
from posts.serializers import (
    LocationCreateSerializer,
    LocationSerializer,
    PollSerializer,
)
from users.serializers import UserSerializer


# NOVO SERIALIZER - PostMedia
class PostMediaSerializer(serializers.ModelSerializer):
    """
    Serializer para mídias de posts.
    """

    url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = [
            "id",
            "type",
            "url",
            "thumbnail",
            "order",
        ]
        read_only_fields = ["id", "url", "thumbnail"]

    def get_url(self, obj):
        """Retorna URL completa do arquivo."""
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer para exibição de posts.
    """

    author = UserSerializer(read_only=True)

    # Múltiplas mídias
    media = PostMediaSerializer(many=True, read_only=True)

    # Enquete (se existir)
    poll = PollSerializer(read_only=True)

    # Stats como objeto aninhado
    stats = serializers.SerializerMethodField()

    # Estado de interação do usuário
    is_retweeted = serializers.SerializerMethodField()

    location = LocationSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "image",  # Mantido por compatibilidade
            "media",
            "poll",
            "location",
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
            "media",
            "poll",
            "location",
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

    # Upload de múltiplas mídias
    media_files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
        max_length=4,  # Máximo 4 mídias
        help_text="Lista de arquivos de mídia (máximo 4)",
    )

    # Campo para criar/anexar location
    location = LocationCreateSerializer(
        required=False, allow_null=True, help_text="Dados da localização (opcional)"
    )

    class Meta:
        model = Post
        fields = [
            "content",
            "image",  # Mantido por compatibilidade
            "in_reply_to",
            "media_files",
            "location",
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

    def validate_media_files(self, value):
        """Valida arquivos de mídia."""
        if not value:
            return value

        # Máximo 4 arquivos
        if len(value) > 4:
            raise serializers.ValidationError(
                "Você pode enviar no máximo 4 arquivos de mídia."
            )

        # Validar tamanho de cada arquivo
        max_size_image = 5 * 1024 * 1024  # 5MB
        max_size_video = 50 * 1024 * 1024  # 50MB

        for file in value:
            # Verificar tipo de arquivo
            content_type = file.content_type

            if content_type.startswith("image/"):
                if file.size > max_size_image:
                    raise serializers.ValidationError(
                        "Imagem muito grande. Tamanho máximo: 5MB"
                    )
            elif content_type.startswith("video/"):
                if file.size > max_size_video:
                    raise serializers.ValidationError(
                        "Vídeo muito grande. Tamanho máximo: 50MB"
                    )
            else:
                raise serializers.ValidationError(
                    f"Tipo de arquivo não suportado: {content_type}"
                )

        return value

    def create(self, validated_data):
        """Cria post com mídias e location associadas se fornecida."""
        location_data = validated_data.pop("location", None)
        media_files = validated_data.pop("media_files", [])

        # Criar post
        post = super().create(validated_data)

        # Criar/associar location se fornecida
        if location_data:
            location_serializer = LocationCreateSerializer(data=location_data)
            location_serializer.is_valid(raise_exception=True)
            location = location_serializer.save()
            post.location = location
            post.save(update_fields=["location"])

        # Criar mídias se fornecidas
        if media_files:
            for index, file in enumerate(media_files):
                # Determinar tipo de mídia
                content_type = file.content_type
                if content_type.startswith("image/gif"):
                    media_type = "gif"
                elif content_type.startswith("image/"):
                    media_type = "image"
                elif content_type.startswith("video/"):
                    media_type = "video"
                else:
                    media_type = "image"  # fallback

                PostMedia.objects.create(
                    post=post, type=media_type, file=file, order=index
                )

        return post
