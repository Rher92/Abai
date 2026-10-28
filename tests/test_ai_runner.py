import sys

import ai_runner


def test_run_ai_without_ai_cli_returns_none():
    assert ai_runner.run_ai("hello") is None


def test_run_ai_pipes_prompt_on_stdin_and_returns_stdout(monkeypatch):
    monkeypatch.setenv("AI_CLI", f"{sys.executable} -c \"import sys; print(sys.stdin.read().upper())\"")
    assert ai_runner.run_ai("hello") == "HELLO"


def test_run_ai_nonzero_exit_returns_none(monkeypatch):
    monkeypatch.setenv("AI_CLI", f"{sys.executable} -c \"print('partial'); raise SystemExit(1)\"")
    assert ai_runner.run_ai("hello") is None


def test_run_ai_missing_binary_returns_none(monkeypatch):
    monkeypatch.setenv("AI_CLI", "definitely-not-a-real-ai-cli")
    assert ai_runner.run_ai("hello") is None
