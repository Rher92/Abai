"""Provider-agnostic bridge to whatever AI CLI the developer uses.

Set ``AI_CLI`` to a command that reads a prompt on stdin and prints the answer
on stdout, for example::

    export AI_CLI="claude -p"          # Claude Code
    export AI_CLI="codex exec -"       # OpenAI Codex CLI
    export AI_CLI="gemini"             # Gemini CLI
    export AI_CLI="ollama run llama3"  # local model

When ``AI_CLI`` is unset or the command fails, callers fall back to
deterministic, non-AI output, so hooks never block on an AI being available.
"""
from __future__ import annotations

import os
import shlex
import subprocess

DEFAULT_TIMEOUT = int(os.environ.get("AI_CLI_TIMEOUT", "120"))


def run_ai(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> str | None:
    """Return the AI's answer to ``prompt``, or None if no AI is configured or it fails."""
    command = os.environ.get("AI_CLI", "").strip()
    if not command:
        return None
    try:
        result = subprocess.run(
            shlex.split(command),
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = result.stdout.strip()
    return output if result.returncode == 0 and output else None
