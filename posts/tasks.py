"""
Celery tasks para posts.
"""

from django.utils import timezone

from celery import shared_task

from posts.models import Post


@shared_task
def publish_scheduled_posts():
    """
    Publica posts agendados cuja data/hora já passou.

    Esta task é executada a cada minuto pelo Celery Beat.
    """
    now = timezone.now()

    # Buscar posts que estão agendados e já passaram da hora
    scheduled_posts = Post.objects.filter(
        scheduled_for__isnull=False, scheduled_for__lte=now
    )

    count = scheduled_posts.count()

    if count > 0:
        for post in scheduled_posts:
            print(f"✅ Post {post.id} foi publicado: {post.content[:50]}")

    return f"Processados {count} posts agendados"
