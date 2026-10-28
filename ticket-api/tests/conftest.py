import pytest
from rest_framework.test import APIClient

from tests.fakes import FakeProvider
from tickets.models import Ticket


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def valid_payload() -> dict:
    # Fictitious data only.
    return {
        "subject": "Cannot log in",
        "description": "The login page returns an error after submitting the form.",
        "email": "jane.doe@example.com",
    }


@pytest.fixture
def ticket(db, valid_payload) -> Ticket:
    return Ticket.objects.create(**valid_payload)


@pytest.fixture
def fake_provider(monkeypatch) -> FakeProvider:
    """Inject a FakeProvider into the view through its `get_provider` hook."""
    from tickets.views import TicketViewSet

    provider = FakeProvider()
    monkeypatch.setattr(TicketViewSet, "get_provider", lambda self: provider)
    return provider
