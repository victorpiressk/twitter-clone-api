"""
Testes para os models do app users.
"""
import pytest
from django.contrib.auth import get_user_model
from users.models import Follow

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Testes para o model User."""
    
    def test_create_user(self):
        """Testa criação de usuário."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_create_superuser(self):
        """Testa criação de superusuário."""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        assert admin.username == 'admin'
        assert admin.is_active
        assert admin.is_staff
        assert admin.is_superuser
    
    def test_user_str(self):
        """Testa representação string do usuário."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        assert str(user) == 'testuser'
    
    def test_user_bio_default(self):
        """Testa valor padrão da bio."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        assert user.bio == ''
    
    def test_user_followers_count(self):
        """Testa contagem de seguidores."""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        user3 = User.objects.create_user(username='user3', password='pass123')
        
        # user2 e user3 seguem user1
        Follow.objects.create(follower=user2, following=user1)
        Follow.objects.create(follower=user3, following=user1)
        
        assert user1.followers_count == 2
    
    def test_user_following_count(self):
        """Testa contagem de quem o usuário segue."""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        user3 = User.objects.create_user(username='user3', password='pass123')
        
        # user1 segue user2 e user3
        Follow.objects.create(follower=user1, following=user2)
        Follow.objects.create(follower=user1, following=user3)
        
        assert user1.following_count == 2


@pytest.mark.django_db
class TestFollowModel:
    """Testes para o model Follow."""
    
    def test_create_follow(self):
        """Testa criação de follow."""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        follow = Follow.objects.create(follower=user1, following=user2)
        
        assert follow.follower == user1
        assert follow.following == user2
    
    def test_follow_str(self):
        """Testa representação string do follow."""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        follow = Follow.objects.create(follower=user1, following=user2)
        
        assert 'user1' in str(follow)
        assert 'user2' in str(follow)
    
    def test_cannot_follow_self(self):
        """Testa que usuário não pode seguir a si mesmo."""
        user = User.objects.create_user(username='user1', password='pass123')
        
        follow = Follow(follower=user, following=user)
        
        with pytest.raises(Exception):
            follow.full_clean()  # Valida antes de salvar
    
    def test_unique_follow(self):
        """Testa que não pode seguir o mesmo usuário 2 vezes."""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Primeiro follow
        Follow.objects.create(follower=user1, following=user2)
        
        # Tentar criar duplicado
        with pytest.raises(Exception):
            Follow.objects.create(follower=user1, following=user2)
            