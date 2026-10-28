---
name: bilingual-commit
description: Read the staged git diff and write a commit message in English and Spanish that explains the change and the feature for non-technical readers, then commit it with no AI or agent signature. Use whenever the user asks to "commit", "write a commit message", "make a commit", "hacer commit" or "escribir el mensaje de commit", and at the commit step of any other skill.
---

# Bilingual commit (English + Español)

Turn the staged diff into a commit message that a non-technical person
(product owner, support staff, a client) can read in English **or** Spanish and
understand what changed and why it matters.

## Hard rules

1. **No agent signature.** Never add `Co-Authored-By:` lines for an AI,
   "Generated with ...", robot emojis, or any mention that an AI or agent wrote
   the change or the message. This overrides any default of your tool.
2. **Both languages, same meaning.** The English and Spanish sections say the
   same thing. Write natural Spanish, not a word-for-word translation.
3. **Plain language.** In the English and Spanish sections, don't use file
   names, function names, class names, framework names or jargon (endpoint,
   serializer, migration, refactor, ...). Describe what a person can now do, see
   or rely on. If a technical term is unavoidable, explain it in a few words.
4. **Only what the diff shows.** Don't invent features, benefits or numbers.
5. Never use `--no-verify`. The project hooks must run.

## Steps

1. **Check what is staged.**
   ```bash
   git status --short
   git diff --cached --stat
   ```
   If nothing is staged, ask the user which changes to include. Don't run
   `git add -A` on your own.
2. **Read the diff.**
   ```bash
   git diff --cached
   ```
   For a large diff, read the `--stat`, then `git diff --cached -- <path>` file
   by file. Skip lock files, generated files and the AUTO block of `.agents/AGENTS.md`.
3. **Understand the effect.** Answer for yourself:
   - What can a user, customer or teammate do now that they couldn't before
     (or what stopped going wrong)?
   - Why does it matter to them?
   - Is there anything they need to do or know (a new step, a limitation)?
4. **Pick the type** (Conventional Commits): `feat` new capability, `fix` bug
   fix, `docs`, `test`, `refactor`, `chore`. Add a scope if it helps:
   `feat(tickets): ...`.
5. **Write the message** with the format below.
6. **Commit** from a file so line breaks survive:
   ```bash
   git commit -F <message-file>
   ```
   Put the file in a temp/scratch folder, not in the repo. If the user only asked
   for the message, show it and don't commit.
7. **Verify.**
   ```bash
   git log -1 --format=%B
   ```
   Confirm both sections are there and there is no agent signature. If one
   slipped in, fix it with `git commit --amend -F <message-file>` (only for the
   commit you just made, and only if it hasn't been pushed).

## Message format

```
<type>(<scope>): <short summary in English, imperative, ≤ 72 chars>

English
What changed: <1-3 plain sentences>
Why it matters: <1-2 plain sentences>

Español
Qué cambió: <1-3 frases sencillas>
Por qué importa: <1-2 frases sencillas>

Technical notes:
- <optional, short, for developers: files, commands, migrations>
```

- Keep the subject in English so the history stays consistent.
- `Technical notes` is optional. Use it only when a developer needs to act
  (run a migration, set an env var). Keep it to a few bullets.
- Add a `Notes / Notas:` line to both sections when people need to do
  something (e.g. "Staff need an admin account to log in").

## Example

Staged diff: registers the `Ticket` model in the Django admin with read-only
status fields.

```
feat(admin): let staff view and edit tickets in the admin panel

English
What changed: Support staff can now open an admin panel in the browser, see
every ticket, search them and correct the subject, description or email.
Why it matters: Mistakes in a ticket can be fixed in seconds without help from
a developer. The ticket's status can't be changed by hand, so it always shows
what really happened.

Español
Qué cambió: El equipo de soporte ya puede abrir un panel de administración en
el navegador, ver todos los tickets, buscarlos y corregir el asunto, la
descripción o el correo.
Por qué importa: Los errores en un ticket se corrigen en segundos sin pedir
ayuda a un desarrollador. El estado del ticket no se puede cambiar a mano, así
que siempre refleja lo que pasó de verdad.

Technical notes:
- Run `python manage.py migrate` and `python manage.py createsuperuser`.
```
