from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from rest_framework import status

from posts.models import Post

User = get_user_model()


@pytest.mark.django_db
class TestPostRepliesActions:
    """Testes para actions de replies do PostViewSet."""

    def test_create_reply(self, authenticated_client, user, another_user):
        """Testa criar reply de um post."""
        original = Post.objects.create(author=another_user, content="Original post")

        url = reverse("post-list")
        response = authenticated_client.post(
            url,
            {"content": "This is a reply", "in_reply_to": original.id},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        reply = Post.objects.get(author=user, in_reply_to=original)
        assert reply.content == "This is a reply"

    def test_get_replies_of_post(self, api_client, user):
        """Testa buscar replies de um post."""
        original = Post.objects.create(author=user, content="Original")

        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        reply1 = Post.objects.create(
            author=user2, content="Reply 1", in_reply_to=original
        )
        reply2 = Post.objects.create(
            author=user3, content="Reply 2", in_reply_to=original
        )

        url = reverse("post-replies", kwargs={"pk": original.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        reply_ids = [r["id"] for r in response.data]
        assert reply1.id in reply_ids
        assert reply2.id in reply_ids

    def test_get_thread(self, api_client):
        """Testa buscar thread completa."""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        # Criar thread: A -> B -> C
        post_a = Post.objects.create(author=user1, content="Post A")
        post_b = Post.objects.create(
            author=user2, content="Reply to A", in_reply_to=post_a
        )
        post_c = Post.objects.create(
            author=user3, content="Reply to B", in_reply_to=post_b
        )

        # Buscar thread a partir do post C
        url = reverse("post-thread", kwargs={"pk": post_c.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

        # Verifica ordem: A, B, C
        assert response.data[0]["id"] == post_a.id
        assert response.data[1]["id"] == post_b.id
        assert response.data[2]["id"] == post_c.id

    def test_get_thread_single_post(self, api_client, user):
        """Testa thread de post sem ancestrais."""
        post = Post.objects.create(author=user, content="Single post")

        url = reverse("post-thread", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == post.id

    def test_replies_empty(self, api_client, user):
        """Testa que post sem replies retorna lista vazia."""
        post = Post.objects.create(author=user, content="No replies")

        url = reverse("post-replies", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_reply_to_reply(self, authenticated_client, user, another_user):
        """Testa criar reply de um reply."""
        post_a = Post.objects.create(author=another_user, content="Post A")
        post_b = Post.objects.create(
            author=another_user, content="Reply to A", in_reply_to=post_a
        )

        url = reverse("post-list")
        response = authenticated_client.post(
            url, {"content": "Reply to B", "in_reply_to": post_b.id}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED

        reply = Post.objects.get(author=user, content="Reply to B")
        assert reply.in_reply_to == post_b
