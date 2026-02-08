"""
Post model - Postagens do sistema.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    """
    Modelo para postagens (tweets).

    Representa uma publicação feita por um usuário.
    Pode ser um post normal, um retweet de outro post, ou uma resposta a outro post.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="posts",
        on_delete=models.CASCADE,
        verbose_name="Autor",
    )

    content = models.TextField(
        max_length=280,
        verbose_name="Conteúdo",
        help_text="Conteúdo do post (máximo 280 caracteres)",
    )

    image = models.ImageField(
        upload_to="post_images/",
        blank=True,
        null=True,
        verbose_name="Imagem",
        help_text="Imagem anexada ao post (opcional)",
    )

    # Campos de Retweet
    is_retweet = models.BooleanField(
        default=False,
        verbose_name="É retweet",
        help_text="Indica se este post é um retweet de outro post",
    )

    retweet_of = models.ForeignKey(
        "self",
        related_name="retweets",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Retweet de",
        help_text="Post original sendo retweetado (se aplicável)",
    )

    retweets_count = models.IntegerField(
        default=0,
        verbose_name="Quantidade de retweets",
        help_text="Contador de quantas vezes este post foi retweetado",
    )

    # CAMPO - Reply
    in_reply_to = models.ForeignKey(
        "self",
        related_name="replies",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Em resposta a",
        help_text="Post ao qual este post está respondendo (se aplicável)",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "-created_at"]),
            models.Index(fields=["is_retweet"]),
            models.Index(fields=["retweet_of"]),
            models.Index(fields=["in_reply_to"]),  # NOVO ÍNDICE
        ]

    def __str__(self):
        if self.is_retweet and self.retweet_of:
            return f"{self.author.username} retweetou: {self.retweet_of.content[:50]}"
        return f"{self.author.username}: {self.content[:50]}"

    @property
    def likes_count(self):
        """Retorna quantidade de curtidas."""
        return self.likes.count()

    @property
    def comments_count(self):
        """Retorna quantidade de comentários."""
        return self.comments.count()


class Poll(models.Model):
    """
    Modelo para enquetes em posts.
    
    Um post pode ter uma enquete associada com múltiplas opções de voto.
    """
    
    post = models.OneToOneField(
        "Post",
        related_name="poll",
        on_delete=models.CASCADE,
        verbose_name="Post",
        help_text="Post ao qual esta enquete pertence"
    )
    
    question = models.CharField(
        max_length=280,
        blank=True,
        verbose_name="Pergunta",
        help_text="Pergunta da enquete (opcional, pode estar no conteúdo do post)"
    )
    
    duration_hours = models.IntegerField(
        default=24,
        verbose_name="Duração (horas)",
        help_text="Duração da enquete em horas (ex: 24, 168)"
    )
    
    ends_at = models.DateTimeField(
        verbose_name="Termina em",
        help_text="Data e hora de término da enquete"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    class Meta:
        verbose_name = "Enquete"
        verbose_name_plural = "Enquetes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["ends_at"]),
        ]
    
    def __str__(self):
        question_preview = self.question[:50] if self.question else f"Enquete do post {self.post.id}"
        return f"{question_preview} (termina em {self.ends_at.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def total_votes(self):
        """Retorna o total de votos na enquete."""
        return self.options.aggregate(models.Sum('votes'))['votes__sum'] or 0
    
    @property
    def is_ended(self):
        """Verifica se a enquete já terminou."""
        return timezone.now() > self.ends_at
    
    def save(self, *args, **kwargs):
        """Calcula ends_at baseado em duration_hours se não fornecido."""
        if not self.ends_at:
            self.ends_at = timezone.now() + timezone.timedelta(hours=self.duration_hours)
        super().save(*args, **kwargs)


class PollOption(models.Model):
    """
    Modelo para opções de voto em uma enquete.
    
    Cada enquete tem 2-4 opções para os usuários escolherem.
    """
    
    poll = models.ForeignKey(
        Poll,
        related_name="options",
        on_delete=models.CASCADE,
        verbose_name="Enquete"
    )
    
    text = models.CharField(
        max_length=100,
        verbose_name="Texto",
        help_text="Texto da opção de voto"
    )
    
    votes = models.IntegerField(
        default=0,
        verbose_name="Votos",
        help_text="Quantidade de votos nesta opção"
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição da opção"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    class Meta:
        verbose_name = "Opção de Enquete"
        verbose_name_plural = "Opções de Enquete"
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["poll", "order"]),
        ]
    
    def __str__(self):
        return f"{self.text} ({self.votes} votos)"
    
    @property
    def percentage(self):
        """Calcula a porcentagem de votos desta opção."""
        total = self.poll.total_votes
        if total == 0:
            return 0.0
        return round((self.votes / total) * 100, 1)


class PollVote(models.Model):
    """
    Modelo para registrar votos em enquetes.
    
    Garante que cada usuário só pode votar uma vez por enquete.
    """
    
    poll = models.ForeignKey(
        Poll,
        related_name="poll_votes",
        on_delete=models.CASCADE,
        verbose_name="Enquete"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="poll_votes",
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )
    
    option = models.ForeignKey(
        PollOption,
        related_name="user_votes",
        on_delete=models.CASCADE,
        verbose_name="Opção"
    )
    
    voted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Votado em"
    )
    
    class Meta:
        verbose_name = "Voto em Enquete"
        verbose_name_plural = "Votos em Enquetes"
        ordering = ["-voted_at"]
        unique_together = ("poll", "user")
        indexes = [
            models.Index(fields=["poll", "user"]),
            models.Index(fields=["option"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} votou em '{self.option.text}'"