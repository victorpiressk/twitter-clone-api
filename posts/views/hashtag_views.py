"""
ViewSet para Hashtags.
"""

from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from posts.models import Hashtag
from posts.serializers import HashtagSerializer, PostSerializer


class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para hashtags (somente leitura).

    Hashtags são criadas automaticamente ao criar posts.
    """

    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Retorna queryset ordenado por popularidade."""
        return Hashtag.objects.all().order_by("-posts_count", "name")

    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        """
        Lista posts com uma hashtag específica.

        GET /api/hashtags/{id}/posts/
        GET /api/hashtags/{id}/posts/?limit=50
        """
        hashtag = self.get_object()

        limit = int(request.query_params.get("limit", 20))
        limit = min(limit, 100)

        # Posts publicados com essa hashtag
        posts = (
            hashtag.posts.filter(
                Q(scheduled_for__isnull=True) | Q(scheduled_for__lte=timezone.now())
            )
            .select_related("author")
            .prefetch_related("media", "poll", "location", "hashtags")
            .order_by("-created_at")[:limit]
        )

        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def trending(self, request):
        """
        Lista hashtags em trending com metadados.

        GET /api/hashtags/trending/
        GET /api/hashtags/trending/?period=week&limit=20

        Response inclui:
        - meta: período, total de hashtags, timestamp
        - results: hashtags com posts_count e recent_count
        """
        limit = int(request.query_params.get("limit", 10))
        limit = min(limit, 50)

        period = request.query_params.get("period", "all")

        queryset = Hashtag.objects.all()

        # Calcular data inicial do período
        start_date = None
        if period == "today":
            start_date = timezone.now() - timedelta(days=1)
        elif period == "week":
            start_date = timezone.now() - timedelta(days=7)
        elif period == "month":
            start_date = timezone.now() - timedelta(days=30)

        # Anotar com contagem de posts recentes se período != 'all'
        if start_date:
            queryset = (
                queryset.annotate(
                    recent_posts_count=Count(
                        "posts", filter=Q(posts__created_at__gte=start_date)
                    )
                )
                .filter(recent_posts_count__gt=0)
                .order_by("-recent_posts_count")
            )
        else:
            queryset = queryset.order_by("-posts_count")

        trending = queryset[:limit]

        # Serializar com metadados adicionais
        serializer = self.get_serializer(trending, many=True)

        # Adicionar metadados ao response
        return Response(
            {
                "meta": {
                    "period": period,
                    "limit": limit,
                    "total": trending.count(),
                    "generated_at": timezone.now().isoformat(),
                },
                "results": serializer.data,
            }
        )

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Busca hashtags por nome.

        GET /api/hashtags/search/?q=python
        """
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"detail": "Parâmetro 'q' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hashtags = Hashtag.objects.filter(name__icontains=query).order_by(
            "-posts_count"
        )[:20]

        serializer = self.get_serializer(hashtags, many=True)
        return Response(serializer.data)
