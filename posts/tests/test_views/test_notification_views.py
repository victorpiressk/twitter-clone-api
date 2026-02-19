from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from rest_framework import status

from posts.models import Notification, Post

User = get_user_model()


@pytest.mark.django_db
class TestNotificationViewSet:
    """Testes para NotificationViewSet."""

    def test_list_notifications_authenticated(self, authenticated_client, user):
        """Testa listagem de notificações."""
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=user, content="Test")

        # Criar notificação
        Notification.objects.create(
            recipient=user, actor=bob, notification_type="like", post=post
        )

        url = reverse("notification-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["actor"]["username"] == "bob"

    def test_list_notifications_unauthenticated(self, api_client):
        """Testa que não autenticado não pode listar notificações."""
        url = reverse("notification-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_only_sees_own_notifications(self, authenticated_client, user):
        """Testa que usuário só vê próprias notificações."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        # Notificação para alice (não deve aparecer para user)
        notif_alice = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="follow"
        )

        # Notificação para user (deve aparecer)
        notif_user = Notification.objects.create(
            recipient=user, actor=bob, notification_type="follow"
        )

        url = reverse("notification-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Deve retornar apenas 1 notificação (a do user)
        assert len(response.data["results"]) == 1

        # Verificar que é a notificação correta pelo ID
        assert response.data["results"][0]["id"] == notif_user.id

        # Verificar que a notificação de alice NÃO aparece
        notification_ids = [n["id"] for n in response.data["results"]]
        assert notif_alice.id not in notification_ids

    def test_unread_notifications_endpoint(self, authenticated_client, user):
        """Testa endpoint de notificações não lidas."""
        bob = User.objects.create_user(username="bob", password="pass")

        # Criar notificação não lida
        Notification.objects.create(
            recipient=user, actor=bob, notification_type="follow", is_read=False
        )

        # Criar notificação lida
        Notification.objects.create(
            recipient=user,
            actor=bob,
            notification_type="mention",
            post=Post.objects.create(author=bob, content="Test"),
            is_read=True,
        )

        url = reverse("notification-unread")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["is_read"] is False

    def test_unread_count_endpoint(self, authenticated_client, user):
        """Testa endpoint de contador de não lidas."""
        bob = User.objects.create_user(username="bob", password="pass")

        # Criar 3 notificações não lidas
        for _ in range(3):
            Notification.objects.create(
                recipient=user, actor=bob, notification_type="follow"
            )

        # Criar 2 lidas
        for _ in range(2):
            Notification.objects.create(
                recipient=user, actor=bob, notification_type="follow", is_read=True
            )

        url = reverse("notification-unread-count")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_mark_notification_as_read(self, authenticated_client, user):
        """Testa marcar notificação como lida."""
        bob = User.objects.create_user(username="bob", password="pass")

        notification = Notification.objects.create(
            recipient=user, actor=bob, notification_type="follow", is_read=False
        )

        url = reverse("notification-read", kwargs={"pk": notification.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_read"] is True

        # Verificar no banco
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_cannot_mark_others_notification_as_read(self, authenticated_client, user):
        """Testa que não pode marcar notificação de outro usuário."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")

        # Notificação de alice
        notification = Notification.objects.create(
            recipient=alice, actor=bob, notification_type="follow"
        )

        # user (autenticado) tenta marcar notificação de alice
        url = reverse("notification-read", kwargs={"pk": notification.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_read_all_notifications(self, authenticated_client, user):
        """Testa marcar todas as notificações como lidas."""
        bob = User.objects.create_user(username="bob", password="pass")

        # Criar 5 notificações não lidas
        for _ in range(5):
            Notification.objects.create(
                recipient=user, actor=bob, notification_type="follow", is_read=False
            )

        url = reverse("notification-read-all")
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["updated"] == 5

        # Verificar que todas foram marcadas
        assert Notification.objects.filter(recipient=user, is_read=False).count() == 0

    def test_notification_ordering(self, authenticated_client, user):
        """Testa ordenação (não lidas primeiro, depois por data)."""
        bob = User.objects.create_user(username="bob", password="pass")

        # Criar notificação lida (antiga)
        notif1 = Notification.objects.create(
            recipient=user, actor=bob, notification_type="follow", is_read=True
        )

        # Criar notificação não lida (mais recente)
        notif2 = Notification.objects.create(
            recipient=user,
            actor=bob,
            notification_type="mention",
            post=Post.objects.create(author=bob, content="Test"),
            is_read=False,
        )

        url = reverse("notification-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Não lida deve vir primeiro
        results = response.data["results"]
        assert results[0]["id"] == notif2.id
        assert results[1]["id"] == notif1.id
