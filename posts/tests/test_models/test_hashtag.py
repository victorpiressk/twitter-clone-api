from django.contrib.auth import get_user_model

import pytest

from posts.models import Hashtag, Post
from posts.utils import extract_hashtags

User = get_user_model()


@pytest.mark.django_db
class TestHashtagModel:
    """Testes para o model Hashtag."""

    def test_create_hashtag(self):
        """Testa criação de hashtag."""
        hashtag = Hashtag.objects.create(name="python")

        assert hashtag.name == "python"
        assert hashtag.slug == "python"
        assert hashtag.posts_count == 0

    def test_hashtag_slug_auto_generated(self):
        """Testa que slug é gerado automaticamente."""
        hashtag = Hashtag.objects.create(name="Machine Learning")

        assert hashtag.slug == "machine-learning"

    def test_hashtag_unique_name(self):
        """Testa que name deve ser único."""
        Hashtag.objects.create(name="python")

        with pytest.raises(Exception):
            Hashtag.objects.create(name="python")

    def test_hashtag_str_representation(self):
        """Testa representação string."""
        hashtag = Hashtag.objects.create(name="django")
        hashtag.posts_count = 5
        hashtag.save()

        assert str(hashtag) == "#django (5 posts)"

    def test_increment_count(self):
        """Testa método increment_count()."""
        hashtag = Hashtag.objects.create(name="python")

        assert hashtag.posts_count == 0

        hashtag.increment_count()
        assert hashtag.posts_count == 1

        hashtag.increment_count()
        assert hashtag.posts_count == 2

    def test_decrement_count(self):
        """Testa método decrement_count()."""
        hashtag = Hashtag.objects.create(name="python", posts_count=3)

        hashtag.decrement_count()
        assert hashtag.posts_count == 2

        hashtag.decrement_count()
        assert hashtag.posts_count == 1

    def test_post_hashtag_relationship(self):
        """Testa relacionamento ManyToMany Post ↔ Hashtag."""
        user = User.objects.create_user(username="testuser", password="pass123")

        post = Post.objects.create(author=user, content="Test post")
        tag1 = Hashtag.objects.create(name="python")
        tag2 = Hashtag.objects.create(name="django")

        post.hashtags.add(tag1, tag2)

        assert post.hashtags.count() == 2
        assert tag1 in post.hashtags.all()
        assert tag2 in post.hashtags.all()

    def test_hashtag_posts_reverse_relationship(self):
        """Testa relacionamento reverso hashtag.posts."""
        user = User.objects.create_user(username="testuser", password="pass123")

        hashtag = Hashtag.objects.create(name="python")

        post1 = Post.objects.create(author=user, content="Post 1")
        post2 = Post.objects.create(author=user, content="Post 2")

        post1.hashtags.add(hashtag)
        post2.hashtags.add(hashtag)

        assert hashtag.posts.count() == 2
        assert post1 in hashtag.posts.all()
        assert post2 in hashtag.posts.all()


@pytest.mark.django_db
class TestHashtagUtils:
    """Testes para funções utilitárias de hashtags."""

    def test_extract_hashtags_single(self):
        """Testa extração de uma hashtag."""
        text = "Adorei #python!"
        tags = extract_hashtags(text)

        assert tags == ["python"]

    def test_extract_hashtags_multiple(self):
        """Testa extração de múltiplas hashtags."""
        text = "Adorei #python e #django! #API_REST"
        tags = extract_hashtags(text)

        assert set(tags) == {"api_rest", "django", "python"}

    def test_extract_hashtags_lowercase(self):
        """Testa normalização para lowercase."""
        text = "#Python #DJANGO #Api"
        tags = extract_hashtags(text)

        assert all(tag.islower() for tag in tags)
        assert set(tags) == {"api", "django", "python"}

    def test_extract_hashtags_no_duplicates(self):
        """Testa remoção de duplicatas."""
        text = "#python #Python #PYTHON"
        tags = extract_hashtags(text)

        assert tags == ["python"]

    def test_extract_hashtags_with_underscore(self):
        """Testa hashtags com underscore."""
        text = "#Machine_Learning #Deep_Learning"
        tags = extract_hashtags(text)

        assert set(tags) == {"deep_learning", "machine_learning"}

    def test_extract_hashtags_with_numbers(self):
        """Testa hashtags com números."""
        text = "#python3 #django4 #api2023"
        tags = extract_hashtags(text)

        assert set(tags) == {"api2023", "django4", "python3"}

    def test_extract_hashtags_empty_text(self):
        """Testa com texto vazio."""
        assert extract_hashtags("") == []
        assert extract_hashtags(None) == []

    def test_extract_hashtags_no_hashtags(self):
        """Testa texto sem hashtags."""
        text = "Sem hashtags neste texto"
        tags = extract_hashtags(text)

        assert tags == []

    def test_extract_hashtags_special_characters(self):
        """Testa que caracteres especiais não são incluídos."""
        text = "#python! #django? #api."
        tags = extract_hashtags(text)

        assert set(tags) == {"api", "django", "python"}

    def test_extract_hashtags_at_start(self):
        """Testa hashtag no início do texto."""
        text = "#python é incrível"
        tags = extract_hashtags(text)

        assert tags == ["python"]

    def test_extract_hashtags_at_end(self):
        """Testa hashtag no final do texto."""
        text = "Adorei #python"
        tags = extract_hashtags(text)

        assert tags == ["python"]
