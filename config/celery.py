"""
Configuração do Celery.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Define o settings padrão do Django para o Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("twitter_clone")

# Usa string para não precisar serializar objetos
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-descobre tasks em todos os apps instalados
app.autodiscover_tasks()

# Configurar beat schedule diretamente aqui
app.conf.beat_schedule = {
    "check-scheduled-posts-every-minute": {
        "task": "posts.tasks.publish_scheduled_posts",
        "schedule": crontab(minute="*"),  # A cada minuto
    },
}

app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    """Task de debug."""
    print(f"Request: {self.request!r}")
