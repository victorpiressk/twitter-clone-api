from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

from posts.models import Poll, PollOption, PollVote, Post

User = get_user_model()


@pytest.mark.django_db
class TestPollModel:
    """Testes para o model Poll."""

    def test_create_poll(self):
        """Testa criação de poll."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test post")

        poll = Poll.objects.create(
            post=post, question="Qual sua linguagem favorita?", duration_hours=24
        )

        assert poll.post == post
        assert poll.question == "Qual sua linguagem favorita?"
        assert poll.duration_hours == 24
        assert poll.ends_at is not None

    def test_poll_auto_calculate_ends_at(self):
        """Testa que ends_at é calculado automaticamente."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        now = timezone.now()
        poll = Poll.objects.create(post=post, question="Test poll", duration_hours=48)

        # ends_at deve ser ~48 horas no futuro
        expected_end = now + timedelta(hours=48)
        time_diff = abs((poll.ends_at - expected_end).total_seconds())

        # Permitir diferença de até 5 segundos
        assert time_diff < 5

    def test_poll_str(self):
        """Testa representação string da poll."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        poll = Poll.objects.create(
            post=post, question="Test question", duration_hours=24
        )

        poll_str = str(poll)
        assert "Test question" in poll_str
        assert "termina em" in poll_str.lower()

    def test_poll_total_votes_property(self):
        """Testa property total_votes."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        # Criar opções com votos
        PollOption.objects.create(poll=poll, text="Opção 1", votes=10, order=0)
        PollOption.objects.create(poll=poll, text="Opção 2", votes=5, order=1)

        assert poll.total_votes == 15

    def test_poll_total_votes_zero(self):
        """Testa total_votes quando não há votos."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        assert poll.total_votes == 0

    def test_poll_is_ended_false(self):
        """Testa is_ended quando poll ainda está ativa."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        poll = Poll.objects.create(post=post, duration_hours=24)

        assert poll.is_ended is False

    def test_poll_is_ended_true(self):
        """Testa is_ended quando poll já terminou."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Criar poll que terminou ontem
        past_time = timezone.now() - timedelta(hours=24)
        poll = Poll.objects.create(post=post, duration_hours=1, ends_at=past_time)

        assert poll.is_ended is True

    def test_poll_one_to_one_with_post(self):
        """Testa relação OneToOne entre Poll e Post."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        poll = Poll.objects.create(post=post, duration_hours=24)

        # Acessar poll através do post
        assert post.poll == poll

        # Não pode criar segunda poll para o mesmo post
        with pytest.raises(Exception):
            Poll.objects.create(post=post, duration_hours=24)


@pytest.mark.django_db
class TestPollOptionModel:
    """Testes para o model PollOption."""

    def test_create_poll_option(self):
        """Testa criação de poll option."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        assert option.poll == poll
        assert option.text == "Python"
        assert option.votes == 0
        assert option.order == 0

    def test_poll_option_str(self):
        """Testa representação string da option."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        option = PollOption.objects.create(
            poll=poll, text="JavaScript", votes=5, order=0
        )

        option_str = str(option)
        assert "JavaScript" in option_str
        assert "5 votos" in option_str

    def test_poll_option_percentage_with_votes(self):
        """Testa cálculo de porcentagem."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        opt1 = PollOption.objects.create(poll=poll, text="Opt 1", votes=30, order=0)
        opt2 = PollOption.objects.create(poll=poll, text="Opt 2", votes=70, order=1)

        assert opt1.percentage == 30.0
        assert opt2.percentage == 70.0

    def test_poll_option_percentage_no_votes(self):
        """Testa porcentagem quando não há votos."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        option = PollOption.objects.create(poll=poll, text="Opt", order=0)

        assert option.percentage == 0.0

    def test_poll_option_ordering(self):
        """Testa ordenação de opções por order."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)

        opt2 = PollOption.objects.create(poll=poll, text="Second", order=2)
        opt1 = PollOption.objects.create(poll=poll, text="First", order=1)
        opt3 = PollOption.objects.create(poll=poll, text="Third", order=3)

        options = list(poll.options.all())

        assert options[0] == opt1
        assert options[1] == opt2
        assert options[2] == opt3


@pytest.mark.django_db
class TestPollVoteModel:
    """Testes para o model PollVote."""

    def test_create_poll_vote(self):
        """Testa criação de voto."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        vote = PollVote.objects.create(poll=poll, user=user, option=option)

        assert vote.poll == poll
        assert vote.user == user
        assert vote.option == option
        assert vote.voted_at is not None

    def test_poll_vote_str(self):
        """Testa representação string do voto."""
        user = User.objects.create_user(username="voter", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="JavaScript", order=0)

        vote = PollVote.objects.create(poll=poll, user=user, option=option)

        vote_str = str(vote)
        assert "voter" in vote_str
        assert "JavaScript" in vote_str
        assert "votou" in vote_str

    def test_poll_vote_unique_together(self):
        """Testa que usuário não pode votar duas vezes."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        opt1 = PollOption.objects.create(poll=poll, text="Opt 1", order=0)
        opt2 = PollOption.objects.create(poll=poll, text="Opt 2", order=1)

        # Primeiro voto
        PollVote.objects.create(poll=poll, user=user, option=opt1)

        # Tentar votar novamente (mesmo que em opção diferente)
        with pytest.raises(Exception):
            PollVote.objects.create(poll=poll, user=user, option=opt2)

    def test_multiple_users_can_vote(self):
        """Testa que múltiplos usuários podem votar."""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        post = Post.objects.create(author=user1, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Python", order=0)

        PollVote.objects.create(poll=poll, user=user1, option=option)
        PollVote.objects.create(poll=poll, user=user2, option=option)
        PollVote.objects.create(poll=poll, user=user3, option=option)

        assert PollVote.objects.filter(poll=poll).count() == 3

    def test_delete_poll_cascades_votes(self):
        """Testa que deletar poll deleta votos associados."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")
        poll = Poll.objects.create(post=post, duration_hours=24)
        option = PollOption.objects.create(poll=poll, text="Opt", order=0)

        vote = PollVote.objects.create(poll=poll, user=user, option=option)
        vote_id = vote.id

        # Deletar poll
        poll.delete()

        # Voto deve ter sido deletado também
        assert not PollVote.objects.filter(id=vote_id).exists()
