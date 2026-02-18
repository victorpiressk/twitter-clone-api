"""
Testes para os serializers do app posts.
"""
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest
from rest_framework.test import APIRequestFactory

from posts.models import (
    Comment,
    Hashtag,
    Like,
    Location,
    Poll,
    PollOption,
    PollVote,
    Post,
    Notification,
    PostMedia,
)
from posts.serializers import (
    CommentSerializer,
    HashtagSerializer,
    LikeSerializer,
    LocationCreateSerializer,
    LocationSerializer,
    PollCreateSerializer,
    PollOptionSerializer,
    PollResultsSerializer,
    PollSerializer,
    PollVoteSerializer,
    PostCreateSerializer,
    PostSerializer,
    ScheduledPostSerializer,
    NotificationSerializer,
    PostMediaSerializer
)

User = get_user_model()


@pytest.mark.django_db
class TestPostSerializer:
    """Testes para o PostSerializer."""

    def test_serialize_post(self):
        """Testa serialização de post."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test post content")

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["content"] == "Test post content"
        assert data["author"]["username"] == "author"
        assert "created_at" in data

    # TESTE - Stats como objeto
    def test_serialize_post_stats_object(self):
        """Testa que stats é retornado como objeto."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test")

        serializer = PostSerializer(post)
        data = serializer.data

        assert "stats" in data
        assert isinstance(data["stats"], dict)
        assert data["stats"]["comments"] == 0
        assert data["stats"]["retweets"] == 0
        assert data["stats"]["likes"] == 0
        assert data["stats"]["views"] == 0

    def test_serialize_post_with_counts(self):
        """Testa serialização com contadores."""
        author = User.objects.create_user(username="author", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        user3 = User.objects.create_user(username="user3", password="pass123")

        post = Post.objects.create(author=author, content="Test")

        # Criar likes e comments
        Like.objects.create(user=user2, post=post)
        Like.objects.create(user=user3, post=post)
        Comment.objects.create(user=user2, post=post, content="Comment 1")
        Comment.objects.create(user=user3, post=post, content="Comment 2")
        Comment.objects.create(user=user3, post=post, content="Comment 3")

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["stats"]["likes"] == 2
        assert data["stats"]["comments"] == 3

    # TESTES - Retweets
    def test_serialize_retweet(self):
        """Testa serialização de retweet."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original")
        retweet = Post.objects.create(
            author=retweeter, content="", is_retweet=True, retweet_of=original_post
        )

        serializer = PostSerializer(retweet)
        data = serializer.data

        assert data["is_retweet"] is True
        assert data["retweet_of"] == original_post.id
        assert data["author"]["username"] == "retweeter"

    def test_serialize_quote_retweet(self):
        """Testa serialização de quote retweet."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original")
        quote_retweet = Post.objects.create(
            author=retweeter,
            content="Concordo!",
            is_retweet=True,
            retweet_of=original_post,
        )

        serializer = PostSerializer(quote_retweet)
        data = serializer.data

        assert data["is_retweet"] is True
        assert data["retweet_of"] == original_post.id
        assert data["content"] == "Concordo!"

    def test_is_retweeted_true(self):
        """Testa que is_retweeted retorna True se usuário retweetou."""
        author = User.objects.create_user(username="author", password="pass123")
        retweeter = User.objects.create_user(username="retweeter", password="pass123")

        original_post = Post.objects.create(author=author, content="Original")

        # Criar retweet
        Post.objects.create(
            author=retweeter, content="", is_retweet=True, retweet_of=original_post
        )

        # Criar request mock com usuário autenticado
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = retweeter

        serializer = PostSerializer(original_post, context={"request": request})
        data = serializer.data

        assert data["is_retweeted"] is True

    def test_is_retweeted_false(self):
        """Testa que is_retweeted retorna False se usuário não retweetou."""
        author = User.objects.create_user(username="author", password="pass123")
        user = User.objects.create_user(username="user", password="pass123")

        post = Post.objects.create(author=author, content="Test")

        # Criar request mock com usuário autenticado
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        serializer = PostSerializer(post, context={"request": request})
        data = serializer.data

        assert data["is_retweeted"] is False

    def test_retweets_count_in_stats(self):
        """Testa que retweets_count aparece em stats."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test")

        # Manualmente incrementar contador
        post.retweets_count = 5
        post.save()

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["stats"]["retweets"] == 5

    # TESTES - Replies
    def test_serialize_reply(self):
        """Testa serialização de reply."""
        author = User.objects.create_user(username="author", password="pass123")
        replier = User.objects.create_user(username="replier", password="pass123")

        original = Post.objects.create(author=author, content="Original")
        reply = Post.objects.create(
            author=replier, content="This is a reply", in_reply_to=original
        )

        serializer = PostSerializer(reply)
        data = serializer.data

        assert data["in_reply_to"] == original.id
        assert data["content"] == "This is a reply"
        assert data["author"]["username"] == "replier"

    def test_serialize_post_without_reply(self):
        """Testa que in_reply_to é None para posts normais."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Normal post")

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["in_reply_to"] is None


