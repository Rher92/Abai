import pytest
from rest_framework.permissions import AllowAny

from tickets.views import TicketViewSet


def test_ticket_viewset_allows_anonymous_access():
    assert TicketViewSet.permission_classes == [AllowAny]


@pytest.mark.django_db
def test_anonymous_client_can_create_and_read_ticket(api_client, valid_payload):
    created = api_client.post("/tickets", valid_payload, format="json")
    fetched = api_client.get(f"/tickets/{created.data['id']}")

    assert created.status_code == 201
    assert fetched.status_code == 200


@pytest.mark.django_db
def test_listing_tickets_is_not_allowed(api_client, ticket):
    response = api_client.get("/tickets")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["put", "patch", "delete"])
def test_editing_or_deleting_ticket_is_not_allowed(api_client, ticket, method):
    response = getattr(api_client, method)(
        f"/tickets/{ticket.id}", {"subject": "changed"}, format="json"
    )

    assert response.status_code == 405
    ticket.refresh_from_db()
    assert ticket.subject != "changed"


@pytest.mark.django_db
def test_anonymous_client_can_send_ticket(api_client, ticket, fake_provider):
    response = api_client.post(f"/tickets/{ticket.id}/send")

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_on_send_route_is_not_allowed(api_client, ticket, fake_provider):
    response = api_client.get(f"/tickets/{ticket.id}/send")

    assert response.status_code == 405
    assert fake_provider.calls == []
