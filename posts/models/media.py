"""
PostMedia model - Mídias anexadas a posts.
"""

from django.db import models


class PostMedia(models.Model):
    """
    Modelo para mídias anexadas a posts.

    Suporta múltiplas imagens, vídeos e GIFs por post.
    """

    MEDIA_TYPES = [
        ("image", "Imagem"),
        ("video", "Vídeo"),
        ("gif", "GIF"),
    ]

    post = models.ForeignKey(
        "Post",
        related_name="media",
        on_delete=models.CASCADE,
        verbose_name="Post",
        help_text="Post ao qual esta mídia pertence",
    )

    type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPES,
        verbose_name="Tipo de mídia",
        help_text="Tipo do arquivo (imagem, vídeo ou GIF)",
    )

    file = models.FileField(
        upload_to="post_media/",
        verbose_name="Arquivo",
        help_text="Arquivo de mídia (imagem, vídeo ou GIF)",
    )

    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
        null=True,
        verbose_name="Thumbnail",
        help_text="Miniatura do vídeo (gerada automaticamente)",
    )

    order = models.IntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição da mídia no post",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Mídia do Post"
        verbose_name_plural = "Mídias dos Posts"
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["post", "order"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.post.id} (ordem: {self.order})"
