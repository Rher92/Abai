"""Tiny git helpers used by the memory hook."""
from __future__ import annotations

import subprocess
from pathlib import Path


def git(root: Path, *args: str) -> str:
    """Run a git command in ``root``; return stripped stdout, or "" on failure."""
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def repo_root(start: Path | None = None) -> Path:
    top = git(start or Path.cwd(), "rev-parse", "--show-toplevel")
    return Path(top) if top else (start or Path.cwd())
