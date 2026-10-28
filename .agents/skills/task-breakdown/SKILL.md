---
name: task-breakdown
description: Break a feature request, bug, or goal into small, verifiable tasks, write them to TASKS.md as a checklist, then execute them one at a time while keeping the list current. Use when a request touches more than one file or needs more than a few steps, or when the user asks to "plan", "break down", "make a task list", or "split this into steps".
---

# Task Breakdown

Turn a request into an ordered, checkable task list, then work through it.
This skill is tool-agnostic: it only assumes you can read files, edit files,
and run shell commands. If your environment has a native todo/task tool, mirror
the list there too, but `TASKS.md` is the source of truth.

## When to use

- The request needs more than ~3 steps or touches several files/modules.
- The scope is fuzzy and needs to be made concrete before coding.
- Work may span multiple sessions or multiple agents (the file survives).

Skip it for one-line fixes or pure questions.

## Phase 0: Ask for the input (mandatory)

Right after this skill is invoked, **stop and ask the user** what to break down
before reading code or planning anything. Ask for one of:

- a document (spec, PRD, ticket, issue link, file path), or
- a written description of the feature, bug, or goal.

Do this even if the invoking message seems to contain a request: confirm it
with the user, and ask whether there is a document that goes with it. Don't
start Phase 1 until the user has replied. If your tool has a structured
question/prompt feature, use it; otherwise ask in plain text and wait.

## Phase 1: Understand

1. Restate the goal in one sentence. If you cannot, ask the user.
2. Read `.agents/AGENTS.md` for project conventions, commands and past decisions.
3. Inspect the code that will change (entry points, callers, tests).
4. Write down **assumptions** and **open questions**. Ask only the questions
   whose answers would change the plan; otherwise pick a sensible default and
   record it as an assumption.

## Phase 2: Decompose

Split the work into tasks that each satisfy **all** of these rules:

| Rule | Meaning |
|------|---------|
| Small | Doable in one focused sitting (roughly ≤ 1 commit, ≤ ~200 changed lines). |
| Verifiable | Has an acceptance check: a test, a command, or an observable behaviour. |
| Independent where possible | Prefer vertical slices (working end-to-end) over layers. |
| Ordered | Dependencies come first; list them explicitly with `depends:`. |
| Concrete | Names the files/functions involved, not "improve X". |

Rules of thumb:
- Put risky or uncertain work (spikes, unknown APIs) **first**, so surprises appear early.
- Every behaviour change gets a test task, either inside the task or right after it (see the `pytest-unittest` skill).
- End with a wrap-up task: run the full test suite, update docs, update `.agents/AGENTS.md` learnings.
- More than ~12 tasks means the goal is too big. Group the tasks into milestones.

## Phase 3: Write `TASKS.md`

Create or overwrite `TASKS.md` in the repo root, using
`templates/TASKS.md` from this skill as the format. Status markers:

- `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked (add reason)

Show the list to the user before starting if the work is large or the
assumptions are significant.

## Phase 4: Execute

Loop until every task is `[x]`:

1. Pick the first `[ ]` task whose dependencies are done. Mark it `[~]`.
   Only **one** task is `[~]` at a time.
2. Implement it. Keep changes scoped to that task.
3. Run its acceptance check. If the check fails, fix the problem before moving on.
4. Mark it `[x]` and add a one-line note under it if you learned something
   (a surprise, a decision, a follow-up).
5. If you discover new work, **add it as a new task**. Don't silently
   expand the current one. If the plan turns out wrong, re-plan in `TASKS.md`
   and tell the user.
6. Commit with the `bilingual-commit` skill (Conventional Commit subject,
   English + Spanish body, no agent signature).

## Phase 5: Close out

- Run the full test suite and linters.
- Move durable lessons into the curated sections of `.agents/AGENTS.md`
  (the auto-generated block is rewritten by a hook; don't edit it).
- Report to the user what was done, what was deferred, and any open risks.
- Delete `TASKS.md` or leave it with every task checked. Ask the user which they prefer.

## Example

Request: "Add CSV export to the reports page."

```markdown
## Tasks
- [ ] T1 Spike: confirm report data shape in `reports/service.py::build_report`
      accept: notes added below with field list
- [ ] T2 Add `to_csv(report) -> str` in `reports/export.py`   depends: T1
      accept: `pytest tests/test_export.py` passes (header, escaping, empty report)
- [ ] T3 Add `GET /reports/{id}.csv` endpoint                  depends: T2
      accept: endpoint test returns 200 + `text/csv`; 404 for unknown id
- [ ] T4 Add "Export CSV" button on reports page               depends: T3
      accept: manual check, button downloads file
- [ ] T5 Wrap-up: full test run, update .agents/AGENTS.md                depends: T2-T4
```
