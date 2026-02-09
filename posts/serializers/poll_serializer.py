"""
Poll serializers.
"""

from rest_framework import serializers

from posts.models import Poll, PollOption, PollVote


class PollOptionSerializer(serializers.ModelSerializer):
    """
    Serializer para opções de enquete.
    """

    percentage = serializers.ReadOnlyField()

    class Meta:
        model = PollOption
        fields = [
            "id",
            "text",
            "votes",
            "percentage",
            "order",
        ]
        read_only_fields = ["id", "votes", "percentage"]


class PollSerializer(serializers.ModelSerializer):
    """
    Serializer para enquetes.
    """

    options = PollOptionSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField()
    is_ended = serializers.ReadOnlyField()
    user_voted_option_id = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            "id",
            "question",
            "duration_hours",
            "ends_at",
            "options",
            "total_votes",
            "is_ended",
            "user_voted_option_id",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "ends_at",
            "total_votes",
            "is_ended",
            "user_voted_option_id",
            "created_at",
        ]

    def get_user_voted_option_id(self, obj):
        """
        Retorna o ID da opção que o usuário votou (se votou).
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        try:
            vote = PollVote.objects.get(poll=obj, user=request.user)
            return vote.option.id
        except PollVote.DoesNotExist:
            return None


class PollCreateSerializer(serializers.Serializer):
    """
    Serializer para criação de enquetes.

    Aceita a pergunta, duração e lista de opções.
    """

    question = serializers.CharField(
        max_length=280,
        required=False,
        allow_blank=True,
        help_text="Pergunta da enquete (opcional)",
    )

    duration_hours = serializers.IntegerField(
        default=24,
        min_value=1,
        max_value=168,  # Máximo 7 dias
        help_text="Duração da enquete em horas (1-168)",
    )

    options = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=2,
        max_length=4,
        help_text="Lista de opções (2-4 opções)",
    )

    def validate_options(self, value):
        """Valida que as opções não são duplicadas."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "As opções da enquete não podem ser duplicadas."
            )
        return value

    def create(self, validated_data):
        """
        Cria a enquete e suas opções.

        Espera que 'post' seja passado no contexto ou validated_data.
        """
        post = validated_data.pop("post", None) or self.context.get("post")
        if not post:
            raise serializers.ValidationError("Post é obrigatório para criar enquete.")

        options_data = validated_data.pop("options")

        # Criar enquete
        poll = Poll.objects.create(post=post, **validated_data)

        # Criar opções
        for index, option_text in enumerate(options_data):
            PollOption.objects.create(poll=poll, text=option_text, order=index)

        return poll


class PollVoteSerializer(serializers.Serializer):
    """
    Serializer para votar em enquete.
    """

    option_id = serializers.IntegerField(help_text="ID da opção escolhida")

    def validate_option_id(self, value):
        """Valida que a opção existe."""
        try:
            option = PollOption.objects.get(id=value)
            self.context["option"] = option
            return value
        except PollOption.DoesNotExist:
            raise serializers.ValidationError("Opção não encontrada.")

    def validate(self, data):
        """Valida que a enquete não terminou e usuário não votou."""
        option = self.context.get("option")
        poll = option.poll
        request = self.context.get("request")

        # Verificar se enquete terminou
        if poll.is_ended:
            raise serializers.ValidationError("Esta enquete já foi encerrada.")

        # Verificar se usuário já votou
        if PollVote.objects.filter(poll=poll, user=request.user).exists():
            raise serializers.ValidationError("Você já votou nesta enquete.")

        return data

    def create(self, validated_data):
        """Cria o voto e incrementa contador."""
        option = self.context["option"]
        user = self.context["request"].user

        # Criar voto
        vote = PollVote.objects.create(poll=option.poll, user=user, option=option)

        # Incrementar contador da opção
        option.votes += 1
        option.save(update_fields=["votes"])

        return vote


class PollResultsSerializer(serializers.ModelSerializer):
    """
    Serializer para resultados da enquete.

    Similar ao PollSerializer mas otimizado para exibir resultados.
    """

    options = PollOptionSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField()
    is_ended = serializers.ReadOnlyField()

    class Meta:
        model = Poll
        fields = [
            "id",
            "question",
            "ends_at",
            "options",
            "total_votes",
            "is_ended",
        ]
