import datetime as dt

import pytest

import update_agent_memory as mem
from conftest import run_git

NOW = dt.datetime(2026, 10, 28, 12, 0, tzinfo=dt.timezone.utc)


def test_replace_block_swaps_existing_block_and_keeps_curated_text():
    text = f"# Title\ncurated\n{mem.START}\nold\n{mem.END}\nfooter\n"
    result = mem.replace_block(text, f"{mem.START}\nnew\n{mem.END}")
    assert result == f"# Title\ncurated\n{mem.START}\nnew\n{mem.END}\nfooter\n"


def test_replace_block_appends_when_markers_missing():
    result = mem.replace_block("# Title\n", f"{mem.START}\nnew\n{mem.END}")
    assert result == f"# Title\n\n{mem.START}\nnew\n{mem.END}\n"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("---\nname: x\ndescription: does: things\n---\nbody", {"name": "x", "description": "does: things"}),
        ("no frontmatter", {}),
        ("", {}),
    ],
    ids=["valid", "missing", "empty"],
)
def test_parse_frontmatter(text, expected):
    assert mem.parse_frontmatter(text) == expected


def test_staged_changes_reports_status_and_excludes_memory_file(repo, commit):
    commit("chore: init", {"a.py": "1", "b.py": "2"})
    (repo / "a.py").write_text("changed")
    (repo / "c.py").write_text("new")
    (repo / ".agents").mkdir()
    (repo / ".agents" / "AGENTS.md").write_text("memory")
    run_git(repo, "rm", "-q", "b.py")
    run_git(repo, "add", "a.py", "c.py", ".agents/AGENTS.md")

    assert sorted(mem.staged_changes(repo)) == [
        ("added", "c.py"),
        ("deleted", "b.py"),
        ("modified", "a.py"),
    ]


def test_recent_commits_on_empty_repo_is_empty(repo):
    assert mem.recent_commits(repo) == []


def test_recent_commits_keeps_pipes_in_subject(repo, commit):
    commit("feat: a | b", {"x": "1"})
    [(sha, date, subject)] = mem.recent_commits(repo)
    assert subject == "feat: a | b"
    assert len(sha) >= 7


def test_project_layout_collapses_deep_paths(repo, commit):
    commit("chore: init", {"README.md": "", "src/pkg/deep/mod.py": "", "src/top.py": ""})
    assert mem.project_layout(repo, depth=2) == ["README.md", "src/pkg/", "src/top.py"]


def test_skills_index_reads_skill_frontmatter(repo):
    skill = repo / ".agents/skills/demo/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: demo\ndescription: Demo skill\n---\n")
    assert mem.skills_index(repo) == [("demo", "Demo skill", ".agents/skills/demo/SKILL.md")]


def test_render_block_contains_all_sections(repo, commit):
    commit("feat: first", {"app.py": "print()"})
    (repo / "app.py").write_text("print('hi')")
    run_git(repo, "add", "app.py")

    block = mem.render_block(repo, NOW, use_ai=False)

    assert block.startswith(mem.START) and block.endswith(mem.END)
    assert "_Last updated: 2026-10-28 12:00 UTC · branch `main`_" in block
    assert "- modified `app.py`" in block
    assert ": feat: first" in block
    assert "### Change summary" not in block


def test_render_block_includes_ai_summary_when_available(repo, monkeypatch):
    (repo / "x.py").write_text("x = 1")
    run_git(repo, "add", "x.py")
    monkeypatch.setattr(mem, "run_ai", lambda prompt: "- adds x")

    block = mem.render_block(repo, NOW)

    assert "### Change summary (AI-generated)\n- adds x" in block


def test_main_rewrites_block_and_stages_memory_file(repo):
    (repo / ".agents").mkdir()
    (repo / ".agents" / "AGENTS.md").write_text(f"# Memory\nkeep me\n{mem.START}\nstale\n{mem.END}\n")
    (repo / "new.py").write_text("")
    run_git(repo, "add", "new.py")

    assert mem.main(["--root", str(repo), "--no-ai"]) == 0

    content = (repo / ".agents" / "AGENTS.md").read_text()
    assert "keep me" in content
    assert "stale" not in content
    assert "- added `new.py`" in content
    assert ".agents/AGENTS.md" in run_git(repo, "diff", "--cached", "--name-only")


def test_main_creates_memory_file_if_missing(repo):
    mem.main(["--root", str(repo), "--no-ai", "--no-stage"])
    assert (repo / ".agents" / "AGENTS.md").read_text().startswith("# AGENTS.md")
