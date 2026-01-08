"""
Posts admin configuration.
"""
from django.contrib import admin
from posts.models import Post, Comment, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Configuração do Post no admin."""
    
    list_display = ['id', 'author', 'content_preview', 'created_at', 'likes_count', 'comments_count']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'likes_count', 'comments_count']
    
    def content_preview(self, obj):
        """Mostra preview do conteúdo."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Conteúdo'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Configuração do Comment no admin."""
    
    list_display = ['id', 'user', 'post', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        """Mostra preview do conteúdo."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Conteúdo'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Configuração do Like no admin."""
    
    list_display = ['id', 'user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    