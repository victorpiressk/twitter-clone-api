"""
Modelo Hashtag.
"""

from django.db import models
from django.utils.text import slugify


class Hashtag(models.Model):
    """
    Hashtag extraída de posts.
    
    Ex: "Adorei #python e #django!" → cria hashtags 'python' e 'django'
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Nome",
        help_text="Nome da hashtag (sem #, ex: 'python')"
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Slug",
        help_text="Versão normalizada da hashtag"
    )
    
    posts_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Contagem de posts",
        help_text="Número de posts que usam esta hashtag"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    class Meta:
        verbose_name = "Hashtag"
        verbose_name_plural = "Hashtags"
        ordering = ["-posts_count", "name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["-posts_count"]),  # Para trending
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return f"#{self.name} ({self.posts_count} posts)"
    
    def save(self, *args, **kwargs):
        """Auto-gera slug ao salvar."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def increment_count(self):
        """Incrementa contador de posts (thread-safe)."""
        from django.db.models import F
        Hashtag.objects.filter(pk=self.pk).update(posts_count=F('posts_count') + 1)
        self.refresh_from_db(fields=['posts_count'])
    
    def decrement_count(self):
        """Decrementa contador de posts (thread-safe)."""
        from django.db.models import F
        Hashtag.objects.filter(pk=self.pk).update(posts_count=F('posts_count') - 1)
        self.refresh_from_db(fields=['posts_count'])
