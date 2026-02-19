from decimal import Decimal

from django.urls import reverse

import pytest
from rest_framework import status

from posts.models import Location, Post


@pytest.mark.django_db
class TestLocationViewSet:
    """Testes para o LocationViewSet."""

    def test_list_locations(self, api_client):
        """Testa listagem de locations."""
        Location.objects.create(
            name="Paris, França", latitude=48.8566, longitude=2.3522
        )
        Location.objects.create(
            name="Londres, Reino Unido", latitude=51.5074, longitude=-0.1278
        )

        url = reverse("location-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_retrieve_location(self, api_client):
        """Testa obter detalhes de uma location."""
        location = Location.objects.create(
            name="Torre Eiffel, Paris",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )

        url = reverse("location-detail", kwargs={"pk": location.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Torre Eiffel, Paris"
        assert response.data["has_coordinates"] is True

    def test_search_locations(self, api_client):
        """Testa busca de locations por nome."""
        Location.objects.create(name="Paris, França")
        Location.objects.create(name="Parque Ibirapuera, São Paulo")
        Location.objects.create(name="Londres, Reino Unido")

        url = reverse("location-search")
        response = api_client.get(url, {"q": "par"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Paris e Parque

        # Verificar que Londres não está nos resultados
        names = [loc["name"] for loc in response.data]
        assert "Paris, França" in names
        assert "Parque Ibirapuera, São Paulo" in names
        assert "Londres, Reino Unido" not in names

    def test_search_locations_case_insensitive(self, api_client):
        """Testa busca case-insensitive."""
        Location.objects.create(name="Paris, França")

        url = reverse("location-search")
        response = api_client.get(url, {"q": "PARIS"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Paris, França"

    def test_search_locations_without_query(self, api_client):
        """Testa busca sem parâmetro q."""
        url = reverse("location-search")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "obrigatório" in str(response.data["detail"]).lower()

    def test_search_locations_limit_results(self, api_client):
        """Testa que busca limita a 10 resultados."""
        # Criar 15 locations com "City" no nome
        for i in range(15):
            Location.objects.create(name=f"City {i}")

        url = reverse("location-search")
        response = api_client.get(url, {"q": "City"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10  # Máximo 10

    def test_nearby_locations(self, api_client):
        """Testa busca de locations próximas."""
        # Torre Eiffel
        Location.objects.create(
            name="Torre Eiffel",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )
        # Louvre (próximo)
        Location.objects.create(
            name="Museu do Louvre",
            latitude=Decimal("48.860611"),
            longitude=Decimal("2.337644"),
        )
        # Londres (longe)
        Location.objects.create(
            name="Big Ben", latitude=Decimal("51.5007"), longitude=Decimal("-0.1246")
        )

        url = reverse("location-nearby")
        response = api_client.get(
            url, {"lat": "48.858844", "lng": "2.294351", "radius": "10"}  # 10 km
        )

        assert response.status_code == status.HTTP_200_OK

        # Torre Eiffel e Louvre devem estar nos resultados
        names = [loc["name"] for loc in response.data]
        assert "Torre Eiffel" in names
        assert "Museu do Louvre" in names
        # Big Ben não deve estar (muito longe)
        assert "Big Ben" not in names

    def test_nearby_locations_without_parameters(self, api_client):
        """Testa nearby sem parâmetros lat/lng."""
        url = reverse("location-nearby")

        # Sem parâmetros (usa 0,0 como padrão - comportamento válido)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Parâmetros inválidos (texto ao invés de número)
        response = api_client.get(url, {"lat": "abc", "lng": "xyz"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_nearby_locations_invalid_coordinates(self, api_client):
        """Testa nearby com coordenadas inválidas."""
        url = reverse("location-nearby")

        # Latitude inválida
        response = api_client.get(url, {"lat": "95.0", "lng": "10.0"})  # > 90
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Longitude inválida
        response = api_client.get(url, {"lat": "10.0", "lng": "185.0"})  # > 180
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_nearby_only_returns_locations_with_coordinates(self, api_client):
        """Testa que nearby só retorna locations com coordenadas."""
        Location.objects.create(
            name="Com coordenadas",
            latitude=Decimal("48.858844"),
            longitude=Decimal("2.294351"),
        )
        Location.objects.create(name="Sem coordenadas")

        url = reverse("location-nearby")
        response = api_client.get(
            url, {"lat": "48.858844", "lng": "2.294351", "radius": "10"}
        )

        assert response.status_code == status.HTTP_200_OK

        names = [loc["name"] for loc in response.data]
        assert "Com coordenadas" in names
        assert "Sem coordenadas" not in names


@pytest.mark.django_db
class TestPostWithLocation:
    """Testes para posts com locations."""

    def test_create_post_with_location(self, authenticated_client, user):
        """Testa criar post com location."""
        url = reverse("post-list")

        data = {
            "content": "Visitando Paris!",
            "location": {
                "name": "Torre Eiffel, Paris",
                "latitude": "48.858844",
                "longitude": "2.294351",
            },
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verificar que post foi criado
        post = Post.objects.get(id=response.data["id"])
        assert post.content == "Visitando Paris!"

        # Verificar que location foi criada e associada
        assert post.location is not None
        assert post.location.name == "Torre Eiffel, Paris"
        assert post.location.latitude == Decimal("48.858844")

    def test_create_post_with_location_without_coordinates(
        self, authenticated_client, user
    ):
        """Testa criar post com location sem coordenadas."""
        url = reverse("post-list")

        data = {"content": "Visitando o Brasil!", "location": {"name": "Brasil"}}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.location is not None
        assert post.location.name == "Brasil"
        assert post.location.has_coordinates is False

    def test_create_post_without_location(self, authenticated_client, user):
        """Testa criar post sem location (campo opcional)."""
        url = reverse("post-list")

        data = {"content": "Post sem localização"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])
        assert post.location is None

    def test_create_post_reuses_existing_location(self, authenticated_client, user):
        """Testa que location existente é reutilizada."""
        # Criar location previamente
        existing_location = Location.objects.create(
            name="Paris", latitude=Decimal("48.858844"), longitude=Decimal("2.294351")
        )

        url = reverse("post-list")

        # Criar post com mesmas coordenadas
        data = {
            "content": "Post 1",
            "location": {
                "name": "Torre Eiffel",  # Nome diferente
                "latitude": "48.858844",
                "longitude": "2.294351",
            },
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        post = Post.objects.get(id=response.data["id"])

        # Deve usar location existente
        assert post.location.id == existing_location.id
        assert post.location.name == "Paris"  # Nome original mantido

        # Verificar que não criou location duplicada
        assert Location.objects.count() == 1

    def test_get_post_includes_location(self, api_client, user):
        """Testa que GET /posts/{id}/ inclui location."""
        location = Location.objects.create(
            name="São Paulo, Brasil",
            latitude=Decimal("-23.550520"),
            longitude=Decimal("-46.633308"),
        )

        post = Post.objects.create(
            author=user, content="Visitando SP!", location=location
        )

        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "location" in response.data
        assert response.data["location"] is not None
        assert response.data["location"]["name"] == "São Paulo, Brasil"
        assert response.data["location"]["has_coordinates"] is True

    def test_list_posts_includes_locations(self, api_client, user):
        """Testa que GET /posts/ inclui locations."""
        location = Location.objects.create(name="Paris")

        Post.objects.create(author=user, content="Post com location", location=location)

        url = reverse("post-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        post_data = response.data["results"][0]
        assert "location" in post_data
        assert post_data["location"]["name"] == "Paris"

    def test_create_post_with_invalid_location_coordinates(
        self, authenticated_client, user
    ):
        """Testa criar post com coordenadas inválidas."""
        url = reverse("post-list")

        # Latitude inválida
        data = {
            "content": "Test",
            "location": {"name": "Local", "latitude": "95.0", "longitude": "10.0"},
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_post_with_incomplete_coordinates(self, authenticated_client, user):
        """Testa criar post com coordenadas incompletas."""
        url = reverse("post-list")

        # Só latitude
        data = {"content": "Test", "location": {"name": "Local", "latitude": "10.0"}}

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "juntas" in str(response.data).lower()
