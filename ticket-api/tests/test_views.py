import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from tickets.models import Ticket
from tickets.providers import ProviderTimeout, ProviderUnavailable

pytestmark = pytest.mark.django_db

UNKNOWN_ID = "00000000-0000-4000-8000-000000000000"


# --- POST /tickets ---------------------------------------------------------


def test_create_ticket_returns_201_with_pending_ticket(api_client, valid_payload):
    response = api_client.post("/tickets", valid_payload, format="json")

    assert response.status_code == 201
    body = response.json()
    assert body["subject"] == valid_payload["subject"]
    assert body["description"] == valid_payload["description"]
    assert body["email"] == valid_payload["email"]
    assert body["status"] == "pending"
    assert body["external_id"] is None
    uuid.UUID(body["id"])  # backend-generated UUID


def test_create_ticket_persists_row(api_client, valid_payload):
    response = api_client.post("/tickets", valid_payload, format="json")

    stored = Ticket.objects.get(pk=response.json()["id"])
    assert stored.status == Ticket.Status.PENDING
    assert stored.external_id is None
    assert stored.email == valid_payload["email"]
    assert abs(timezone.now() - stored.created_at) < timedelta(minutes=1)


def test_create_ticket_stores_trimmed_values(api_client, valid_payload):
    payload = {**valid_payload, "subject": "  Padded subject  "}

    response = api_client.post("/tickets", payload, format="json")

    assert response.json()["subject"] == "Padded subject"
    assert Ticket.objects.get().subject == "Padded subject"


def test_create_ticket_with_invalid_data_returns_400_and_creates_nothing(api_client):
    payload = {"subject": "   ", "description": "x" * 2001, "email": "nope"}

    response = api_client.post("/tickets", payload, format="json")

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "invalid_input"
    assert set(error["details"]) == {"subject", "description", "email"}
    assert Ticket.objects.count() == 0


def test_create_ticket_cannot_set_backend_managed_fields(api_client, valid_payload):
    payload = {**valid_payload, "status": "sent", "external_id": "EXT-FAKE"}

    response = api_client.post("/tickets", payload, format="json")

    assert response.status_code == 400
    assert set(response.json()["error"]["details"]) == {"status", "external_id"}
    assert Ticket.objects.count() == 0


def test_create_ticket_with_malformed_json_returns_400(api_client):
    response = api_client.post(
        "/tickets", data='{"subject": ', content_type="application/json"
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "parse_error"


def test_create_ticket_with_non_json_body_returns_415_and_creates_nothing(api_client):
    # What `curl -d 'subject=x'` sends by default.
    response = api_client.post(
        "/tickets", data="subject=x", content_type="application/x-www-form-urlencoded"
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_media_type"
    assert Ticket.objects.count() == 0


def test_create_ticket_with_empty_body_returns_400(api_client):
    response = api_client.post("/tickets", {}, format="json")

    assert response.status_code == 400
    assert set(response.json()["error"]["details"]) == {"subject", "description", "email"}


# --- GET /tickets/{id} -----------------------------------------------------


def test_get_ticket_returns_persisted_ticket(api_client, valid_payload):
    created = api_client.post("/tickets", valid_payload, format="json").json()

    response = api_client.get(f"/tickets/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_unknown_ticket_returns_404(api_client):
    response = api_client.get(f"/tickets/{UNKNOWN_ID}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Ticket not found.", "details": None}
    }


def test_get_ticket_with_malformed_id_returns_404(api_client):
    response = api_client.get("/tickets/not-a-uuid")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


# --- POST /tickets/{id}/send ----------------------------------------------


def _send(api_client, ticket_id):
    return api_client.post(f"/tickets/{ticket_id}/send")


def test_send_ticket_success_returns_200_and_persists_state(api_client, ticket, fake_provider):
    fake_provider.result = "EXT-OK-1"

    response = _send(api_client, ticket.id)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "sent"
    assert body["external_id"] == "EXT-OK-1"
    assert body["id"] == str(ticket.id)
    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.SENT
    assert ticket.external_id == "EXT-OK-1"
    # The persisted state is what GET returns too.
    assert api_client.get(f"/tickets/{ticket.id}").json() == body


@pytest.mark.parametrize(
    ("error", "status_code", "code"),
    [
        (ProviderTimeout(), 504, "provider_timeout"),
        (ProviderUnavailable(), 502, "provider_unavailable"),
    ],
    ids=["timeout", "error"],
)
def test_send_ticket_provider_failure_keeps_ticket_pending(
    api_client, ticket, fake_provider, error, status_code, code
):
    fake_provider.error = error

    response = _send(api_client, ticket.id)

    assert response.status_code == status_code
    assert response.json()["error"]["code"] == code
    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.PENDING
    assert ticket.external_id is None


def test_send_ticket_retry_after_failure_succeeds(api_client, ticket, fake_provider):
    fake_provider.error = ProviderTimeout()
    assert _send(api_client, ticket.id).status_code == 504

    fake_provider.error = None
    fake_provider.result = "EXT-RETRY"
    response = _send(api_client, ticket.id)

    assert response.status_code == 200
    assert response.json()["external_id"] == "EXT-RETRY"
    assert len(fake_provider.calls) == 2
    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.SENT


def test_send_already_sent_ticket_returns_200_without_calling_provider(
    api_client, ticket, fake_provider
):
    first = _send(api_client, ticket.id).json()

    second = _send(api_client, ticket.id)

    assert second.status_code == 200
    assert second.json() == first
    assert fake_provider.calls == [ticket.id]


def test_send_unknown_ticket_returns_404_without_calling_provider(api_client, fake_provider):
    response = _send(api_client, UNKNOWN_ID)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert fake_provider.calls == []


def test_send_uses_mode_from_settings_end_to_end(api_client, ticket, settings):
    """Real SimulatedProvider, mode switched like an operator would via config."""
    settings.TICKET_PROVIDER_MODE = "error"
    assert _send(api_client, ticket.id).status_code == 502

    settings.TICKET_PROVIDER_MODE = "timeout"
    assert _send(api_client, ticket.id).status_code == 504

    settings.TICKET_PROVIDER_MODE = "success"
    response = _send(api_client, ticket.id)

    assert response.status_code == 200
    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.SENT
    assert ticket.external_id == response.json()["external_id"]
    assert ticket.external_id.startswith("EXT-")
