# Feature 05: Django admin for tickets

Enable the Django admin at `/admin/` and register the `Ticket` model.

depends: Feature 02

## Assumptions
- The admin needs `django.contrib.admin`, `sessions`, `messages` and `staticfiles`, the standard middleware
  (sessions, CSRF, auth, messages), a `TEMPLATES` entry and `STATIC_URL`. None of these existed (the project was API-only).
- The DRF API stays unauthenticated and CSRF-free: `DEFAULT_AUTHENTICATION_CLASSES` stays empty, so an admin
  session cookie does not change API behaviour.
- Managed fields (`id`, `status`, `external_id`, `created_at`) are **read-only** in the admin, so staff cannot put a
  ticket into an inconsistent state (e.g. `sent` without `external_id`). `subject`, `description` and `email` are editable.
- Access is through `python manage.py createsuperuser` (documented in the README).

## Tasks
<!-- [ ] todo · [~] in progress (only one) · [x] done · [!] blocked: reason -->
- [x] T1 Enable the admin in `config/settings.py` (apps, middleware, templates, static) and `config/urls.py` (`admin/`)
      accept: `python manage.py check` clean; `migrate` adds the admin/sessions tables
- [x] T2 `tickets/admin.py::TicketAdmin` (list_display, list_filter on status, search, read-only managed fields)   depends: T1
      accept: `tests/test_admin.py`: model registered; changelist/add/change pages return 200 for a superuser; anonymous user redirected to login; managed fields read-only
- [x] T3 Regression + docs: full suite green (API still works when a session cookie is present); README section "Admin"   depends: T2
      accept: `pytest -q` green; manual login at `/admin/` works

## Notes
- `migrate` now also creates the admin, sessions and messages tables. Existing DBs just need `python manage.py migrate` again.
- Live check: superuser login via the real form → 302 to `/admin/`; changelist 200 shows a ticket created via the API; `/static/admin/css/base.css` 200 (served by runserver with DEBUG=1).
- 86 tests green (+9 in `tests/test_admin.py`).
