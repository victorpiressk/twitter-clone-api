"""
Testes para os models do app posts.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

from posts.models import Comment, Like, Location, Poll, PollOption, PollVote, Post

User = get_user_model()


@pytest.mark.django_db
class TestPostModel:
    """Testes para o model Post."""

    def test_create_post(self):
        """Testa criação de post."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test post content")

        assert post.author == user
        assert post.content == "Test post content"
        assert not post.image

    def test_post_str(self):
        """Testa representação string do post."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(
            author=user,
            content="This is a very long content that should be "
            "truncated in the string representation",
        )

        post_str = str(post)
        assert "testuser" in post_str
        assert len(post_str) <= 60  # Username + 50 chars de conteúdo + ": "

    # TESTES - Retweets
    def test_create_retweet(self):
        """Testa criação de retweet."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original post")
        retweet = Post.objects.create(
            author=retweeter, content="", is_retweet=True, retweet_of=original_post
        )

        assert retweet.is_retweet is True
        assert retweet.retweet_of == original_post
        assert retweet.author == retweeter

    def test_create_quote_retweet(self):
        """Testa criação de quote retweet (retweet com comentário)."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original post")
        quote_retweet = Post.objects.create(
            author=retweeter,
            content="Concordo totalmente!",
            is_retweet=True,
            retweet_of=original_post,
        )

        assert quote_retweet.is_retweet is True
        assert quote_retweet.retweet_of == original_post
        assert quote_retweet.content == "Concordo totalmente!"

    def test_retweet_str(self):
        """Testa representação string de retweet."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original content")
        retweet = Post.objects.create(
            author=retweeter, content="", is_retweet=True, retweet_of=original_post
        )

        retweet_str = str(retweet)
        assert "retweeter" in retweet_str
        assert "retweetou" in retweet_str

    def test_retweets_count_default(self):
        """Testa que retweets_count começa em 0."""
        user = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        assert post.retweets_count == 0

    # TESTES - Replies
    def test_create_reply(self):
        """Testa criação de reply."""
        author = User.objects.create_user(username="author", password="pass123")
        replier = User.objects.create_user(username="replier", password="pass123")

        original_post = Post.objects.create(author=author, content="Original post")
        reply = Post.objects.create(
            author=replier, content="This is a reply", in_reply_to=original_post
        )

        assert reply.in_reply_to == original_post
        assert reply.author == replier
        assert reply.content == "This is a reply"

    def test_reply_to_reply(self):
        """Testa criar reply de um reply (thread)."""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        post_a = Post.objects.create(author=user1, content="Post A")
        post_b = Post.objects.create(
            author=user2, content="Reply to A", in_reply_to=post_a
        )
        post_c = Post.objects.create(
            author=user3, content="Reply to B", in_reply_to=post_b
        )

        assert post_c.in_reply_to == post_b
        assert post_b.in_reply_to == post_a
        assert post_a.in_reply_to is None

    def test_get_replies(self):
        """Testa buscar replies de um post."""
        author = User.objects.create_user(username="author", password="pass123")
        replier1 = User.objects.create_user(username="replier1", password="pass123")
        replier2 = User.objects.create_user(username="replier2", password="pass123")

        original = Post.objects.create(author=author, content="Original")

        reply1 = Post.objects.create(
            author=replier1, content="Reply 1", in_reply_to=original
        )
        reply2 = Post.objects.create(
            author=replier2, content="Reply 2", in_reply_to=original
        )

        replies = Post.objects.filter(in_reply_to=original)

        assert replies.count() == 2
        assert reply1 in replies
        assert reply2 in replies

    def test_post_likes_count(self):
        """Testa contagem de curtidas."""
        user = User.objects.create_user(username="author", password="pass123")
        user2 = User.objects.create_user(username="liker1", password="pass123")
        user3 = User.objects.create_user(username="liker2", password="pass123")

        post = Post.objects.create(author=user, content="Test")

        Like.objects.create(user=user2, post=post)
        Like.objects.create(user=user3, post=post)

        assert post.likes_count == 2

    def test_post_comments_count(self):
        """Testa contagem de comentários."""
        user = User.objects.create_user(username="author", password="pass123")
        user2 = User.objects.create_user(username="commenter", password="pass123")

        post = Post.objects.create(author=user, content="Test")

        Comment.objects.create(user=user2, post=post, content="Comment 1")
        Comment.objects.create(user=user2, post=post, content="Comment 2")
        Comment.objects.create(user=user2, post=post, content="Comment 3")

        assert post.comments_count == 3

    def test_post_content_max_length(self):
        """Testa limite de caracteres do conteúdo."""
        user = User.objects.create_user(username="testuser", password="pass123")
        content = "a" * 280  # Exatamente 280 caracteres

        post = Post.objects.create(author=user, content=content)

        assert len(post.content) == 280


