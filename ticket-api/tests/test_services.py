import logging

import pytest

from tests.fakes import FakeProvider
from tickets.models import Ticket
from tickets.providers import ProviderTimeout, ProviderUnavailable
from tickets.services import send_ticket

pytestmark = pytest.mark.django_db


def test_send_ticket_success_persists_sent_status_and_external_id(ticket):
    provider = FakeProvider(result="EXT-123")

    result = send_ticket(ticket, provider)

    assert result.status == Ticket.Status.SENT
    stored = Ticket.objects.get(pk=ticket.pk)
    assert stored.status == Ticket.Status.SENT
    assert stored.external_id == "EXT-123"
    assert provider.calls == [ticket.id]


@pytest.mark.parametrize("error", [ProviderTimeout(), ProviderUnavailable()])
def test_send_ticket_failure_reraises_and_keeps_ticket_pending(ticket, error):
    provider = FakeProvider(error=error)

    with pytest.raises(type(error)):
        send_ticket(ticket, provider)

    stored = Ticket.objects.get(pk=ticket.pk)
    assert stored.status == Ticket.Status.PENDING
    assert stored.external_id is None


def test_send_ticket_already_sent_does_not_call_provider(ticket):
    ticket.status = Ticket.Status.SENT
    ticket.external_id = "EXT-ORIGINAL"
    ticket.save()
    provider = FakeProvider(result="EXT-NEW")

    result = send_ticket(ticket, provider)

    assert provider.calls == []
    assert Ticket.objects.get(pk=ticket.pk).external_id == "EXT-ORIGINAL"
    assert result.external_id == "EXT-ORIGINAL"


def test_send_ticket_can_succeed_after_a_failure(ticket):
    with pytest.raises(ProviderUnavailable):
        send_ticket(ticket, FakeProvider(error=ProviderUnavailable()))

    send_ticket(ticket, FakeProvider(result="EXT-RETRY"))

    stored = Ticket.objects.get(pk=ticket.pk)
    assert stored.status == Ticket.Status.SENT
    assert stored.external_id == "EXT-RETRY"


@pytest.mark.parametrize(
    ("provider", "outcome"),
    [
        (FakeProvider(result="EXT-LOG"), "result=sent"),
        (FakeProvider(error=ProviderTimeout()), "result=failed reason=ProviderTimeout"),
        (FakeProvider(error=ProviderUnavailable()), "result=failed reason=ProviderUnavailable"),
    ],
    ids=["sent", "timeout", "error"],
)
def test_send_ticket_logs_id_and_outcome_without_personal_data(ticket, caplog, provider, outcome):
    caplog.set_level(logging.INFO, logger="tickets")

    try:
        send_ticket(ticket, provider)
    except Exception:
        pass

    assert f"ticket_id={ticket.id}" in caplog.text
    assert outcome in caplog.text
    assert ticket.email not in caplog.text
    assert ticket.description not in caplog.text
