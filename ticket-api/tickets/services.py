"""Business rules for sending a ticket to the external provider.

Kept free of HTTP concerns: it raises provider exceptions, and the view maps
them to HTTP status codes.
"""
import logging

from .models import Ticket
from .providers import ProviderError, TicketProvider

logger = logging.getLogger("tickets")


def send_ticket(ticket: Ticket, provider: TicketProvider) -> Ticket:
    """Send `ticket` once and persist the outcome.

    - Already sent: return it unchanged without calling the provider.
    - Provider failure: re-raise; nothing is written, so the ticket stays
      `pending` with `external_id=None` and can be sent again later.
    - Success: store `external_id` and mark the ticket as `sent`.

    Only the ticket id and the outcome are logged (never email or description).
    """
    if ticket.status == Ticket.Status.SENT:
        logger.info("ticket_send ticket_id=%s result=already_sent", ticket.id)
        return ticket

    try:
        external_id = provider.send(ticket)
    except ProviderError as exc:
        logger.warning(
            "ticket_send ticket_id=%s result=failed reason=%s",
            ticket.id,
            type(exc).__name__,
        )
        raise

    ticket.external_id = external_id
    ticket.status = Ticket.Status.SENT
    ticket.save(update_fields=["external_id", "status"])
    logger.info(
        "ticket_send ticket_id=%s result=sent external_id=%s", ticket.id, external_id
    )
    return ticket
