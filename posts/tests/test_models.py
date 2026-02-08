"""
Testes para os models do app posts.
"""

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
