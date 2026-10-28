# Feature 06: Bilingual commit skill

A skill that reads the staged diff and writes the commit message in English and Spanish, explaining the
change and the feature for non-technical readers, with no AI/agent signature.

## Assumptions
- A skill, not a hook (user decision): the agent writes the message; nothing blocks manual commits.
- Subject stays a Conventional Commit in English; the body has `English` and `Español` sections with the same meaning.
- The skill never runs `git add -A` or `--no-verify`, and asks what to stage when nothing is staged.

## Tasks
<!-- [ ] todo · [~] in progress (only one) · [x] done · [!] blocked: reason -->
- [x] T1 `.agents/skills/bilingual-commit/SKILL.md` (rules, steps, message format, example)
      accept: frontmatter has `name` + `description`; visible through the `.claude/skills` symlink
- [x] T2 Wire it in: `AGENT.md` (skills list, working rule 2, learnings), `README.md`, task-breakdown step 6   depends: T1
      accept: no remaining "Use Conventional Commits" rule without the skill; pre-commit hook lists the skill
- [x] T3 Wrap-up: root tests green   depends: T2
      accept: `python -m pytest -q`

## Notes
- No Python changed, so no new tests.
