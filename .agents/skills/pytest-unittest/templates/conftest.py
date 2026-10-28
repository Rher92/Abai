"""Shared pytest fixtures. Copy into tests/conftest.py and trim to what you need."""
import pytest


@pytest.fixture
def make_user():
    """Factory fixture: build test objects with sensible defaults and overrides."""

    def _make_user(**overrides):
        data = {"id": 1, "name": "Ada", "email": "ada@example.com", "active": True}
        data.update(overrides)
        return data

    return _make_user


@pytest.fixture
def fixed_env(monkeypatch):
    """Pin environment variables so tests never read the developer's real config."""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.delenv("API_TOKEN", raising=False)


@pytest.fixture
def data_file(tmp_path):
    """A temp file pre-filled with sample content; removed automatically."""
    path = tmp_path / "input.csv"
    path.write_text("id,name\n1,Ada\n", encoding="utf-8")
    return path
