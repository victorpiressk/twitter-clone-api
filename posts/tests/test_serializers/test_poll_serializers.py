from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest
from rest_framework.test import APIRequestFactory

from posts.models import Poll, PollOption, PollVote, Post
from posts.serializers import (
    PollCreateSerializer,
    PollOptionSerializer,
    PollResultsSerializer,
    PollSerializer,
    PollVoteSerializer,
)

User = get_user_model()


@pytest.mark.django_db
class TestPollOptionSerializer:
    """Testes para PollOptionSerializer."""

    def test_serialize_poll_option(self):
        """Testa serialização de poll option."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        option = PollOption.objects.create(poll=poll, text="Python", votes=10, order=0)

        serializer = PollOptionSerializer(option)
        data = serializer.data

        assert data["text"] == "Python"
        assert data["votes"] == 10
        assert data["order"] == 0
        assert "percentage" in data

    def test_percentage_field_readonly(self):
        """Testa que percentage é read-only."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        opt1 = PollOption.objects.create(poll=poll, text="Opt 1", votes=30, order=0)
        PollOption.objects.create(poll=poll, text="Opt 2", votes=70, order=1)

        serializer = PollOptionSerializer(opt1)
        data = serializer.data

        assert data["percentage"] == 30.0


@pytest.mark.django_db
class TestPollSerializer:
    """Testes para PollSerializer."""

    def test_serialize_poll(self):
        """Testa serialização de poll."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        poll = Poll.objects.create(
            post=post, question="Qual sua linguagem favorita?", duration_hours=24
        )

        PollOption.objects.create(poll=poll, text="Python", order=0)
        PollOption.objects.create(poll=poll, text="JavaScript", order=1)

        serializer = PollSerializer(poll)
        data = serializer.data

        assert data["question"] == "Qual sua linguagem favorita?"
        assert data["duration_hours"] == 24
        assert "ends_at" in data
        assert "options" in data
        assert len(data["options"]) == 2
        assert "total_votes" in data
        assert "is_ended" in data

    def test_user_voted_option_id_authenticated(self):
        """Testa user_voted_option_id quando usuário votou."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        opt1 = PollOption.objects.create(poll=poll, text="Python", order=0)
        PollOption.objects.create(poll=poll, text="JavaScript", order=1)

        # Usuário vota na opção 1
        PollVote.objects.create(poll=poll, user=user, option=opt1)

        # Criar request mock
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        serializer = PollSerializer(poll, context={"request": request})
        data = serializer.data

        assert data["user_voted_option_id"] == opt1.id

    def test_user_voted_option_id_not_voted(self):
        """Testa user_voted_option_id quando usuário não votou."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        PollOption.objects.create(poll=poll, text="Python", order=0)

        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        serializer = PollSerializer(poll, context={"request": request})
        data = serializer.data

        assert data["user_voted_option_id"] is None

    def test_user_voted_option_id_unauthenticated(self):
        """Testa user_voted_option_id quando não autenticado."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        PollOption.objects.create(poll=poll, text="Python", order=0)

        serializer = PollSerializer(poll)
        data = serializer.data

        assert data["user_voted_option_id"] is None


