"""
Post serializers.
"""

from django.utils import timezone

from rest_framework import serializers

from posts.models import Post, PostMedia
from posts.serializers import (
    LocationCreateSerializer,
    LocationSerializer,
    PollSerializer,
    HashtagSerializer,
)
from users.serializers import UserSerializer
from posts.utils import extract_hashtags


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
    media = PostMediaSerializer(many=True, read_only=True)
    poll = PollSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    is_published = serializers.ReadOnlyField()
    stats = serializers.SerializerMethodField()
    is_retweeted = serializers.SerializerMethodField()
    hashtags = HashtagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "image",
            "media",
            "poll",
            "location",
            "hashtags",
            "scheduled_for",
            "is_published",
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
            "hashtags",
            "scheduled_for",
            "is_published",
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
            "views": obj.views_count,
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

    scheduled_for = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Data e hora para publicação agendada (formato ISO 8601)",
    )

    class Meta:
        model = Post
        fields = [
            "content",
            "image",
            "in_reply_to",
            "media_files",
            "location",
            "scheduled_for",
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

    def validate_scheduled_for(self, value):
        """
        Valida que scheduled_for não é no passado.
        """
        if value is not None:
            # Permitir pequena margem de erro (5 minutos no passado)
            min_time = timezone.now() - timezone.timedelta(minutes=5)

            if value < min_time:
                raise serializers.ValidationError(
                    "A data de agendamento não pode ser no passado."
                )

        return value

    def create(self, validated_data):
        """Cria post com mídias e location associadas se fornecida."""
        location_data = validated_data.pop("location", None)
        media_files = validated_data.pop("media_files", [])
        scheduled_for = validated_data.pop("scheduled_for", None)

        # Extrair hashtags do conteúdo
        content = validated_data.get('content', '')
        hashtag_names = extract_hashtags(content)

        # Criar post
        post = super().create(validated_data)

        # Definir scheduled_for se fornecido
        if scheduled_for is not None:
            post.scheduled_for = scheduled_for
            post.save(update_fields=["scheduled_for"])

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

        # Processar hashtags extraídas
        if hashtag_names:
            from posts.models import Hashtag
            
            hashtags = []
            for name in hashtag_names:
                # Reutilizar hashtag existente ou criar nova
                hashtag, created = Hashtag.objects.get_or_create(name=name)
                hashtags.append(hashtag)
                
                # Incrementar contador
                if not created:
                    hashtag.increment_count()
                else:
                    # Nova hashtag, definir contador = 1
                    hashtag.posts_count = 1
                    hashtag.save(update_fields=['posts_count'])
            
            # Associar hashtags ao post
            post.hashtags.set(hashtags)

        return post


class ScheduledPostSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para posts agendados.

    Usado no endpoint /api/posts/scheduled/ para listar
    posts que o usuário agendou.
    """

    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "scheduled_for",
            "is_published",
            "created_at",
        ]
        read_only_fields = ["id", "author", "is_published", "created_at"]
