# Abai

This repository has two parts:

| Part | Where | What it is |
|------|-------|------------|
| [Agent toolkit](#agent-toolkit) | repo root | AI-agnostic skills, and shared agent memory (`.agents/AGENTS.md`) kept fresh by a git hook |
| [Ticket API](#ticket-api) | `ticket-api/` | Django REST Framework service for support tickets (ABAI technical test) |

Each part has its own virtualenv and test suite. Root `python -m pytest -q` runs only the toolkit tests;
run the Ticket API tests from inside `ticket-api/`.

## Agent toolkit

Works with any AI coding agent (Claude Code, Codex, Gemini CLI, Copilot, Cursor, local models).

| Piece | Where | What it does |
|-------|-------|--------------|
| Task breakdown skill | `.agents/skills/task-breakdown/` | Plan work into `Tasks/<nn-feature>.md`, execute task by task |
| Pytest skill | `.agents/skills/pytest-unittest/` | Write isolated, deterministic pytest unit tests |
| Bilingual commit skill | `.agents/skills/bilingual-commit/` | Read the staged diff and write an English + Spanish commit message for non-technical readers, with no agent signature |
| AI memory | `.agents/AGENTS.md` (single file; root `AGENTS.md` and `.claude/CLAUDE.md` are symlinks to it) | Shared context for every agent |
| Memory hook | `.githooks/pre-commit` | Rewrites `.agents/AGENTS.md`'s AUTO block on **every commit** |

### Setup
```bash
./scripts/install.sh
```

### Optional AI
The hook works without AI. To have an AI write the AGENTS.md summary, set a CLI
that reads a prompt from stdin, e.g. `export AI_CLI="claude -p"`, `"codex exec -"`,
`"gemini"`, or `"ollama run llama3"`.

## Ticket API

A small Django REST Framework service that registers customer-support tickets,
returns their state, and sends them to a simulated external provider.

- Python 3.11+ · Django 5.2 LTS · Django REST Framework 3.16 · SQLite (local file)
- Tests: pytest + pytest-django

All commands and paths in this section are relative to `ticket-api/`.

### Install

Requires **Python 3.11 or newer**. Check with `python3 --version`; if it is older, call a specific
interpreter instead, for example `python3.12 -m venv .venv`.

```bash
cd ticket-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt     # runtime deps only: requirements.txt
```

### Initialise the database

```bash
python manage.py migrate
```

This creates `db.sqlite3` in `ticket-api/`. Set `TICKETS_DB_PATH=/path/to/file.sqlite3`
to use another file. Data survives server restarts.

### Run

```bash
python manage.py runserver 8000                           # provider mode: success (default)
TICKET_PROVIDER_MODE=timeout python manage.py runserver 8000
TICKET_PROVIDER_MODE=error   python manage.py runserver 8000
```

The mode is read from the environment when the server starts. To switch modes,
stop the server and start it again with another value. Tickets are kept.

### Admin

The Django admin at <http://localhost:8000/admin/> lists, searches and filters tickets by status.
Create a user first (after `migrate`):

```bash
python manage.py createsuperuser
```

In the admin, `subject`, `description` and `email` can be edited. `id`, `status`, `external_id` and
`created_at` are read-only, because only the send flow may change a ticket's state.

#### Configuration

All variables are optional; see `.env.example`. No real credentials are used.

| Variable | Default | Purpose |
|----------|---------|---------|
| `TICKET_PROVIDER_MODE` | `success` | Simulated provider: `success`, `timeout` or `error` |
| `TICKETS_DB_PATH` | `./db.sqlite3` | SQLite file |
| `DJANGO_SECRET_KEY` | dev placeholder | Django secret (development value only) |
| `DJANGO_DEBUG` | `1` | Django debug mode |

### Run the tests

```bash
cd ticket-api && python -m pytest -q
```

Tests use pytest-django's isolated test database, so they don't depend on `db.sqlite3` or on earlier runs.

### API

All bodies are JSON. Invalid input always returns **HTTP 400**. A body that is not JSON returns **HTTP 415**.

| Method & path | Success | Errors |
|---------------|---------|--------|
| `POST /tickets` | 201 + ticket | 400 invalid input · 415 non-JSON body |
| `GET /tickets/{id}` | 200 + ticket | 404 |
| `POST /tickets/{id}/send` | 200 + ticket | 404 · 502 provider error · 504 provider timeout |

Ticket representation:

```json
{
  "id": "1e6371bc-de1b-4e35-804c-b4069c7520fb",
  "subject": "Cannot log in",
  "description": "Login page fails.",
  "email": "jane.doe@example.com",
  "status": "pending",
  "created_at": "2026-10-28T11:04:41.793882Z",
  "external_id": null
}
```

Every error uses the same shape:

```json
{"error": {"code": "invalid_input", "message": "Invalid input.", "details": {"email": ["Enter a valid email address."]}}}
```

Codes: `invalid_input`, `parse_error` (malformed JSON), `unsupported_media_type` (non-JSON body),
`not_found`, `method_not_allowed`, `provider_timeout`, `provider_unavailable`, `server_error`.

#### Examples

Start the server first (`python manage.py runserver 8000`). Add `-i` to any command to see the status line.

If `jq` fails with `parse error: Invalid numeric literal`, the response was HTML, not JSON: another app is
probably running on port 8000 (check with `lsof -nP -iTCP:8000 -sTCP:LISTEN`). Start this server on a free port
instead (`python manage.py runserver 8001`) and use `localhost:8001` in the commands.

```bash
# Create
curl -s -X POST localhost:8000/tickets \
  -H 'Content-Type: application/json' \
  -d '{"subject": "Cannot log in", "description": "Login page fails.", "email": "jane.doe@example.com"}'
# 201 {"id": "<id>", ..., "status": "pending", "external_id": null}

# Create and keep the id for the next commands (needs jq)
ID=$(curl -s -X POST localhost:8000/tickets \
  -H 'Content-Type: application/json' \
  -d '{"subject": "Cannot log in", "description": "Login page fails.", "email": "jane.doe@example.com"}' | jq -r .id)

# Read
curl -s localhost:8000/tickets/$ID
# 200 {...}

# Send
curl -s -X POST localhost:8000/tickets/$ID/send
# success: 200 {..., "status": "sent", "external_id": "EXT-86F0F654A33B"}
# already sent: 200 with the stored ticket; the provider is not called again
```

Error cases:

```bash
# Invalid input: blank subject, bad email, and a field the client may not set
curl -s -X POST localhost:8000/tickets -H 'Content-Type: application/json' \
  -d '{"subject": " ", "description": "x", "email": "bad", "status": "sent"}'
# 400 {"error": {"code": "invalid_input", "details": {"subject": [...], "email": [...], "status": ["This field is not allowed."]}}}

# Unknown id (on GET or on send)
curl -s localhost:8000/tickets/00000000-0000-0000-0000-000000000000
# 404 {"error": {"code": "not_found", "message": "Ticket not found.", "details": null}}

# Listing is not exposed
curl -s localhost:8000/tickets
# 405 {"error": {"code": "method_not_allowed", ...}}

# Body that is not JSON (curl -d without a JSON Content-Type sends form data)
curl -s -X POST localhost:8000/tickets -d 'subject=x'
# 415 {"error": {"code": "unsupported_media_type", ...}}
```

Provider failures: restart the server in another mode, create a ticket, then send it:

```bash
TICKET_PROVIDER_MODE=timeout python manage.py runserver 8000
curl -s -X POST localhost:8000/tickets/$ID/send
# 504 {"error": {"code": "provider_timeout", ...}}      ticket stays pending

TICKET_PROVIDER_MODE=error python manage.py runserver 8000
curl -s -X POST localhost:8000/tickets/$ID/send
# 502 {"error": {"code": "provider_unavailable", ...}}  ticket stays pending
```

A failed ticket stays `pending` with `external_id: null`, so it can be sent again after a restart in `success` mode.

Every case above is covered by `ticket-api/tests/test_views.py` and `ticket-api/tests/test_permissions.py`.

### Project layout

```
config/            Django settings and root URLs
tickets/
  admin.py         Ticket admin (managed fields read-only)
  models.py        Ticket model (UUID id, status pending|sent, UTC created_at, external_id)
  serializers.py   TicketCreateSerializer (input contract) / TicketSerializer (output)
  views.py         TicketViewSet: create, retrieve, @action send
  urls.py          SimpleRouter(trailing_slash=False)
  services.py      send_ticket(): send rules, persistence and logging (no HTTP code)
  providers.py     TicketProvider protocol, SimulatedProvider, get_provider()
  exceptions.py    502/504 API errors + JSON error handler
tests/             serializers, views, permissions, URLs, services, providers, admin
```

### Decisions

- **DRF ViewSet + router.** `GenericViewSet` with only `CreateModelMixin` and `RetrieveModelMixin`,
  plus `@action(detail=True) send`. List, update and delete are not exposed, so they return 405.
  `trailing_slash=False` keeps the paths exactly as in the spec.
- **400 for invalid input.** This is DRF's native validation status, used for field errors, unknown fields and malformed JSON.
- **Unknown fields are rejected, not ignored.** Sending `status`, `external_id`, `id`, `created_at` or any
  other extra key returns 400, which makes "these fields cannot be set" explicit to the client.
- **Trimming before validation.** DRF `CharField` trims outer whitespace before the length validators run,
  so `"   "` is blank and the limits (120 / 2000) apply to the trimmed text. The trimmed value is what gets stored.
- **UUID ids.** Generated by the backend and not enumerable.
- **Thin view, separate service.** `services.send_ticket()` holds the rules and raises provider exceptions.
  The view only maps them to 504 / 502. Any other `ProviderError` also maps to 502, so an unexpected provider
  failure can never mark a ticket as sent.
- **Swappable provider.** The view gets its provider from `TicketViewSet.get_provider()`, which calls
  `providers.get_provider()` and builds a `SimulatedProvider` for `settings.TICKET_PROVIDER_MODE`. Tests replace
  that hook with a `FakeProvider` that counts calls. The simulator raises immediately and never sleeps.
- **Persist only on success.** The ticket row is written only after the provider returns an id, so a failure leaves
  `pending` / `external_id = null` and the same ticket can be sent again.
- **Logging without personal data.** The `tickets` logger writes only `ticket_id`, the outcome and the
  `external_id`, never the email or description (a test checks this).
- **Permissions.** No authentication (out of scope); `AllowAny` is declared explicitly on the view and in settings.
- **Admin next to an unauthenticated API.** The admin uses Django sessions and CSRF, while DRF keeps
  `DEFAULT_AUTHENTICATION_CLASSES = []`, so being logged into the admin never makes the API require CSRF tokens (tested).
- **Django ORM over raw SQL.** It is enough for one table, and `migrate` doubles as the documented init command.

### Limitations

- "Already sent → no second provider call" is guaranteed for **sequential** requests only (as the spec allows).
- SQLite is fine for local use, but it serialises writes and does not support `SELECT ... FOR UPDATE`.
- No authentication, rate limiting, pagination or listing.
- The provider mode is process-wide and fixed at start-up (restart to change it).
- The simulated provider does not receive an idempotency key, because there is no real API to honour it.

### What happens if...

**Two `send` requests for the same pending ticket arrive at the same time?**
Both read `status = pending`, both call the provider, and both write `sent`. The ticket ends up `sent`, but the
provider may have received it twice, and the stored `external_id` is whichever write landed last. To fix it:
1. Claim the ticket atomically before calling the provider, for example
   `Ticket.objects.filter(pk=id, status="pending").update(status="sending")`. Only the request that updates one row
   proceeds; the other gets 409 (or the current state). Failures move the ticket back to `pending`.
2. Send the ticket id as an idempotency key, so the provider deduplicates even if two calls get through.
3. On PostgreSQL, `select_for_update()` inside a transaction is an alternative to the conditional update.

**The provider accepts the ticket but saving locally fails?**
The client gets a 500 (`server_error`), and the ticket stays `pending` with no `external_id`, even though the
provider already has it. A retry would send it again and create a duplicate on the provider side. To fix it:
- Use an idempotency key (the ticket id), so the retry returns the same `external_id` instead of creating a new one.
- Record the intent before the call (status `sending` or an outbox row), so a reconciliation job can query the
  provider for tickets stuck in `sending` and complete them.
- Log the `external_id` returned by the provider (already done), so a failed save can be repaired by hand.
