# Feature 01: Project scaffold

Self-contained Django + DRF project in `ticket-api/` that installs, checks and runs pytest.

## Assumptions
- Own virtualenv `ticket-api/.venv`; Django 5.2 LTS + DRF + pytest-django pinned in `requirements.txt`.
- DB file path from env `TICKETS_DB_PATH` (default `ticket-api/db.sqlite3`).
- `USE_TZ=True`, `TIME_ZONE="UTC"`; `SECRET_KEY` from env, with a dev-only fallback (no real credentials).

## Tasks
<!-- [ ] todo · [~] in progress (only one) · [x] done · [!] blocked: reason -->
- [x] T1 Create `requirements.txt`, `manage.py`, `config/{__init__,settings,urls,wsgi}.py`, empty `tickets` app, `pytest.ini`, `.env.example`, `.gitignore`
      accept: `python manage.py check` passes
- [x] T2 Create `ticket-api/.venv` and install the pinned requirements   depends: T1
      accept: `pytest` runs with no errors (no tests yet)

## Notes
- Split deps: `requirements.txt` (runtime) + `requirements-dev.txt` (pytest). DRF 3.16.1 pinned (supports Django 5.2).
- Only JSON renderer/parser enabled: no browsable API, and form posts get 415.
