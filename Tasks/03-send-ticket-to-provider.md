# Feature 03: Send a ticket to the simulated provider

`POST /tickets/{id}/send` with a swappable, in-process provider (modes `success|timeout|error`).

depends: Feature 02

## Assumptions
- `tickets/providers.py`: `TicketProvider` protocol, `SimulatedProvider(mode)`, exceptions `ProviderTimeout` / `ProviderUnavailable`,
  and `get_provider()` that reads `settings.TICKET_PROVIDER_MODE` (from env `TICKET_PROVIDER_MODE`, default `success`) on each call. A running server needs a restart to change mode, which also demonstrates persistence; tests override it with the `settings` fixture.
- `tickets/services.py::send_ticket(ticket, provider)` holds the rules; the view stays thin and gets the provider from an overridable
  `TicketViewSet.get_provider()`, so tests can inject a fake that counts calls.
- Provider exceptions map to DRF exceptions: timeout → 504 `provider_timeout`, unavailable → 502 `provider_unavailable`.
- Logs (`tickets` logger) record `ticket_id` + outcome only, never email or description.
- Sequential-only guarantee for "already sent" (no locking); concurrency is discussed in the README.

## Tasks
<!-- [ ] todo · [~] in progress (only one) · [x] done · [!] blocked: reason -->
- [x] T1 `tickets/providers.py` (simulator + `get_provider()`; an invalid mode raises a clear config error)
      accept: `tests/test_providers.py`: each mode's result/exception; env selection; invalid mode
- [x] T2 `tickets/services.py::send_ticket()` + `ProviderTimeoutError` (504) / `ProviderUnavailableError` (502) in `tickets/exceptions.py`   depends: T1
      accept: `tests/test_services.py`: success persists `sent` + `external_id`; failures leave the DB row unchanged; already sent → provider not called; logs have no PII (`caplog`)
- [x] T3 `send` action on `TicketViewSet` (`@action(detail=True, methods=["post"])`)   depends: T2
      accept: `tests/test_urls.py` + `tests/test_permissions.py` cover the `send` route (GET → 405)
- [x] T4 View tests for send: 200 success (DB checked), 504 timeout, 502 error (DB still pending/null), retry after failure → 200, second send → 200 with zero provider calls, unknown id → 404, mode via env var end to end   depends: T3
      accept: `pytest -q` green

## Notes
- Service raises domain exceptions (`ProviderTimeout`/`ProviderError`); only the view maps them to 504/502, so `services.py` has no DRF imports.
- Any other `ProviderError` subclass also maps to 502, so unknown provider failures never mark the ticket as sent.
- `FakeProvider` lives in `tests/fakes.py` (not conftest) so test modules can import it.
- 76 tests green.
