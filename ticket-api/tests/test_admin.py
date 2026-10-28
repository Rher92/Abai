import pytest
from django.contrib import admin
from django.urls import reverse
from rest_framework.test import APIClient

from tickets.admin import TicketAdmin
from tickets.models import Ticket

pytestmark = pytest.mark.django_db


def test_ticket_model_is_registered_in_admin():
    assert isinstance(admin.site._registry.get(Ticket), TicketAdmin)


def test_admin_managed_fields_are_read_only():
    assert set(TicketAdmin.readonly_fields) == {"id", "status", "external_id", "created_at"}


def test_admin_index_redirects_anonymous_user_to_login(client):
    response = client.get("/admin/")

    assert response.status_code == 302
    assert response.url.startswith("/admin/login/")


def test_admin_ticket_changelist_lists_tickets(admin_client, ticket):
    response = admin_client.get(reverse("admin:tickets_ticket_changelist"))

    assert response.status_code == 200
    assert ticket.subject in response.content.decode()


def test_admin_ticket_changelist_filters_by_status(admin_client, ticket):
    response = admin_client.get(
        reverse("admin:tickets_ticket_changelist"), {"status__exact": "sent"}
    )

    assert response.status_code == 200
    assert ticket.subject not in response.content.decode()


def test_admin_ticket_change_page_loads(admin_client, ticket):
    response = admin_client.get(reverse("admin:tickets_ticket_change", args=[ticket.pk]))

    assert response.status_code == 200


def test_admin_cannot_change_managed_fields(admin_client, ticket):
    url = reverse("admin:tickets_ticket_change", args=[ticket.pk])
    form = {
        "subject": "Edited by staff",
        "description": ticket.description,
        "email": ticket.email,
        "status": "sent",
        "external_id": "EXT-FORGED",
    }

    response = admin_client.post(url, form)

    assert response.status_code == 302
    ticket.refresh_from_db()
    assert ticket.subject == "Edited by staff"
    assert ticket.status == Ticket.Status.PENDING
    assert ticket.external_id is None


def test_admin_add_creates_pending_ticket(admin_client):
    form = {"subject": "  From admin  ", "description": "Created by staff.", "email": "staff@example.com"}

    response = admin_client.post(reverse("admin:tickets_ticket_add"), form)

    assert response.status_code == 302
    created = Ticket.objects.get()
    assert created.subject == "From admin"
    assert created.status == Ticket.Status.PENDING


def test_api_post_still_works_with_admin_session_cookie(admin_user, valid_payload):
    """Logging into the admin must not make the API require CSRF tokens."""
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin_user)

    response = client.post("/tickets", valid_payload, format="json")

    assert response.status_code == 201
