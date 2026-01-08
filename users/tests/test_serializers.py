"""
Testes para os serializers do app users.
"""
import pytest
from django.contrib.auth import get_user_model
from users.models import Follow
from users.serializers import UserSerializer, UserCreateSerializer, FollowSerializer

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializer:
    """Testes para o UserSerializer."""
    
    def test_serialize_user(self):
        """Testa serialização de usuário."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            bio='Test bio'
        )
        
        serializer = UserSerializer(user)
        data = serializer.data
        
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['first_name'] == 'Test'
        assert data['last_name'] == 'User'
        assert data['bio'] == 'Test bio'
        assert data['followers_count'] == 0
        assert data['following_count'] == 0
        assert data['posts_count'] == 0
        assert 'password' not in data  # Senha não deve aparecer
    
    def test_serialize_user_with_followers(self):
        """Testa serialização com contadores."""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        user3 = User.objects.create_user(username='user3', password='pass123')
        
        # user2 e user3 seguem user1
        Follow.objects.create(follower=user2, following=user1)
        Follow.objects.create(follower=user3, following=user1)
        
        serializer = UserSerializer(user1)
        data = serializer.data
        
        assert data['followers_count'] == 2
        assert data['following_count'] == 0


@pytest.mark.django_db
class TestUserCreateSerializer:
    """Testes para o UserCreateSerializer."""
    
    def test_create_user_valid(self):
        """Testa criação de usuário com dados válidos."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('newpass123')
        assert user.first_name == 'New'
        assert user.last_name == 'User'
    
    def test_create_user_password_mismatch(self):
        """Testa criação com senhas diferentes."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors or 'non_field_errors' in serializer.errors
    
    def test_create_user_missing_fields(self):
        """Testa criação com campos obrigatórios faltando."""
        data = {
            'username': 'newuser'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
        assert 'password_confirm' in serializer.errors
    
    def test_password_min_length(self):
        """Testa validação de tamanho mínimo de senha."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'short',
            'password_confirm': 'short'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors


@pytest.mark.django_db
class TestFollowSerializer:
    """Testes para o FollowSerializer."""
    
    def test_serialize_follow(self):
        """Testa serialização de follow."""
        user1 = User.objects.create_user(username='follower', password='pass123')
        user2 = User.objects.create_user(username='following', password='pass123')
        
        follow = Follow.objects.create(follower=user1, following=user2)
        
        serializer = FollowSerializer(follow)
        data = serializer.data
        
        assert data['follower'] == user1.id
        assert data['following'] == user2.id
        assert data['follower_username'] == 'follower'
        assert data['following_username'] == 'following'
    
    def test_create_follow_valid(self):
        """Testa criação de follow válido."""
        user1 = User.objects.create_user(username='follower', password='pass123')
        user2 = User.objects.create_user(username='following', password='pass123')
        
        data = {
            'follower': user1.id,
            'following': user2.id
        }
        
        serializer = FollowSerializer(data=data)
        assert serializer.is_valid()
        
        follow = serializer.save()
        
        assert follow.follower == user1
        assert follow.following == user2
    
    def test_cannot_follow_self(self):
        """Testa que não pode seguir a si mesmo."""
        user = User.objects.create_user(username='user1', password='pass123')
        
        data = {
            'follower': user.id,
            'following': user.id
        }
        
        serializer = FollowSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        