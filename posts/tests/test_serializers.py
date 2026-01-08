"""
Testes para os serializers do app posts.
"""
import pytest
from django.contrib.auth import get_user_model
from posts.models import Post, Comment, Like
from posts.serializers import (
    PostSerializer,
    PostCreateSerializer,
    CommentSerializer,
    LikeSerializer
)

User = get_user_model()


@pytest.mark.django_db
class TestPostSerializer:
    """Testes para o PostSerializer."""
    
    def test_serialize_post(self):
        """Testa serialização de post."""
        author = User.objects.create_user(
            username='author',
            password='pass123'
        )
        post = Post.objects.create(
            author=author,
            content='Test post content'
        )
        
        serializer = PostSerializer(post)
        data = serializer.data
        
        assert data['content'] == 'Test post content'
        assert data['author']['username'] == 'author'
        assert data['likes_count'] == 0
        assert data['comments_count'] == 0
        assert 'created_at' in data
    
    def test_serialize_post_with_counts(self):
        """Testa serialização com contadores."""
        author = User.objects.create_user(username='author', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        user3 = User.objects.create_user(username='user3', password='pass123')
        
        post = Post.objects.create(author=author, content='Test')
        
        # Criar likes e comments
        Like.objects.create(user=user2, post=post)
        Like.objects.create(user=user3, post=post)
        Comment.objects.create(user=user2, post=post, content='Comment 1')
        Comment.objects.create(user=user3, post=post, content='Comment 2')
        Comment.objects.create(user=user3, post=post, content='Comment 3')
        
        serializer = PostSerializer(post)
        data = serializer.data
        
        assert data['likes_count'] == 2
        assert data['comments_count'] == 3


@pytest.mark.django_db
class TestPostCreateSerializer:
    """Testes para o PostCreateSerializer."""
    
    def test_create_post_valid(self):
        """Testa criação de post com dados válidos."""
        data = {
            'content': 'New post content'
        }
        
        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_create_post_empty_content(self):
        """Testa criação com conteúdo vazio."""
        data = {
            'content': '   '  # Apenas espaços
        }
        
        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
    
    def test_create_post_missing_content(self):
        """Testa criação sem conteúdo."""
        data = {}
        
        serializer = PostCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'content' in serializer.errors


@pytest.mark.django_db
class TestCommentSerializer:
    """Testes para o CommentSerializer."""
    
    def test_serialize_comment(self):
        """Testa serialização de comentário."""
        author = User.objects.create_user(username='author', password='pass123')
        commenter = User.objects.create_user(username='commenter', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        comment = Comment.objects.create(
            user=commenter,
            post=post,
            content='Test comment'
        )
        
        serializer = CommentSerializer(comment)
        data = serializer.data
        
        assert data['content'] == 'Test comment'
        assert data['user']['username'] == 'commenter'
        assert data['post'] == post.id
        assert 'created_at' in data
    
    def test_create_comment_valid(self):
        """Testa criação de comentário válido."""
        author = User.objects.create_user(username='author', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        data = {
            'post': post.id,
            'content': 'New comment'
        }
        
        serializer = CommentSerializer(data=data)
        assert serializer.is_valid()
    
    def test_create_comment_empty_content(self):
        """Testa criação com conteúdo vazio."""
        author = User.objects.create_user(username='author', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        data = {
            'post': post.id,
            'content': '   '
        }
        
        serializer = CommentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'content' in serializer.errors


@pytest.mark.django_db
class TestLikeSerializer:
    """Testes para o LikeSerializer."""
    
    def test_serialize_like(self):
        """Testa serialização de like."""
        author = User.objects.create_user(username='author', password='pass123')
        liker = User.objects.create_user(username='liker', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        like = Like.objects.create(user=liker, post=post)
        
        serializer = LikeSerializer(like)
        data = serializer.data
        
        assert data['user'] == liker.id
        assert data['post'] == post.id
        assert data['user_username'] == 'liker'
        assert 'created_at' in data
    
    def test_create_like_valid(self):
        """Testa validação de like válido."""
        author = User.objects.create_user(username='author', password='pass123')
        liker = User.objects.create_user(username='liker', password='pass123')
        post = Post.objects.create(author=author, content='Test post')
        
        data = {
            'user': liker.id,
            'post': post.id
        }
        
        serializer = LikeSerializer(data=data)
        assert serializer.is_valid()
        
        # Nota: Na prática, o user é definido pelo viewset (request.user)
        # Aqui só validamos que os dados são válidos
