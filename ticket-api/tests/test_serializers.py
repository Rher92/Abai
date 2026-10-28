import pytest

from tickets.models import Ticket
from tickets.serializers import TicketCreateSerializer, TicketSerializer


def test_create_serializer_valid_payload_is_valid(valid_payload):
    serializer = TicketCreateSerializer(data=valid_payload)

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == valid_payload


def test_create_serializer_trims_outer_whitespace(valid_payload):
    payload = {**valid_payload, "subject": "  Hello  ", "description": "\n Body \t"}

    serializer = TicketCreateSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["subject"] == "Hello"
    assert serializer.validated_data["description"] == "Body"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("subject", ""),
        ("subject", "   "),
        ("subject", "x" * 121),
        ("description", ""),
        ("description", " \n\t "),
        ("description", "x" * 2001),
        ("email", "not-an-email"),
        ("email", "jane@"),
        ("email", ""),
        ("subject", None),
    ],
    ids=[
        "subject-empty",
        "subject-whitespace-only",
        "subject-too-long",
        "description-empty",
        "description-whitespace-only",
        "description-too-long",
        "email-no-at",
        "email-no-domain",
        "email-empty",
        "subject-null",
    ],
)
def test_create_serializer_rejects_invalid_field(valid_payload, field, value):
    serializer = TicketCreateSerializer(data={**valid_payload, field: value})

    assert not serializer.is_valid()
    assert list(serializer.errors) == [field]


@pytest.mark.parametrize(
    ("field", "value"),
    [("subject", "x" * 120), ("description", "x" * 2000), ("subject", "x")],
    ids=["subject-max", "description-max", "subject-min"],
)
def test_create_serializer_accepts_length_boundaries(valid_payload, field, value):
    serializer = TicketCreateSerializer(data={**valid_payload, field: value})

    assert serializer.is_valid(), serializer.errors


def test_create_serializer_length_is_checked_after_trimming(valid_payload):
    payload = {**valid_payload, "subject": "  " + "x" * 120 + "  "}

    serializer = TicketCreateSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors


@pytest.mark.parametrize("field", ["subject", "description", "email"])
def test_create_serializer_requires_field(valid_payload, field):
    payload = {k: v for k, v in valid_payload.items() if k != field}

    serializer = TicketCreateSerializer(data=payload)

    assert not serializer.is_valid()
    assert field in serializer.errors


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", "00000000-0000-0000-0000-000000000000"),
        ("status", "sent"),
        ("external_id", "EXT-1"),
        ("created_at", "2020-01-01T00:00:00Z"),
        ("priority", "high"),
    ],
)
def test_create_serializer_rejects_managed_or_unknown_fields(valid_payload, field, value):
    serializer = TicketCreateSerializer(data={**valid_payload, field: value})

    assert not serializer.is_valid()
    assert serializer.errors == {field: ["This field is not allowed."]}


def test_create_serializer_reports_unknown_and_invalid_fields_together(valid_payload):
    payload = {**valid_payload, "subject": "", "status": "sent"}

    serializer = TicketCreateSerializer(data=payload)

    assert not serializer.is_valid()
    assert set(serializer.errors) == {"subject", "status"}


def test_create_serializer_rejects_non_object_body():
    serializer = TicketCreateSerializer(data=["not", "an", "object"])

    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors


@pytest.mark.django_db
def test_create_serializer_save_persists_pending_ticket(valid_payload):
    serializer = TicketCreateSerializer(data=valid_payload)
    serializer.is_valid(raise_exception=True)

    ticket = serializer.save()

    stored = Ticket.objects.get(pk=ticket.pk)
    assert stored.status == Ticket.Status.PENDING
    assert stored.external_id is None
    assert stored.subject == valid_payload["subject"]


@pytest.mark.django_db
def test_ticket_serializer_outputs_all_model_fields_with_utc_timestamp(ticket):
    data = TicketSerializer(ticket).data

    assert set(data) == {
        "id",
        "subject",
        "description",
        "email",
        "status",
        "created_at",
        "external_id",
    }
    assert data["id"] == str(ticket.id)
    assert data["status"] == "pending"
    assert data["external_id"] is None
    assert data["created_at"].endswith("Z")


def test_ticket_serializer_is_read_only():
    serializer = TicketSerializer()

    assert all(field.read_only for field in serializer.fields.values())
