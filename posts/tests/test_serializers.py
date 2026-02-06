"""
Testes para os serializers do app posts.
"""

from django.contrib.auth import get_user_model

import pytest
from rest_framework.test import APIRequestFactory

from posts.models import Comment, Like, Post
from posts.serializers import (
    CommentSerializer,
    LikeSerializer,
    PostCreateSerializer,
    PostSerializer,
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
            author=replier,
            content="This is a reply",
            in_reply_to=original
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
        
        data = {
            "content": "This is a reply",
            "in_reply_to": original.id
        }

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_create_reply_invalid_post(self):
        """Testa que in_reply_to com post inexistente retorna erro."""
        data = {
            "content": "Reply to nothing",
            "in_reply_to": 99999  # Post que não existe
        }

        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "in_reply_to" in serializer.errors

    def test_create_post_without_reply(self):
        """Testa que in_reply_to é opcional."""
        data = {"content": "Normal post"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()
        assert "in_reply_to" not in serializer.validated_data or serializer.validated_data.get("in_reply_to") is None


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