@pytest.mark.django_db
class TestPostMediaSerializer:
    """Testes para PostMediaSerializer - MÚLTIPLAS MÍDIAS."""

    def test_serialize_post_with_media(self):
        """Testa serialização de post com mídias."""
        

        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Post with media")

        def create_test_image(name):
            file = BytesIO()
            image = Image.new("RGB", (100, 100), color="red")
            image.save(file, "JPEG")
            file.seek(0)
            return SimpleUploadedFile(
                name=name, content=file.read(), content_type="image/jpeg"
            )

        PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img1.jpg"), order=0
        )
        PostMedia.objects.create(
            post=post, type="image", file=create_test_image("img2.jpg"), order=1
        )

        serializer = PostSerializer(post)
        data = serializer.data

        assert "media" in data
        assert len(data["media"]) == 2
        assert data["media"][0]["type"] == "image"
        assert data["media"][0]["order"] == 0
        assert "url" in data["media"][0]

    def test_media_url_generation(self):
        """Testa geração de URL da mídia."""
        

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
            post=post, type="image", file=test_image, order=0
        )

        # Criar request mock para context
        factory = APIRequestFactory()
        request = factory.get("/")

        serializer = PostMediaSerializer(media, context={"request": request})
        data = serializer.data

        assert "url" in data
        assert data["url"] is not None