@pytest.mark.django_db
class TestPostMediaModel:
    """Testes para o model PostMedia - MÚLTIPLAS MÍDIAS."""

    def test_create_post_media(self):
        """Testa criação de PostMedia."""
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile

        from PIL import Image

        from posts.models import PostMedia

        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test post")

        # Criar imagem fake
        file = BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(file, "JPEG")
        file.seek(0)
        test_image = SimpleUploadedFile(
            name="test.jpg", content=file.read(), content_type="image/jpeg"
        )

        media = PostMedia.objects.create(
            post=post, type="image", file=test_image, order=0
        )

        assert media.post == post
        assert media.type == "image"
        assert media.order == 0
        assert media.file is not None

    def test_post_media_str(self):
        """Testa representação string de PostMedia."""
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile

        from PIL import Image

        from posts.models import PostMedia

        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        file = BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(file, "JPEG")
        file.seek(0)
        test_image = SimpleUploadedFile(
            name="test.jpg", content=file.read(), content_type="image/jpeg"
        )

        media = PostMedia.objects.create(
            post=post, type="video", file=test_image, order=1
        )

        media_str = str(media)
        assert "Vídeo" in media_str or "Video" in media_str
        assert str(post.id) in media_str
        assert "1" in media_str  # ordem

    def test_post_media_ordering(self):
        """Testa ordenação de mídias por order e created_at."""
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile

        from PIL import Image

        from posts.models import PostMedia

        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        def create_test_image(name):
            file = BytesIO()
            image = Image.new("RGB", (100, 100), color="red")
            image.save(file, "JPEG")
            file.seek(0)
            return SimpleUploadedFile(
                name=name, content=file.read(), content_type="image/jpeg"
            )

        media2 = PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img2.jpg"), order=2
        )
        media1 = PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img1.jpg"), order=1
        )
        media3 = PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img3.jpg"), order=3
        )

        media_list = list(post.media.all())

        assert media_list[0] == media1
        assert media_list[1] == media2
        assert media_list[2] == media3


