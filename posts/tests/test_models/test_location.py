from decimal import Decimal

from django.contrib.auth import get_user_model

import pytest

from posts.models import Location, Post

User = get_user_model()


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
