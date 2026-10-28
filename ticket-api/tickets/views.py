import logging

from django.http import Http404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .exceptions import ProviderTimeoutError, ProviderUnavailableError
from .models import Ticket
from .providers import ProviderError, ProviderTimeout, TicketProvider, get_provider
from .serializers import TicketCreateSerializer, TicketSerializer
from .services import send_ticket

logger = logging.getLogger("tickets")


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """POST /tickets, GET /tickets/{id} and POST /tickets/{id}/send.

    Listing, editing and deleting are out of scope, so those mixins are
    deliberately not included (the router answers 405 for them).
    """

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "create":
            return TicketCreateSerializer
        return TicketSerializer

    def get_object(self) -> Ticket:
        try:
            return super().get_object()
        except Http404:
            raise NotFound("Ticket not found.") from None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        logger.info("ticket_created ticket_id=%s", ticket.id)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    def get_provider(self) -> TicketProvider:
        """Hook to swap the provider (tests override this)."""
        return get_provider()

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        ticket = self.get_object()
        try:
            ticket = send_ticket(ticket, self.get_provider())
        except ProviderTimeout:
            raise ProviderTimeoutError() from None
        except ProviderError:
            raise ProviderUnavailableError() from None
        return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)
