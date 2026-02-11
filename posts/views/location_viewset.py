"""
Location ViewSet.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from posts.models import Location
from posts.serializers import LocationSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para localizações.
    
    list: Lista todas as localizações
    retrieve: Detalhes de uma localização
    search: Busca localizações por nome
    nearby: Busca localizações próximas (requer coordenadas)
    """
    
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Busca localizações por nome.
        
        Query params:
        - q: termo de busca (obrigatório)
        
        Exemplo: GET /api/locations/search/?q=paris
        """
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {"detail": "Parâmetro 'q' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Busca case-insensitive no nome
        locations = Location.objects.filter(
            name__icontains=query
        ).order_by('name')[:10]  # Limitar a 10 resultados
        
        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Busca localizações próximas a uma coordenada.
        
        Query params:
        - lat: latitude (obrigatório)
        - lng: longitude (obrigatório)
        - radius: raio em km (padrão: 10)
        
        Exemplo: GET /api/locations/nearby/?lat=-23.5505&lng=-46.6333&radius=5
        
        Nota: Esta é uma implementação simples. Para produção,
        considere usar PostGIS para queries geoespaciais eficientes.
        """
        try:
            latitude = float(request.query_params.get('lat', 0))
            longitude = float(request.query_params.get('lng', 0))
            radius_km = float(request.query_params.get('radius', 10))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Parâmetros inválidos. Use: lat, lng (números), radius (opcional)."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return Response(
                {"detail": "Coordenadas inválidas. Lat: -90 a 90, Lng: -180 a 180."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cálculo aproximado de distância (em graus)
        # 1 grau ≈ 111 km
        # Esta é uma aproximação simples, não considera a curvatura da Terra
        delta = radius_km / 111.0
        
        # Buscar localizações dentro do "quadrado" aproximado
        locations = Location.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__gte=latitude - delta,
            latitude__lte=latitude + delta,
            longitude__gte=longitude - delta,
            longitude__lte=longitude + delta
        )[:20]  # Limitar a 20 resultados
        
        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)
