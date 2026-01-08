"""
Testes para os models do app posts.
"""
import pytest
from django.contrib.auth import get_user_model
from posts.models import Post, Comment, Like

User = get_user_model()


@pytest.mark.django_db
class TestPostModel:
    """Testes para o model Post."""
    
    def test_create_post(self):
        """Testa criação de post."""
        user = User.objects.create_user(username='testuser', password='pass123')
        post = Post.objects.create(
            author=user,
            content='Test post content'
        )
        
        assert post.author == user
        assert post.content == 'Test post content'
        assert not post.image
    
    def test_post_str(self):
        """Testa representação string do post."""
        user = User.objects.create_user(username='testuser', password='pass123')
        post = Post.objects.create(
            author=user,
            content='This is a very long content that should be truncated in the string representation'
        )
        
        post_str = str(post)
        assert 'testuser' in post_str
        assert len(post_str) <= 60  # Username + 50 chars de conteúdo + ": "
    
    def test_post_likes_count(self):
        """Testa contagem de curtidas."""
        user = User.objects.create_user(username='author', password='pass123')
        user2 = User.objects.create_user(username='liker1', password='pass123')
        user3 = User.objects.create_user(username='liker2', password='pass123')
        
        post = Post.objects.create(author=user, content='Test')
        
        Like.objects.create(user=user2, post=post)
        Like.objects.create(user=user3, post=post)
        
        assert post.likes_count == 2
    
    def test_post_comments_count(self):
        """Testa contagem de comentários."""
        user = User.objects.create_user(username='author', password='pass123')
        user2 = User.objects.create_user(username='commenter', password='pass123')
        
        post = Post.objects.create(author=user, content='Test')
        
        Comment.objects.create(user=user2, post=post, content='Comment 1')
        Comment.objects.create(user=user2, post=post, content='Comment 2')
        Comment.objects.create(user=user2, post=post, content='Comment 3')
        
        assert post.comments_count == 3
    
    def test_post_content_max_length(self):
        """Testa limite de caracteres do conteúdo."""
        user = User.objects.create_user(username='testuser', password='pass123')
        content = 'a' * 280  # Exatamente 280 caracteres
        
        post = Post.objects.create(author=user, content=content)
        
        assert len(post.content) == 280


@pytest.mark.django_db
class TestCommentModel:
    """Testes para o model Comment."""
    
    def test_create_comment(self):
        """Testa criação de comentário."""
        author = User.objects.create_user(username='author', password='pass123')
        commenter = User.objects.create_user(username='commenter', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        comment = Comment.objects.create(
            user=commenter,
            post=post,
            content='Test comment'
        )
        
        assert comment.user == commenter
        assert comment.post == post
        assert comment.content == 'Test comment'
    
    def test_comment_str(self):
        """Testa representação string do comentário."""
        author = User.objects.create_user(username='author', password='pass123')
        commenter = User.objects.create_user(username='commenter', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        comment = Comment.objects.create(
            user=commenter,
            post=post,
            content='Test comment'
        )
        
        comment_str = str(comment)
        assert 'commenter' in comment_str
        assert 'comentou' in comment_str or 'comment' in comment_str.lower()


@pytest.mark.django_db
class TestLikeModel:
    """Testes para o model Like."""
    
    def test_create_like(self):
        """Testa criação de curtida."""
        author = User.objects.create_user(username='author', password='pass123')
        liker = User.objects.create_user(username='liker', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        like = Like.objects.create(user=liker, post=post)
        
        assert like.user == liker
        assert like.post == post
    
    def test_like_str(self):
        """Testa representação string da curtida."""
        author = User.objects.create_user(username='author', password='pass123')
        liker = User.objects.create_user(username='liker', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        like = Like.objects.create(user=liker, post=post)
        
        like_str = str(like)
        assert 'liker' in like_str
        assert 'curtiu' in like_str or 'like' in like_str.lower()
    
    def test_unique_like(self):
        """Testa que não pode curtir o mesmo post 2 vezes."""
        author = User.objects.create_user(username='author', password='pass123')
        liker = User.objects.create_user(username='liker', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        # Primeiro like
        Like.objects.create(user=liker, post=post)
        
        # Tentar criar duplicado
        with pytest.raises(Exception):
            Like.objects.create(user=liker, post=post)
    
    def test_user_can_like_multiple_posts(self):
        """Testa que usuário pode curtir vários posts diferentes."""
        author = User.objects.create_user(username='author', password='pass123')
        liker = User.objects.create_user(username='liker', password='pass123')
        
        post1 = Post.objects.create(author=author, content='Post 1')
        post2 = Post.objects.create(author=author, content='Post 2')
        post3 = Post.objects.create(author=author, content='Post 3')
        
        Like.objects.create(user=liker, post=post1)
        Like.objects.create(user=liker, post=post2)
        Like.objects.create(user=liker, post=post3)
        
        assert Like.objects.filter(user=liker).count() == 3
