"""
Poll ViewSet.

Criar arquivo: posts/views/poll_views.py
"""

from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from posts.models import Poll, PollVote
from posts.serializers import (
    PollResultsSerializer,
    PollSerializer,
    PollVoteSerializer,
    PostSerializer,
)


class PollViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para enquetes.

    list: Lista todas as enquetes
    retrieve: Detalhes de uma enquete
    vote: Votar em uma enquete
    results: Ver resultados de uma enquete
    """

    queryset = Poll.objects.all().prefetch_related("options")
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        """
        Votar em uma enquete.

        Body: {"option_id": 1}
        """
        poll = self.get_object()

        serializer = PollVoteSerializer(
            data=request.data, context={"request": request, "poll": poll}
        )
        serializer.is_valid(raise_exception=True)

        # Criar voto e incrementar contador atomicamente
        with transaction.atomic():
            serializer.save()

        # Retornar enquete atualizada
        poll.refresh_from_db()
        output_serializer = PollSerializer(poll, context={"request": request})

        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def results(self, request, pk=None):
        """
        Ver resultados da enquete.

        Retorna a enquete com todas as opções e porcentagens.
        """
        poll = self.get_object()
        serializer = PollResultsSerializer(poll)
        return Response(serializer.data)

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def unvote(self, request, pk=None):
        """
        Desfazer voto em enquete (antes de terminar).

        Permite que usuário mude de opinião.
        """
        poll = self.get_object()

        # Verificar se enquete terminou
        if poll.is_ended:
            return Response(
                {"detail": "Não é possível desfazer voto em enquete encerrada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Buscar voto do usuário
        try:
            vote = PollVote.objects.get(poll=poll, user=request.user)
        except PollVote.DoesNotExist:
            return Response(
                {"detail": "Você não votou nesta enquete."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Deletar voto e decrementar contador atomicamente
        with transaction.atomic():
            option = vote.option
            vote.delete()

            # Decrementar contador
            if option.votes > 0:
                option.votes -= 1
                option.save(update_fields=["votes"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    """
    3. Modificar método create() existente para suportar polls:
    """

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve create para retornar PostSerializer na resposta.
        Suporta criação de posts com enquetes.
        """
        # Se tem poll no body, usar método específico
        if "poll" in request.data:
            return self.create_with_poll(request, *args, **kwargs)

        # Lógica normal (já existente)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        instance = serializer.instance
        output_serializer = PostSerializer(instance, context={"request": request})
        headers = self.get_success_headers(output_serializer.data)

        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
