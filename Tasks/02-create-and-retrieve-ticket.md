# Feature 02: Create and retrieve tickets

`POST /tickets` (201 / 400) and `GET /tickets/{id}` (200 / 404), persisted in SQLite.

depends: Feature 01

## Assumptions
- `id` is a backend-generated UUID4; `status` is `pending|sent` (default `pending`); `external_id` is null until sent.
- `subject` (1–120) and `description` (1–2000) are trimmed before validation; `email` is validated by DRF `EmailField`.
- Unknown fields and backend-managed fields in the create body are **rejected with 400**, not silently ignored.
- The response always includes all model fields: `id, subject, description, email, status, created_at, external_id`.

## Tasks
<!-- [ ] todo · [~] in progress (only one) · [x] done · [!] blocked: reason -->
- [x] T1 `tickets/models.py::Ticket` + initial migration
      accept: `python manage.py migrate` creates the DB; `makemigrations --check` is clean
- [x] T2 `tickets/serializers.py`: `TicketCreateSerializer` (input) + `TicketSerializer` (output)   depends: T1
      accept: `tests/test_serializers.py`: valid, trimming, blank/whitespace-only, too long, bad email, unknown/managed fields
- [x] T3 `tickets/exceptions.py::api_exception_handler` → `{"error": {"code","message","details"}}`, wired in `REST_FRAMEWORK`
      accept: 400 and 404 bodies have this shape (asserted in view tests)
- [x] T4 `tickets/views.py::TicketViewSet` (Create + Retrieve mixins, `AllowAny`) + `tickets/urls.py` (`SimpleRouter(trailing_slash=False)`)   depends: T2, T3
      accept: `tests/test_urls.py` (reverse/resolve), `tests/test_permissions.py` (anonymous OK; 405 on list/PUT/PATCH/DELETE)
- [x] T5 `tests/test_views.py`: create → row in DB + 201 body; get → 200 same data; invalid → 400 with no row created; malformed JSON → 400; unknown id → 404   depends: T4
      accept: `pytest -q` green

## Notes
- Router also maps HEAD to retrieve; URL test asserts only the GET mapping.
- `get_object()` turns Http404 into `NotFound("Ticket not found.")` so 404 messages name the resource (also covers malformed UUIDs).
- Unhandled exceptions also return the JSON error shape (500 `server_error`), logging only the exception type.
- 48 tests green.
