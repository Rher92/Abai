import uuid

from django.urls import resolve, reverse

from tickets.views import TicketViewSet

TICKET_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")


def test_ticket_list_route_is_tickets_without_trailing_slash():
    assert reverse("ticket-list") == "/tickets"


def test_ticket_detail_route_includes_id():
    assert reverse("ticket-detail", args=[TICKET_ID]) == f"/tickets/{TICKET_ID}"


def test_tickets_path_resolves_to_viewset_create():
    match = resolve("/tickets")

    assert match.func.cls is TicketViewSet
    assert match.func.actions == {"post": "create"}


def test_ticket_detail_path_resolves_to_viewset_retrieve():
    match = resolve(f"/tickets/{TICKET_ID}")

    assert match.func.cls is TicketViewSet
    assert match.func.actions["get"] == "retrieve"
    assert match.kwargs == {"pk": str(TICKET_ID)}


def test_ticket_send_route_is_nested_under_ticket():
    assert reverse("ticket-send", args=[TICKET_ID]) == f"/tickets/{TICKET_ID}/send"


def test_ticket_send_path_resolves_to_send_action_post_only():
    match = resolve(f"/tickets/{TICKET_ID}/send")

    assert match.func.cls is TicketViewSet
    assert match.func.actions == {"post": "send"}
