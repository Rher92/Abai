# Feature 04: README and delivery

Make the project reproducible and explain its decisions, as the test requires.

depends: Features 01–03

## Tasks
<!-- [ ] todo · [~] in progress (only one) · [x] done · [!] blocked: reason -->
- [x] T1 Manual smoke run: `migrate`, `runserver`, curl the 3 endpoints in each provider mode, restart the server, and confirm the ticket still exists
      accept: observed outputs match the README examples
- [x] T2 `ticket-api/README.md` (now the "Ticket API" section of the root `README.md`): install / init DB / run / test commands; curl examples for the 3 requests; how to set each provider mode;
      the 400 choice; decisions; limitations; next iteration; concurrent double-send and "provider accepted but local save failed" reasoning;
      time spent; AI/tools declaration   depends: T1
      accept: following the README in a fresh venv works
- [x] T3 Wrap-up: full test run (ticket-api + toolkit), learnings into `AGENT.md`, mark all task files done   depends: T1, T2
      accept: all checks green

## Notes
- Smoke run over 3 server restarts (error → timeout → success): ticket persisted, 502/504 kept pending, success stored the external_id, the second send returned 200 with an `already_sent` log, unknown id → 404, no email in the logs.
- The smoke run showed unknown-field errors hid other field errors; the serializer now merges them (+1 test).
- Clean copy + fresh Python 3.11 venv following the README: install, migrate and 77 tests OK. The README now states the Python 3.11+ requirement (the pyenv shim fell back to 3.9 outside the repo).
- **Open:** `README.md` "Effective time" is a TODO for Roger to fill in.
