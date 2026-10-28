import subprocess

import pytest


def run_git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture(autouse=True)
def no_ai(monkeypatch):
    """Never call a real AI from tests."""
    monkeypatch.delenv("AI_CLI", raising=False)


@pytest.fixture
def repo(tmp_path):
    """An empty git repository with a deterministic identity."""
    run_git(tmp_path, "init", "-q", "-b", "main")
    run_git(tmp_path, "config", "user.name", "Test")
    run_git(tmp_path, "config", "user.email", "test@example.com")
    run_git(tmp_path, "config", "commit.gpgsign", "false")
    return tmp_path


@pytest.fixture
def commit(repo):
    """Factory: write files, stage them and commit; returns the full SHA."""

    def _commit(message, files):
        for name, content in files.items():
            path = repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        run_git(repo, "add", *files)
        run_git(repo, "commit", "-q", "--no-verify", "-m", message)
        return run_git(repo, "rev-parse", "HEAD")

    return _commit