@pytest.mark.django_db
class TestPostCreateSerializer:
    """Testes para o PostCreateSerializer."""

    def test_create_post_valid(self):
        """Testa criação de post com dados válidos."""
        data = {"content": "New post content"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_post_empty_content(self):
        """Testa criação com conteúdo vazio."""
        data = {"content": "   "}  # Apenas espaços

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "content" in serializer.errors

    def test_create_post_missing_content(self):
        """Testa criação sem conteúdo."""
        data = {}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "content" in serializer.errors

    # TESTES - Replies no create
    def test_create_reply_valid(self):
        """Testa criação de reply com in_reply_to válido."""
        author = User.objects.create_user(username="author", password="pass123")
        original = Post.objects.create(author=author, content="Original")

        data = {"content": "This is a reply", "in_reply_to": original.id}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_reply_invalid_post(self):
        """Testa que in_reply_to com post inexistente retorna erro."""
        data = {
            "content": "Reply to nothing",
            "in_reply_to": 99999,  # Post que não existe
        }

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "in_reply_to" in serializer.errors

    def test_create_post_without_reply(self):
        """Testa que in_reply_to é opcional."""
        data = {"content": "Normal post"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()
        assert (
            "in_reply_to" not in serializer.validated_data
            or serializer.validated_data.get("in_reply_to") is None
        )

    # TESTES - Múltiplas Mídias (Validações)
    def test_validate_media_files_max_4(self):
        """Testa validação de máximo 4 mídias."""

        def create_test_image(name):
            file = BytesIO()
            image = Image.new("RGB", (100, 100), color="red")
            image.save(file, "JPEG")
            file.seek(0)
            return SimpleUploadedFile(
                name=name, content=file.read(), content_type="image/jpeg"
            )

        # 5 imagens (excede limite)
        media_files = [create_test_image(f"img{i}.jpg") for i in range(5)]

        data = {"content": "Post with too many images", "media_files": media_files}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "media_files" in serializer.errors
        assert "4" in str(serializer.errors["media_files"][0])

    def test_validate_image_size(self):
        """Testa validação de tamanho de imagem (máx 5MB)."""

        # Imagem de 6MB (excede limite)
        large_content = b"0" * (6 * 1024 * 1024)
        large_image = SimpleUploadedFile(
            name="large.jpg", content=large_content, content_type="image/jpeg"
        )

        data = {"content": "Post with large image", "media_files": [large_image]}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "media_files" in serializer.errors
        assert "5MB" in str(serializer.errors["media_files"][0])

    def test_validate_video_size(self):
        """Testa validação de tamanho de vídeo (máx 50MB)."""

        # Vídeo de 60MB (excede limite)
        large_content = b"0" * (60 * 1024 * 1024)
        large_video = SimpleUploadedFile(
            name="large.mp4", content=large_content, content_type="video/mp4"
        )

        data = {"content": "Post with large video", "media_files": [large_video]}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "media_files" in serializer.errors
        assert "50MB" in str(serializer.errors["media_files"][0])

    def test_validate_unsupported_file_type(self):
        """Testa validação de tipo de arquivo não suportado."""

        txt_file = SimpleUploadedFile(
            name="document.txt", content=b"Hello world", content_type="text/plain"
        )

        data = {"content": "Post with txt file", "media_files": [txt_file]}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "media_files" in serializer.errors
        assert "suportado" in str(serializer.errors["media_files"][0]).lower()


@pytest.mark.django_db
class TestCommentSerializer:
    """Testes para o CommentSerializer."""

    def test_serialize_comment(self):
        """Testa serialização de comentário."""
        author = User.objects.create_user(username="author", password="pass123")
        commenter = User.objects.create_user(username="commenter", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        comment = Comment.objects.create(
            user=commenter, post=post, content="Test comment"
        )

        serializer = CommentSerializer(comment)
        data = serializer.data

        assert data["content"] == "Test comment"
        assert data["user"]["username"] == "commenter"
        assert data["post"] == post.id
        assert "created_at" in data

    def test_create_comment_valid(self):
        """Testa criação de comentário válido."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        data = {"post": post.id, "content": "New comment"}

        serializer = CommentSerializer(data=data)
        assert serializer.is_valid()

    def test_create_comment_empty_content(self):
        """Testa criação com conteúdo vazio."""
        author = User.objects.create_user(username="author", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        data = {"post": post.id, "content": "   "}

        serializer = CommentSerializer(data=data)
        assert not serializer.is_valid()
        assert "content" in serializer.errors


@pytest.mark.django_db
class TestLikeSerializer:
    """Testes para o LikeSerializer."""

    def test_serialize_like(self):
        """Testa serialização de like."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        like = Like.objects.create(user=liker, post=post)

        serializer = LikeSerializer(like)
        data = serializer.data

        assert data["user"] == liker.id
        assert data["post"] == post.id
        assert data["user_username"] == "liker"
        assert "created_at" in data

    def test_create_like_valid(self):
        """Testa validação de like válido."""
        author = User.objects.create_user(username="author", password="pass123")
        liker = User.objects.create_user(username="liker", password="pass123")
        post = Post.objects.create(author=author, content="Test post")

        data = {"user": liker.id, "post": post.id}

        serializer = LikeSerializer(data=data)
        assert serializer.is_valid()

        # Nota: Na prática, o user é definido pelo viewset (request.user)
        # Aqui só validamos que os dados são válidos


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


@pytest.mark.django_db
class TestLocationSerializer:
    """Testes para LocationSerializer."""

    def test_serialize_location_with_coordinates(self):
        """Testa serialização de location com coordenadas."""
        location = Location.objects.create(
            name="Torre Eiffel, Paris",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )

        serializer = LocationSerializer(location)
        data = serializer.data

        assert data["name"] == "Torre Eiffel, Paris"
        assert data["latitude"] == "48.858844"
        assert data["longitude"] == "2.294351"
        assert data["has_coordinates"] is True

    def test_serialize_location_without_coordinates(self):
        """Testa serialização de location sem coordenadas."""
        location = Location.objects.create(name="Brasil")

        serializer = LocationSerializer(location)
        data = serializer.data

        assert data["name"] == "Brasil"
        assert data["latitude"] is None
        assert data["longitude"] is None
        assert data["has_coordinates"] is False

    def test_has_coordinates_field_readonly(self):
        """Testa que has_coordinates é read-only."""
        location = Location.objects.create(
            name="Local", latitude=Decimal("10.0"), longitude=Decimal("20.0")
        )

        serializer = LocationSerializer(location)
        assert "has_coordinates" in serializer.data
        assert serializer.data["has_coordinates"] is True


@pytest.mark.django_db
class TestLocationCreateSerializer:
    """Testes para LocationCreateSerializer."""

    def test_create_location_with_coordinates(self):
        """Testa criação de location com coordenadas."""
        data = {"name": "Paris, França", "latitude": "48.8566", "longitude": "2.3522"}

        serializer = LocationCreateSerializer(data=data)
        assert serializer.is_valid()

        location = serializer.save()

        assert location.name == "Paris, França"
        assert location.latitude == Decimal("48.8566")
        assert location.longitude == Decimal("2.3522")

    def test_create_location_without_coordinates(self):
        """Testa criação de location sem coordenadas."""
        data = {"name": "Algum lugar"}

        serializer = LocationCreateSerializer(data=data)
        assert serializer.is_valid()

        location = serializer.save()

        assert location.name == "Algum lugar"
        assert location.latitude is None
        assert location.longitude is None

    def test_validate_latitude_without_longitude(self):
        """Testa validação: latitude sem longitude."""
        data = {"name": "Local", "latitude": "10.0"}

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
        assert "juntas" in str(serializer.errors["non_field_errors"][0]).lower()

    def test_validate_longitude_without_latitude(self):
        """Testa validação: longitude sem latitude."""
        data = {"name": "Local", "longitude": "20.0"}

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_validate_latitude_range(self):
        """Testa validação: latitude fora do range (-90 a 90)."""
        # Latitude > 90
        data = {"name": "Local", "latitude": "95.0", "longitude": "10.0"}

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "latitude" in serializer.errors

        # Latitude < -90
        data["latitude"] = "-95.0"

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "latitude" in serializer.errors

    def test_validate_longitude_range(self):
        """Testa validação: longitude fora do range (-180 a 180)."""
        # Longitude > 180
        data = {"name": "Local", "latitude": "10.0", "longitude": "185.0"}

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "longitude" in serializer.errors

        # Longitude < -180
        data["longitude"] = "-185.0"

        serializer = LocationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "longitude" in serializer.errors

    def test_get_or_create_by_coordinates(self):
        """Testa reutilização de location por coordenadas (get_or_create)."""
        # Criar location inicial
        data = {
            "name": "Torre Eiffel",
            "latitude": "48.858844",
            "longitude": "2.294351",
        }

        serializer1 = LocationCreateSerializer(data=data)
        assert serializer1.is_valid()
        location1 = serializer1.save()

        # Tentar criar com mesmas coordenadas mas nome diferente
        data2 = {
            "name": "Eiffel Tower",
            "latitude": "48.858844",
            "longitude": "2.294351",
        }

        serializer2 = LocationCreateSerializer(data=data2)
        assert serializer2.is_valid()
        location2 = serializer2.save()

        # Deve retornar o mesmo location (unique_together)
        assert location1.id == location2.id
        assert location2.name == "Torre Eiffel"  # Nome original mantido

    def test_get_or_create_by_name(self):
        """Testa reutilização de location por nome (sem coordenadas)."""
        # Criar location sem coordenadas
        data = {"name": "Brasil"}

        serializer1 = LocationCreateSerializer(data=data)
        assert serializer1.is_valid()
        location1 = serializer1.save()

        # Tentar criar com mesmo nome
        serializer2 = LocationCreateSerializer(data=data)
        assert serializer2.is_valid()
        location2 = serializer2.save()

        # Deve retornar o mesmo location
        assert location1.id == location2.id

    def test_different_names_without_coordinates_create_multiple(self):
        """Testa que nomes diferentes sem coordenadas criam locations separadas."""
        data1 = {"name": "Brasil"}
        data2 = {"name": "Argentina"}

        serializer1 = LocationCreateSerializer(data=data1)
        serializer2 = LocationCreateSerializer(data=data2)

        assert serializer1.is_valid()
        assert serializer2.is_valid()

        location1 = serializer1.save()
        location2 = serializer2.save()

        assert location1.id != location2.id
        assert location1.name == "Brasil"
        assert location2.name == "Argentina"

    def test_create_with_null_coordinates(self):
        """Testa criação explícita com coordenadas null."""
        data = {"name": "Local", "latitude": None, "longitude": None}

        serializer = LocationCreateSerializer(data=data)
        assert serializer.is_valid()

        location = serializer.save()

        assert location.name == "Local"
        assert location.latitude is None
        assert location.longitude is None


@pytest.mark.django_db
class TestScheduledPostsSerializer:
    """Testes para serializers de posts agendados."""

    def test_serialize_post_with_scheduled_for(self):
        """Testa serialização de post agendado."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future = timezone.now() + timedelta(hours=2)
        post = Post.objects.create(
            author=user, content="Post agendado", scheduled_for=future
        )

        serializer = PostSerializer(post)
        data = serializer.data

        assert "scheduled_for" in data
        assert data["scheduled_for"] is not None
        assert "is_published" in data
        assert data["is_published"] is False

    def test_serialize_post_without_scheduled_for(self):
        """Testa serialização de post sem agendamento."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Post normal")

        serializer = PostSerializer(post)
        data = serializer.data

        assert "scheduled_for" in data
        assert data["scheduled_for"] is None
        assert "is_published" in data
        assert data["is_published"] is True

    def test_is_published_field_readonly(self):
        """Testa que is_published é read-only."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test")

        serializer = PostSerializer(post)
        assert "is_published" in serializer.data
        assert serializer.data["is_published"] is True

    def test_create_post_with_scheduled_for_valid(self):
        """Testa criação de post com scheduled_for válido."""
        future = timezone.now() + timedelta(hours=2)

        data = {"content": "Post agendado", "scheduled_for": future.isoformat()}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_post_with_scheduled_for_in_past_fails(self):
        """Testa que scheduled_for no passado retorna erro."""
        past = timezone.now() - timedelta(hours=1)

        data = {"content": "Post no passado", "scheduled_for": past.isoformat()}

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "scheduled_for" in serializer.errors
        assert "passado" in str(serializer.errors["scheduled_for"][0]).lower()

    def test_create_post_with_scheduled_for_near_past_allowed(self):
        """Testa margem de erro de 5 minutos no passado."""
        # 3 minutos atrás (dentro da margem de 5 min)
        near_past = timezone.now() - timedelta(minutes=3)

        data = {"content": "Post 3 min atrás", "scheduled_for": near_past.isoformat()}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_post_with_scheduled_for_null(self):
        """Testa criação com scheduled_for = null."""
        data = {"content": "Post normal", "scheduled_for": None}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_post_without_scheduled_for_field(self):
        """Testa criação sem fornecer scheduled_for (campo opcional)."""
        data = {"content": "Post sem scheduled_for"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_scheduled_post_serializer_fields(self):
        """Testa campos do ScheduledPostSerializer."""
        user = User.objects.create_user(username="testuser", password="pass123")

        future = timezone.now() + timedelta(hours=2)
        post = Post.objects.create(
            author=user, content="Post agendado", scheduled_for=future
        )

        serializer = ScheduledPostSerializer(post)
        data = serializer.data

        assert "id" in data
        assert "content" in data
        assert "scheduled_for" in data
        assert "is_published" in data
        assert "created_at" in data
        assert "author" in data

    def test_scheduled_post_serializer_multiple_posts(self):
        """Testa serialização de múltiplos posts agendados."""
        user = User.objects.create_user(username="testuser", password="pass123")

        posts = []
        for i in range(3):
            future = timezone.now() + timedelta(hours=i + 1)
            post = Post.objects.create(
                author=user, content=f"Post {i}", scheduled_for=future
            )
            posts.append(post)

        serializer = ScheduledPostSerializer(posts, many=True)
        data = serializer.data

        assert len(data) == 3
        assert all("scheduled_for" in item for item in data)


@pytest.mark.django_db
class TestViewsCounterSerializer:
    """Testes para views_count no serializer."""

    def test_serialize_post_includes_views_in_stats(self):
        """Testa que stats inclui views."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test post")

        serializer = PostSerializer(post)
        data = serializer.data

        assert "stats" in data
        assert "views" in data["stats"]
        assert data["stats"]["views"] == 0

    def test_serialize_post_with_views_count(self):
        """Testa serialização com views_count != 0."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Incrementar views
        post.increment_views()
        post.increment_views()
        post.increment_views()

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["stats"]["views"] == 3

    def test_stats_includes_all_metrics(self):
        """Testa que stats inclui comments, retweets, likes, views."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        post.increment_views()

        serializer = PostSerializer(post)
        stats = serializer.data["stats"]

        assert "comments" in stats
        assert "retweets" in stats
        assert "likes" in stats
        assert "views" in stats
        assert stats["views"] == 1

    def test_views_field_is_readonly(self):
        """Testa que views não pode ser editado via serializer."""
        user = User.objects.create_user(username="testuser", password="pass123")
        post = Post.objects.create(author=user, content="Test")

        # Tentar "editar" views via serializer não deve funcionar
        # (views_count não está em PostCreateSerializer)
        serializer = PostSerializer(post)

        # views aparece em stats, mas não é editável
        assert "views" in serializer.data["stats"]

    def test_multiple_posts_different_views(self):
        """Testa serialização de múltiplos posts com views diferentes."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post1 = Post.objects.create(author=user, content="Post 1")
        post2 = Post.objects.create(author=user, content="Post 2")
        post3 = Post.objects.create(author=user, content="Post 3")

        post1.increment_views()
        post2.increment_views()
        post2.increment_views()
        post3.increment_views()
        post3.increment_views()
        post3.increment_views()

        serializer = PostSerializer([post1, post2, post3], many=True)
        data = serializer.data

        assert data[0]["stats"]["views"] == 1
        assert data[1]["stats"]["views"] == 2
        assert data[2]["stats"]["views"] == 3


@pytest.mark.django_db
class TestHashtagSerializer:
    """Testes para HashtagSerializer."""

    def test_serialize_hashtag(self):
        """Testa serialização de hashtag."""
        hashtag = Hashtag.objects.create(name="python", posts_count=5)

        serializer = HashtagSerializer(hashtag)
        data = serializer.data

        assert data["name"] == "python"
        assert data["slug"] == "python"
        assert data["posts_count"] == 5
        assert "created_at" in data

    def test_hashtag_fields_readonly(self):
        """Testa que campos são read-only."""
        hashtag = Hashtag.objects.create(name="python")

        serializer = HashtagSerializer(hashtag)

        # Todos os campos devem ser read-only
        assert "id" in serializer.data
        assert "slug" in serializer.data


@pytest.mark.django_db
class TestPostSerializerWithHashtags:
    """Testes para PostSerializer com hashtags."""

    def test_post_includes_hashtags(self):
        """Testa que PostSerializer inclui hashtags."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test #python")
        tag = Hashtag.objects.create(name="python")
        post.hashtags.add(tag)

        serializer = PostSerializer(post)
        data = serializer.data

        assert "hashtags" in data
        assert len(data["hashtags"]) == 1
        assert data["hashtags"][0]["name"] == "python"

    def test_post_with_multiple_hashtags(self):
        """Testa post com múltiplas hashtags."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test")
        tag1 = Hashtag.objects.create(name="python")
        tag2 = Hashtag.objects.create(name="django")
        post.hashtags.add(tag1, tag2)

        serializer = PostSerializer(post)
        data = serializer.data

        assert len(data["hashtags"]) == 2
        names = [h["name"] for h in data["hashtags"]]
        assert "python" in names
        assert "django" in names


@pytest.mark.django_db
class TestPostCreateSerializerHashtagExtraction:
    """Testes para extração automática de hashtags no PostCreateSerializer."""

    def test_create_post_extracts_hashtags(self):
        """Testa que hashtags são extraídas automaticamente."""
        user = User.objects.create_user(username="testuser", password="pass123")

        data = {"content": "Adorei #python e #django!"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        post = serializer.save(author=user)

        # Verificar que hashtags foram extraídas
        assert post.hashtags.count() == 2

        hashtag_names = [h.name for h in post.hashtags.all()]
        assert "python" in hashtag_names
        assert "django" in hashtag_names

    def test_create_post_creates_new_hashtags(self):
        """Testa que hashtags novas são criadas."""
        user = User.objects.create_user(username="testuser", password="pass123")

        assert Hashtag.objects.count() == 0

        data = {"content": "Test #newtag"}
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        serializer.save(author=user)

        # Verificar que hashtag foi criada
        assert Hashtag.objects.count() == 1
        hashtag = Hashtag.objects.get(name="newtag")
        assert hashtag.posts_count == 1

    def test_create_post_reuses_existing_hashtags(self):
        """Testa que hashtags existentes são reutilizadas."""
        user = User.objects.create_user(username="testuser", password="pass123")

        # Criar hashtag existente
        existing_tag = Hashtag.objects.create(name="python", posts_count=5)

        data = {"content": "Test #python"}
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        serializer.save(author=user)

        # Verificar que não criou nova hashtag
        assert Hashtag.objects.count() == 1

        # Verificar que posts_count foi incrementado
        existing_tag.refresh_from_db()
        assert existing_tag.posts_count == 6

    def test_create_post_without_hashtags(self):
        """Testa criação de post sem hashtags."""
        user = User.objects.create_user(username="testuser", password="pass123")

        data = {"content": "Post sem hashtags"}
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        post = serializer.save(author=user)

        assert post.hashtags.count() == 0

    def test_create_post_normalizes_hashtags(self):
        """Testa normalização de hashtags (lowercase, sem duplicatas)."""
        user = User.objects.create_user(username="testuser", password="pass123")

        data = {"content": "#Python #PYTHON #python"}
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

        post = serializer.save(author=user)

        # Deve ter apenas uma hashtag
        assert post.hashtags.count() == 1
        assert post.hashtags.first().name == "python"


@pytest.mark.django_db
class TestNotificationSerializer:
    """Testes para NotificationSerializer."""

    def test_serialize_notification_with_post(self):
        """Testa serialização de notificação com post."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Meu post")
        
        notification = Notification.objects.create(
            recipient=alice,
            actor=bob,
            notification_type='like',
            post=post
        )
        
        serializer = NotificationSerializer(notification)
        data = serializer.data
        
        assert data["actor"]["username"] == "bob"
        assert data["notification_type"] == "like"
        assert data["notification_type_display"] == "Curtida"
        assert data["post"] == post.id
        assert data["is_read"] is False

    def test_serialize_notification_post_preview(self):
        """Testa campo post_preview."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=alice, content="Conteúdo do post")
        
        notification = Notification.objects.create(
            recipient=alice,
            actor=bob,
            notification_type='like',
            post=post
        )
        
        serializer = NotificationSerializer(notification)
        data = serializer.data
        
        assert "post_preview" in data
        assert data["post_preview"]["id"] == post.id
        assert data["post_preview"]["content"] == "Conteúdo do post"
        assert data["post_preview"]["author"]["username"] == "alice"

    def test_serialize_notification_without_post(self):
        """Testa serialização de notificação sem post (follow)."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        
        notification = Notification.objects.create(
            recipient=alice,
            actor=bob,
            notification_type='follow',
            post=None
        )
        
        serializer = NotificationSerializer(notification)
        data = serializer.data
        
        assert data["post"] is None
        assert data["post_preview"] is None

    def test_serialize_notification_truncates_long_content(self):
        """Testa que post_preview trunca conteúdo longo."""
        alice = User.objects.create_user(username="alice", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        
        long_content = "A" * 150  # 150 caracteres
        post = Post.objects.create(author=alice, content=long_content)
        
        notification = Notification.objects.create(
            recipient=alice,
            actor=bob,
            notification_type='like',
            post=post
        )
        
        serializer = NotificationSerializer(notification)
        data = serializer.data
        
        # Deve truncar em 100 caracteres
        assert len(data["post_preview"]["content"]) == 100
