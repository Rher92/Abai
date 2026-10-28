# Tasks: ABAI support-ticket API (Django + DRF + SQLite)

_Created: 2026-10-28 · Owner: Claude (for Roger Hernandez)_

Source: `~/Downloads/Prueba_tecnica_Backend_Python_ABAI.pdf` (ABAI Backend Engineer Python technical test).
Budget: max 4h effective work including README; deliver within 48h. One file per feature; work them in order.

| # | Feature file | Status |
|---|--------------|--------|
| 01 | [01-project-scaffold.md](01-project-scaffold.md) | [x] |
| 02 | [02-create-and-retrieve-ticket.md](02-create-and-retrieve-ticket.md) | [x] |
| 03 | [03-send-ticket-to-provider.md](03-send-ticket-to-provider.md) | [x] |
| 04 | [04-readme-and-delivery.md](04-readme-and-delivery.md) | [x] |
| 05 | [05-django-admin.md](05-django-admin.md) | [x] |
| 06 | [06-bilingual-commit-skill.md](06-bilingual-commit-skill.md) | [x] |

## Goal
A self-contained project in `ticket-api/` that a reviewer can install, migrate, run and test
locally with the exact commands in its README:
- `POST /tickets` → 201 with a `pending` ticket; invalid input → 400 (JSON error).
- `GET /tickets/{id}` → 200 or 404.
- `POST /tickets/{id}/send` → success 200 (`sent` + `external_id` persisted), timeout 504,
  error 502 (both keep `pending` / `external_id=null`), already `sent` → 200 without calling
  the provider, unknown id → 404.

## Shared assumptions
- Stack: Python 3.11+, Django 5.2 LTS, Django REST Framework, SQLite via the Django ORM; pinned in `ticket-api/requirements.txt`.
- DRF pattern: `GenericViewSet` + mixins + `@action`, on `SimpleRouter(trailing_slash=False)`.
- **Invalid input → HTTP 400**, used consistently (including malformed JSON).
- Every error uses the JSON shape `{"error": {"code", "message", "details"}}`.
- No auth: `AllowAny` set explicitly.
- Tests: pytest + pytest-django with an isolated test DB, focused on views, serializers, permissions and URLs.
- `ticket-api` has its own `pytest.ini`; the toolkit's root pytest config is untouched.
- README in English; it declares the AI assistance used.
- Git: **no commits** (user decision). Everything stays uncommitted.
