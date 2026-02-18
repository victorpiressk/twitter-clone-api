"""
ViewSet para Notificações.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from posts.models import Notification
from posts.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para notificações (somente leitura + actions).

    Usuário só vê próprias notificações.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna notificações do usuário autenticado.

        Ordenação: não lidas primeiro, depois por data.
        """
        return (
            Notification.objects.filter(recipient=self.request.user)
            .select_related("actor", "post__author")
            .order_by("is_read", "-created_at")
        )

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """
        Lista apenas notificações não lidas.

        GET /api/notifications/unread/
        """
        unread_notifications = self.get_queryset().filter(is_read=False)

        page = self.paginate_queryset(unread_notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """
        Contador de notificações não lidas.

        GET /api/notifications/unread-count/
        Response: {"count": 5}
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        """
        Marca uma notificação como lida.

        POST /api/notifications/{id}/read/
        """
        notification = self.get_object()

        if notification.recipient != request.user:
            return Response(
                {"detail": "Você não tem permissão para marcar esta notificação."},
                status=status.HTTP_403_FORBIDDEN,
            )

        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        """
        Marca todas as notificações como lidas.

        POST /api/notifications/read-all/
        Response: {"updated": 10}
        """
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"updated": updated})
