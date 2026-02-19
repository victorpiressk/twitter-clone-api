from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework import status

from posts.models import (
    Poll,
    PollOption,
    PollVote,
    Post,
)


@pytest.mark.django_db
class TestPollViewSet:
    """Testes para o PollViewSet."""

    def test_list_polls(self, api_client, user):
        """Testa listagem de polls."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        PollOption.objects.create(poll=poll, text="Opt 1", order=0)
        PollOption.objects.create(poll=poll, text="Opt 2", order=1)

        url = reverse("poll-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_retrieve_poll(self, api_client, user):
        """Testa obter detalhes de uma poll."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(
            post=post, question="Test question", duration_hours=24
        )
        PollOption.objects.create(poll=poll, text="Python", order=0)
        PollOption.objects.create(poll=poll, text="JavaScript", order=1)

        url = reverse("poll-detail", kwargs={"pk": poll.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["question"] == "Test question"
        assert len(response.data["options"]) == 2

    def test_vote_in_poll(self, authenticated_client, user):
        """Testa votar em uma poll."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})
        response = authenticated_client.post(url, {"option_id": option.id})

        assert response.status_code == status.HTTP_200_OK

        # Verificar que voto foi registrado
        assert PollVote.objects.filter(poll=poll, user=user, option=option).exists()

        # Verificar que contador foi incrementado
        option.refresh_from_db()
        assert option.votes == 1

        # Verificar resposta contém user_voted_option_id
        assert response.data["user_voted_option_id"] == option.id

    def test_vote_unauthenticated(self, api_client, user):
        """Testa votar sem autenticação."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})
        response = api_client.post(url, {"option_id": option.id})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_vote_twice_fails(self, authenticated_client, user):
        """Testa que não pode votar duas vezes."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        opt1 = PollOption.objects.create(poll=poll, text="Opt 1", order=0)
        opt2 = PollOption.objects.create(poll=poll, text="Opt 2", order=1)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})

        # Primeiro voto
        response = authenticated_client.post(url, {"option_id": opt1.id})
        assert response.status_code == status.HTTP_200_OK

        # Segundo voto (deve falhar)
        response = authenticated_client.post(url, {"option_id": opt2.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já votou" in str(response.data).lower()

    def test_vote_ended_poll_fails(self, authenticated_client, user):
        """Testa voto em poll encerrada."""
        post = Post.objects.create(author=user, content="Test")

        # Poll que terminou ontem
        past_time = timezone.now() - timedelta(hours=24)
        poll = Poll.objects.create(post=post, duration_hours=1, ends_at=past_time)
        option = PollOption.objects.create(poll=poll, text="Opt", order=0)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})
        response = authenticated_client.post(url, {"option_id": option.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "encerrada" in str(response.data).lower()

    def test_vote_invalid_option(self, authenticated_client, user):
        """Testa voto com option_id inválido."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        url = reverse("poll-vote", kwargs={"pk": poll.pk})
        response = authenticated_client.post(url, {"option_id": 99999})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_poll_results(self, api_client, user):
        """Testa obter resultados de uma poll."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        PollOption.objects.create(poll=poll, text="Opt 1", votes=30, order=0)
        PollOption.objects.create(poll=poll, text="Opt 2", votes=70, order=1)

        url = reverse("poll-results", kwargs={"pk": poll.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_votes"] == 100
        assert len(response.data["options"]) == 2
        assert response.data["options"][0]["percentage"] == 30.0
        assert response.data["options"][1]["percentage"] == 70.0

    def test_unvote_poll(self, authenticated_client, user):
        """Testa desfazer voto."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", votes=5, order=0)

        # Criar voto
        PollVote.objects.create(poll=poll, user=user, option=option)

        url = reverse("poll-unvote", kwargs={"pk": poll.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que voto foi deletado
        assert not PollVote.objects.filter(poll=poll, user=user).exists()

        # Verificar que contador foi decrementado
        option.refresh_from_db()
        assert option.votes == 4

    def test_unvote_not_voted(self, authenticated_client, user):
        """Testa desfazer voto quando não votou."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        url = reverse("poll-unvote", kwargs={"pk": poll.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "não votou" in str(response.data).lower()

    def test_unvote_ended_poll_fails(self, authenticated_client, user):
        """Testa que não pode desfazer voto em poll encerrada."""
        post = Post.objects.create(author=user, content="Test")

        past_time = timezone.now() - timedelta(hours=24)
        poll = Poll.objects.create(post=post, duration_hours=1, ends_at=past_time)
        option = PollOption.objects.create(poll=poll, text="Opt", order=0)

        # Criar voto
        PollVote.objects.create(poll=poll, user=user, option=option)

        url = reverse("poll-unvote", kwargs={"pk": poll.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "encerrada" in str(response.data).lower()


@pytest.mark.django_db
class TestPostWithPoll:
    """Testes para criação de posts com polls."""

    def test_create_post_with_poll(self, authenticated_client, user):
        """Testa criar post com poll."""
        url = reverse("post-list")

        data = {
            "content": "Qual sua linguagem favorita?",
            "poll": {
                "question": "",
                "duration_hours": 24,
                "options": ["Python", "JavaScript", "Go", "Rust"],
            },
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verificar que post foi criado
        post = Post.objects.get(id=response.data["id"])
        assert post.content == "Qual sua linguagem favorita?"

        # Verificar que poll foi criada
        assert hasattr(post, "poll")
        assert post.poll.duration_hours == 24
        assert post.poll.options.count() == 4

    def test_create_post_with_poll_minimum_options(self, authenticated_client, user):
        """Testa criar poll com mínimo de opções (2)."""
        url = reverse("post-list")

        data = {
            "content": "Concordam?",
            "poll": {"duration_hours": 24, "options": ["Sim", "Não"]},
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.poll.options.count() == 2

    def test_create_post_with_poll_invalid_options(self, authenticated_client, user):
        """Testa criar poll com número inválido de opções."""
        url = reverse("post-list")

        # Menos de 2 opções
        data = {
            "content": "Test",
            "poll": {"duration_hours": 24, "options": ["Única opção"]},
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Mais de 4 opções
        data["poll"]["options"] = ["A", "B", "C", "D", "E"]

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_post_with_poll_duplicate_options(self, authenticated_client, user):
        """Testa criar poll com opções duplicadas."""
        url = reverse("post-list")

        data = {
            "content": "Test",
            "poll": {
                "duration_hours": 24,
                "options": ["Python", "JavaScript", "Python", "Go"],
            },
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "duplicadas" in str(response.data).lower()

    def test_create_post_without_poll(self, authenticated_client, user):
        """Testa que post normal ainda funciona."""
        url = reverse("post-list")

        data = {"content": "Post sem poll"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert not hasattr(post, "poll")

    def test_get_post_with_poll(self, api_client, user):
        """Testa que GET /posts/ retorna poll."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        PollOption.objects.create(poll=poll, text="Opt 1", order=0)
        PollOption.objects.create(poll=poll, text="Opt 2", order=1)

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "poll" in response.data
        assert response.data["poll"] is not None
        assert len(response.data["poll"]["options"]) == 2

    def test_list_posts_includes_polls(self, api_client, user):
        """Testa que listagem de posts inclui polls."""
        post = Post.objects.create(author=user, content="Test with poll")
        poll = Poll.objects.create(post=post, duration_hours=24)
        PollOption.objects.create(poll=poll, text="Opt", order=0)

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        post_data = response.data["results"][0]
        assert "poll" in post_data
        assert post_data["poll"] is not None

    def test_delete_post_cascades_poll(self, authenticated_client, user):
        """Testa que deletar post deleta poll associada."""
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        poll_id = poll.id

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Poll deve ter sido deletada
        assert not Poll.objects.filter(id=poll_id).exists()
