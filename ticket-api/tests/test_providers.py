import pytest
from django.core.exceptions import ImproperlyConfigured

from tickets.models import Ticket
from tickets.providers import (
    ProviderMode,
    ProviderTimeout,
    ProviderUnavailable,
    SimulatedProvider,
    get_provider,
)


@pytest.fixture
def unsaved_ticket() -> Ticket:
    return Ticket(subject="s", description="d", email="a@example.com")


def test_simulated_provider_success_returns_external_id(unsaved_ticket):
    external_id = SimulatedProvider(ProviderMode.SUCCESS).send(unsaved_ticket)

    assert external_id.startswith("EXT-")
    assert len(external_id) == 16


def test_simulated_provider_success_returns_unique_ids(unsaved_ticket):
    provider = SimulatedProvider(ProviderMode.SUCCESS)

    assert provider.send(unsaved_ticket) != provider.send(unsaved_ticket)


@pytest.mark.parametrize(
    ("mode", "expected"),
    [(ProviderMode.TIMEOUT, ProviderTimeout), (ProviderMode.ERROR, ProviderUnavailable)],
)
def test_simulated_provider_failure_modes_raise(unsaved_ticket, mode, expected):
    with pytest.raises(expected):
        SimulatedProvider(mode).send(unsaved_ticket)


@pytest.mark.parametrize("raw", ["success", "timeout", "error", " TIMEOUT "])
def test_get_provider_uses_configured_mode(settings, raw):
    settings.TICKET_PROVIDER_MODE = raw

    provider = get_provider()

    assert isinstance(provider, SimulatedProvider)
    assert provider.mode == raw.strip().lower()


def test_get_provider_with_invalid_mode_raises_clear_error(settings):
    settings.TICKET_PROVIDER_MODE = "flaky"

    with pytest.raises(ImproperlyConfigured, match="success, timeout, error"):
        get_provider()