@pytest.mark.django_db
class TestCommentModel:
    """Testes para o model Comment."""

    def test_create_comment(self):
        """Testa criação de comentário."""
        author = User.objects.create_user(username="author", password="pass123")
        commenter = User.objects.create_user(username="commenter", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        comment = Comment.objects.create(
            user=commenter, post=post, content="Test comment"
        )

        assert comment.user == commenter
        assert comment.post == post
        assert comment.content == "Test comment"

    def test_comment_str(self):
        """Testa representação string do comentário."""
        author = User.objects.create_user(username="author", password="pass123")
        commenter = User.objects.create_user(username="commenter", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        comment = Comment.objects.create(
            user=commenter, post=post, content="Test comment"
        )

        comment_str = str(comment)
        assert "commenter" in comment_str
        assert "comentou" in comment_str or "comment" in comment_str.lower()


@pytest.mark.django_db
class TestLikeModel:
    """Testes para o model Like."""

    def test_create_like(self):
        """Testa criação de curtida."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        like = Like.objects.create(user=liker, post=post)

        assert like.user == liker
        assert like.post == post

    def test_like_str(self):
        """Testa representação string da curtida."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        like = Like.objects.create(user=liker, post=post)

        like_str = str(like)
        assert "liker" in like_str
        assert "curtiu" in like_str or "like" in like_str.lower()

    def test_unique_like(self):
        """Testa que não pode curtir o mesmo post 2 vezes."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        # Primeiro like
        Like.objects.create(user=liker, post=post)

        # Tentar criar duplicado
        with pytest.raises(Exception):
            Like.objects.create(user=liker, post=post)

    def test_user_can_like_multiple_posts(self):
        """Testa que usuário pode curtir vários posts diferentes."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")

        post1 = Post.objects.create(author=author, content="Post 1")
        post2 = Post.objects.create(author=author, content="Post 2")
        post3 = Post.objects.create(author=author, content="Post 3")

        Like.objects.create(user=liker, post=post1)
        Like.objects.create(user=liker, post=post2)
        Like.objects.create(user=liker, post=post3)

        assert Like.objects.filter(user=liker).count() == 3


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


@pytest.mark.django_db
class TestLocationModel:
    """Testes para o model Location."""

    def test_create_location_with_coordinates(self):
        """Testa criação de location com coordenadas."""
        location = Location.objects.create(
            name="Torre Eiffel, Paris",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )

        assert location.name == "Torre Eiffel, Paris"
        assert location.latitude == Decimal("48.858844")
        assert location.longitude == Decimal("2.294351")
        assert location.has_coordinates is True

    def test_create_location_without_coordinates(self):
        """Testa criação de location sem coordenadas."""
        location = Location.objects.create(name="Algum lugar")

        assert location.name == "Algum lugar"
        assert location.latitude is None
        assert location.longitude is None
        assert location.has_coordinates is False

    def test_location_str_with_coordinates(self):
        """Testa representação string com coordenadas."""
        location = Location.objects.create(
            name="São Paulo",
            latitude=Decimal("-23.550520"),
            longitude=Decimal("-46.633308"),
        )

        location_str = str(location)
        assert "São Paulo" in location_str
        assert "-23.550520" in location_str or "-23.55052" in location_str
        assert "-46.633308" in location_str or "-46.633308" in location_str

    def test_location_str_without_coordinates(self):
        """Testa representação string sem coordenadas."""
        location = Location.objects.create(name="Brasil")

        location_str = str(location)
        assert location_str == "Brasil"

    def test_location_has_coordinates_property(self):
        """Testa property has_coordinates."""
        loc1 = Location.objects.create(
            name="Com coordenadas", latitude=Decimal("10.0"), longitude=Decimal("20.0")
        )
        loc2 = Location.objects.create(name="Sem coordenadas")

        assert loc1.has_coordinates is True
        assert loc2.has_coordinates is False

    def test_location_unique_together_coordinates(self):
        """Testa constraint unique_together para coordenadas."""
        Location.objects.create(
            name="Local A", latitude=Decimal("48.858844"), longitude=Decimal("2.294351")
        )

        # Tentar criar location com mesmas coordenadas
        with pytest.raises(Exception):
            Location.objects.create(
                name="Local B",
                latitude=Decimal("48.858844"),
                longitude=Decimal("2.294351"),
            )

    def test_location_null_coordinates_allowed(self):
        """Testa que coordenadas null são permitidas."""
        loc1 = Location.objects.create(name="Local 1")
        loc2 = Location.objects.create(name="Local 2")

        # Ambos sem coordenadas devem ser permitidos
        assert loc1.latitude is None
        assert loc2.latitude is None

    def test_post_with_location(self):
        """Testa associação de location com post."""
        user = User.objects.create_user(username="testuser", password="pass123")
        location = Location.objects.create(
            name="Paris, França",
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
        )

        post = Post.objects.create(
            author=user, content="Visitando Paris!", location=location
        )

        assert post.location == location
        assert post.location.name == "Paris, França"

    def test_post_without_location(self):
        """Testa que post sem location é permitido."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Post sem localização")

        assert post.location is None

    def test_delete_location_set_null_on_post(self):
        """Testa que deletar location não deleta posts (SET_NULL)."""
        user = User.objects.create_user(username="testuser", password="pass123")
        location = Location.objects.create(name="Local temporário")

        post = Post.objects.create(
            author=user, content="Post com location", location=location
        )
        post_id = post.id

        # Deletar location
        location.delete()

        # Post deve continuar existindo, mas sem location
        post.refresh_from_db()
        assert post.id == post_id
        assert post.location is None

    def test_location_posts_relationship(self):
        """Testa relacionamento reverso location.posts."""
        user = User.objects.create_user(username="testuser", password="pass123")
        location = Location.objects.create(name="São Paulo")

        post1 = Post.objects.create(author=user, content="Post 1", location=location)
        post2 = Post.objects.create(author=user, content="Post 2", location=location)
        post3 = Post.objects.create(author=user, content="Post 3", location=location)

        assert location.posts.count() == 3
        assert post1 in location.posts.all()
        assert post2 in location.posts.all()
        assert post3 in location.posts.all()


@pytest.mark.django_db
class TestScheduledPostsModel:
    """Testes para posts agendados no model."""

    def test_create_post_without_scheduled_for(self):
        """Testa criação de post sem agendamento (publicado imediatamente)."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Post publicado agora")

        assert post.scheduled_for is None
        assert post.is_published is True

    def test_create_post_with_future_scheduled_for(self):
        """Testa criação de post agendado para o futuro."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future = timezone.now() + timedelta(hours=2)
        post = Post.objects.create(
            author=user, content="Post agendado", scheduled_for=future
        )

        assert post.scheduled_for is not None
        assert post.is_published is False

    def test_create_post_with_past_scheduled_for(self):
        """Testa post com scheduled_for no passado (já publicado)."""
        user = User.objects.create_user(username="testuser", password="pass123")

        past = timezone.now() - timedelta(hours=1)
        post = Post.objects.create(
            author=user, content="Post 'agendado' para o passado", scheduled_for=past
        )

        assert post.scheduled_for is not None
        assert post.is_published is True

    def test_is_published_property_with_null_scheduled_for(self):
        """Testa property is_published quando scheduled_for é None."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test")

        assert post.is_published is True

    def test_is_published_property_with_future_date(self):
        """Testa property is_published com data futura."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future = timezone.now() + timedelta(days=1)
        post = Post.objects.create(author=user, content="Test", scheduled_for=future)

        assert post.is_published is False

    def test_is_published_property_with_past_date(self):
        """Testa property is_published com data passada."""
        user = User.objects.create_user(username="testuser", password="pass123")

        past = timezone.now() - timedelta(hours=1)
        post = Post.objects.create(author=user, content="Test", scheduled_for=past)

        assert post.is_published is True

    def test_manager_published_returns_only_published(self):
        """Testa que Post.objects.published() retorna apenas posts publicados."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Post normal (publicado)
        post1 = Post.objects.create(author=user, content="Post 1")

        # Post agendado (futuro)
        future = timezone.now() + timedelta(hours=2)
        post2 = Post.objects.create(author=user, content="Post 2", scheduled_for=future)

        # Post com scheduled_for passado (publicado)
        past = timezone.now() - timedelta(hours=1)
        post3 = Post.objects.create(author=user, content="Post 3", scheduled_for=past)

        published = Post.objects.published()

        assert post1 in published
        assert post2 not in published  # Agendado (futuro)
        assert post3 in published
        assert published.count() == 2

    def test_manager_scheduled_returns_only_scheduled(self):
        """Testa que Post.objects.scheduled() retorna apenas posts agendados."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Post normal
        Post.objects.create(author=user, content="Post 1")

        # Post agendado (futuro)
        future = timezone.now() + timedelta(hours=2)
        post2 = Post.objects.create(author=user, content="Post 2", scheduled_for=future)

        # Post com scheduled_for passado
        past = timezone.now() - timedelta(hours=1)
        Post.objects.create(author=user, content="Post 3", scheduled_for=past)

        scheduled = Post.objects.scheduled()

        assert scheduled.count() == 1
        assert post2 in scheduled

    def test_manager_scheduled_with_multiple_future_posts(self):
        """Testa scheduled() com múltiplos posts futuros."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future1 = timezone.now() + timedelta(hours=1)
        future2 = timezone.now() + timedelta(hours=2)
        future3 = timezone.now() + timedelta(days=1)

        post1 = Post.objects.create(
            author=user, content="Post 1", scheduled_for=future1
        )
        post2 = Post.objects.create(
            author=user, content="Post 2", scheduled_for=future2
        )
        post3 = Post.objects.create(
            author=user, content="Post 3", scheduled_for=future3
        )

        scheduled = Post.objects.scheduled()

        assert scheduled.count() == 3
        assert post1 in scheduled
        assert post2 in scheduled
        assert post3 in scheduled

    def test_manager_published_excludes_future_posts(self):
        """Testa que published() exclui posts futuros."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Criar 5 posts futuros
        for i in range(5):
            future = timezone.now() + timedelta(hours=i + 1)
            Post.objects.create(
                author=user, content=f"Future post {i}", scheduled_for=future
            )

        # Criar 3 posts publicados
        for i in range(3):
            Post.objects.create(author=user, content=f"Published post {i}")

        assert Post.objects.all().count() == 8
        assert Post.objects.published().count() == 3
        assert Post.objects.scheduled().count() == 5