@pytest.mark.django_db
class TestPollCreateSerializer:
    """Testes para PollCreateSerializer."""

    def test_create_poll_valid(self):
        """Testa criação de poll com dados válidos."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        data = {
            "question": "Qual sua linguagem favorita?",
            "duration_hours": 24,
            "options": ["Python", "JavaScript", "Go", "Rust"],
        }

        serializer = PollCreateSerializer(data=data, context={"post": post})
        assert serializer.is_valid()

        poll = serializer.save()

        assert poll.question == "Qual sua linguagem favorita?"
        assert poll.duration_hours == 24
        assert poll.options.count() == 4

    def test_create_poll_minimum_options(self):
        """Testa criação com mínimo de opções (2)."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        data = {"duration_hours": 24, "options": ["Sim", "Não"]}

        serializer = PollCreateSerializer(data=data, context={"post": post})
        assert serializer.is_valid()

        poll = serializer.save()
        assert poll.options.count() == 2

    def test_create_poll_maximum_options(self):
        """Testa criação com máximo de opções (4)."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        data = {"duration_hours": 48, "options": ["A", "B", "C", "D"]}

        serializer = PollCreateSerializer(data=data, context={"post": post})
        assert serializer.is_valid()

        poll = serializer.save()
        assert poll.options.count() == 4

    def test_create_poll_too_few_options(self):
        """Testa criação com menos de 2 opções (inválido)."""
        data = {"duration_hours": 24, "options": ["Apenas uma opção"]}

        serializer = PollCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "options" in serializer.errors

    def test_create_poll_too_many_options(self):
        """Testa criação com mais de 4 opções (inválido)."""
        data = {"duration_hours": 24, "options": ["A", "B", "C", "D", "E"]}

        serializer = PollCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "options" in serializer.errors

    def test_create_poll_duplicate_options(self):
        """Testa criação com opções duplicadas (inválido)."""
        data = {
            "duration_hours": 24,
            "options": ["Python", "JavaScript", "Python", "Go"],
        }

        serializer = PollCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "options" in serializer.errors
        assert "duplicadas" in str(serializer.errors["options"][0]).lower()

    def test_create_poll_invalid_duration(self):
        """Testa criação com duração inválida."""
        # Duração menor que 1 hora
        data = {"duration_hours": 0, "options": ["Sim", "Não"]}

        serializer = PollCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "duration_hours" in serializer.errors

        # Duração maior que 168 horas (7 dias)
        data["duration_hours"] = 200

        serializer = PollCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "duration_hours" in serializer.errors

    def test_create_poll_options_ordering(self):
        """Testa que opções são criadas na ordem correta."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        data = {"duration_hours": 24, "options": ["First", "Second", "Third"]}

        serializer = PollCreateSerializer(data=data, context={"post": post})
        assert serializer.is_valid()

        poll = serializer.save()
        options = list(poll.options.all())

        assert options[0].text == "First"
        assert options[0].order == 0
        assert options[1].text == "Second"
        assert options[1].order == 1
        assert options[2].text == "Third"
        assert options[2].order == 2


@pytest.mark.django_db
class TestPollVoteSerializer:
    """Testes para PollVoteSerializer."""

    def test_vote_valid(self):
        """Testa validação de voto válido."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        factory = APIRequestFactory()
        request = factory.post("/")
        request.user = user

        data = {"option_id": option.id}

        serializer = PollVoteSerializer(data=data, context={"request": request})
        assert serializer.is_valid()

    def test_vote_invalid_option(self):
        """Testa voto com option_id inválido."""
        user = User.objects.create_user(username="testuser", password="pass123")

        factory = APIRequestFactory()
        request = factory.post("/")
        request.user = user

        data = {"option_id": 99999}

        serializer = PollVoteSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "option_id" in serializer.errors

    def test_vote_poll_ended(self):
        """Testa voto em poll encerrada."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Poll que terminou ontem
        past_time = timezone.now() - timedelta(hours=24)
        poll = Poll.objects.create(post=post, duration_hours=1, ends_at=past_time)
        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        factory = APIRequestFactory()
        request = factory.post("/")
        request.user = user

        data = {"option_id": option.id}

        serializer = PollVoteSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "encerrada" in str(serializer.errors["non_field_errors"][0]).lower()

    def test_vote_already_voted(self):
        """Testa voto quando usuário já votou."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        opt1 = PollOption.objects.create(poll=poll, text="Python", order=0)
        opt2 = PollOption.objects.create(poll=poll, text="JavaScript", order=1)

        # Usuário já votou
        PollVote.objects.create(poll=poll, user=user, option=opt1)

        factory = APIRequestFactory()
        request = factory.post("/")
        request.user = user

        # Tentar votar novamente
        data = {"option_id": opt2.id}

        serializer = PollVoteSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "já votou" in str(serializer.errors["non_field_errors"][0]).lower()


@pytest.mark.django_db
class TestPollResultsSerializer:
    """Testes para PollResultsSerializer."""

    def test_serialize_results(self):
        """Testa serialização de resultados."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, question="Test poll", duration_hours=24)

        PollOption.objects.create(poll=poll, text="Opt 1", votes=30, order=0)
        PollOption.objects.create(poll=poll, text="Opt 2", votes=70, order=1)

        serializer = PollResultsSerializer(poll)
        data = serializer.data

        assert data["question"] == "Test poll"
        assert "ends_at" in data
        assert len(data["options"]) == 2
        assert data["total_votes"] == 100
        assert "is_ended" in data

        # Verificar porcentagens
        assert data["options"][0]["percentage"] == 30.0
        assert data["options"][1]["percentage"] == 70.0
