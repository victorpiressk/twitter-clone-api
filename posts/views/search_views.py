"""
ViewSet para busca global.
"""

from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from posts.models import Hashtag, Post
from posts.serializers import HashtagSerializer, PostSerializer
from users.serializers import UserSerializer

User = get_user_model()


class SearchViewSet(viewsets.ViewSet):
    """
    ViewSet para busca global.

    Endpoint único que busca em posts, users e hashtags.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=["get"])
    def all(self, request):
        """
        Busca global.

        GET /api/search/all/?q=python
        GET /api/search/all/?q=python&limit=10
        """
        query = request.query_params.get("q", "").strip()

        # Validar query
        if not query:
            return Response(
                {"detail": "Parâmetro 'q' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(query) < 2:
            return Response(
                {"detail": "Busca deve ter no mínimo 2 caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Pegar limite
        limit = int(request.query_params.get("limit", 5))
        limit = min(limit, 20)  # Máximo 20 por tipo

        # 1. BUSCAR POSTS (content ou hashtags)
        posts = (
            Post.objects.published()
            .filter(Q(content__icontains=query) | Q(hashtags__name__icontains=query))
            .distinct()
            .select_related("author")
            .prefetch_related("media", "poll", "location", "hashtags")
            .order_by("-created_at")[:limit]
        )

        # 2. BUSCAR USUÁRIOS (username, nome, bio)
        users = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(bio__icontains=query)
        ).order_by("username")[:limit]

        # 3. BUSCAR HASHTAGS (name)
        hashtags = Hashtag.objects.filter(name__icontains=query).order_by(
            "-posts_count"
        )[:limit]

        # Serializar
        posts_data = PostSerializer(posts, many=True, context={"request": request}).data

        users_data = UserSerializer(users, many=True).data
        hashtags_data = HashtagSerializer(hashtags, many=True).data

        # Retornar agregado
        return Response(
            {
                "posts": posts_data,
                "users": users_data,
                "hashtags": hashtags_data,
                "meta": {
                    "query": query,
                    "total_results": len(posts_data)
                    + len(users_data)
                    + len(hashtags_data),
                },
            }
        )
