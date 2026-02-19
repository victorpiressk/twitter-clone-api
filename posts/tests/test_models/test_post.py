from django.contrib.auth import get_user_model

import pytest

from posts.models import Comment, Like, Post

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
