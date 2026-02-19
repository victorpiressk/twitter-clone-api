from django.contrib.auth import get_user_model

import pytest

from posts.models import Like, Notification, Post
from users.models import Follow

User = get_user_model()


@pytest.mark.django_db
class TestNotificationModel:
    """Testes para o model Notification."""

    def test_create_notification(self):
        """Testa criação de notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Test")

        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="like", post=post
        )

        assert notification.recipient == alice
        assert notification.actor == bob
        assert notification.notification_type == "like"
        assert notification.post == post
        assert notification.is_read is False

    def test_notification_str_representation(self):
        """Testa representação string."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Test")

        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="like", post=post
        )

        assert str(notification) == "bob → alice: Curtida"

    def test_mark_as_read(self):
        """Testa método mark_as_read()."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="follow"
        )

        assert notification.is_read is False

        notification.mark_as_read()
        assert notification.is_read is True

    def test_notification_types(self):
        """Testa todos os tipos de notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Test")

        types = ["like", "retweet", "reply", "follow", "mention"]

        for notif_type in types:
            notification = Notification.objects.create(
                recipient=alice,
                actor=bob,
                notification_type=notif_type,
                post=post if notif_type != "follow" else None,
            )
            assert notification.notification_type == notif_type

    def test_notification_without_post(self):
        """Testa notificação sem post (follow)."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="follow", post=None
        )

        assert notification.post is None

    def test_notification_unique_together(self):
        """Testa unique_together evita duplicatas."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Test")

        # Criar primeira notificação
        Notification.objects.create(
            recipient=alice, actor=bob, notification_type="like", post=post
        )

        # Tentar criar duplicata
        with pytest.raises(Exception):
            Notification.objects.create(
                recipient=alice, actor=bob, notification_type="like", post=post
            )

    def test_notification_ordering(self):
        """Testa ordenação por -created_at."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        notif1 = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="follow"
        )

        notif2 = Notification.objects.create(
            recipient=alice,
            actor=bob,
            notification_type="mention",
            post=Post.objects.create(author=bob, content="Test"),
        )

        notifications = Notification.objects.all()

        # Mais recente primeiro
        assert notifications[0] == notif2
        assert notifications[1] == notif1


@pytest.mark.django_db
class TestNotificationSignals:
    """Testes para signals que criam notificações."""

    def test_like_creates_notification(self):
        """Testa que curtida cria notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Test")

        # Curtir post
        Like.objects.create(user=bob, post=post)

        # Verificar notificação
        notification = Notification.objects.get(
            recipient=alice, actor=bob, notification_type="like", post=post
        )

        assert notification is not None
        assert notification.is_read is False

    def test_reply_creates_notification(self):
        """Testa que resposta cria notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Original")

        # Responder post
        reply = Post.objects.create(author=bob, content="Resposta", in_reply_to=post)

        # Verificar notificação
        notification = Notification.objects.get(
            recipient=alice, actor=bob, notification_type="reply", post=reply
        )

        assert notification is not None

    def test_retweet_creates_notification(self):
        """Testa que retweet cria notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Original")

        # Retweet
        Post.objects.create(author=bob, content="", is_retweet=True, retweet_of=post)

        # Verificar notificação
        notification = Notification.objects.get(
            recipient=alice, actor=bob, notification_type="retweet", post=post
        )

        assert notification is not None

    def test_follow_creates_notification(self):
        """Testa que follow cria notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        # Seguir
        Follow.objects.create(follower=bob, following=alice)

        # Verificar notificação
        notification = Notification.objects.get(
            recipient=alice, actor=bob, notification_type="follow"
        )

        assert notification is not None
        assert notification.post is None

    def test_mention_creates_notification(self):
        """Testa que menção cria notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        # Post com menção
        post = Post.objects.create(author=bob, content="Olá @alice, tudo bem?")

        # Verificar notificação
        notification = Notification.objects.get(
            recipient=alice, actor=bob, notification_type="mention", post=post
        )

        assert notification is not None

    def test_self_like_no_notification(self):
        """Testa que curtir próprio post NÃO cria notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        post = Post.objects.create(author=alice, content="Test")

        # Curtir próprio post
        Like.objects.create(user=alice, post=post)

        # Não deve criar notificação
        assert (
            Notification.objects.filter(
                recipient=alice, actor=alice, notification_type="like"
            ).count()
            == 0
        )

    def test_self_reply_no_notification(self):
        """Testa que responder próprio post NÃO cria notificação."""
        alice = User.objects.create_user(username="alice", password="pass")
        post = Post.objects.create(author=alice, content="Original")

        # Responder próprio post
        Post.objects.create(author=alice, content="Resposta", in_reply_to=post)

        # Não deve criar notificação
        assert (
            Notification.objects.filter(
                recipient=alice, actor=alice, notification_type="reply"
            ).count()
            == 0
        )

    def test_self_mention_no_notification(self):
        """Testa que mencionar a si mesmo NÃO cria notificação."""
        alice = User.objects.create_user(username="alice", password="pass")

        # Post mencionando a si mesmo
        Post.objects.create(author=alice, content="Olá @alice")

        # Não deve criar notificação
        assert (
            Notification.objects.filter(
                recipient=alice, actor=alice, notification_type="mention"
            ).count()
            == 0
        )

    def test_mention_nonexistent_user_no_notification(self):
        """Testa que mencionar usuário inexistente não cria notificação."""
        bob = User.objects.create_user(username="bob", password="pass")

        # Mencionar usuário que não existe
        Post.objects.create(author=bob, content="Olá @usernaoinexistente")

        # Não deve criar notificação
        assert Notification.objects.filter(notification_type="mention").count() == 0

    def test_multiple_mentions_creates_multiple_notifications(self):
        """Testa que múltiplas menções criam múltiplas notificações."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        charlie = User.objects.create_user(username="charlie", password="pass")

        # Post mencionando duas pessoas
        post = Post.objects.create(author=charlie, content="Olá @alice e @bob!")

        # Verificar duas notificações
        assert (
            Notification.objects.filter(notification_type="mention", post=post).count()
            == 2
        )

        # Verificar que alice recebeu
        assert Notification.objects.filter(
            recipient=alice, actor=charlie, notification_type="mention"
        ).exists()

        # Verificar que bob recebeu
        assert Notification.objects.filter(
            recipient=bob, actor=charlie, notification_type="mention"
        ).exists()
