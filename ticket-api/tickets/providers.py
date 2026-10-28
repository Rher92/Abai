"""External ticket provider: interface, in-process simulator and factory.

The view never builds a provider directly; it asks `get_provider()` (through
`TicketViewSet.get_provider`), so tests can swap in any object with a
`send(ticket) -> str` method.
"""
import uuid
from enum import StrEnum
from typing import Protocol

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .models import Ticket


class ProviderError(Exception):
    """Base class for provider failures; the ticket must stay pending."""


class ProviderTimeout(ProviderError):
    """The provider did not answer in time."""


class ProviderUnavailable(ProviderError):
    """The provider rejected the call or could not be reached."""


class TicketProvider(Protocol):
    def send(self, ticket: Ticket) -> str:
        """Deliver the ticket and return the provider's identifier for it."""
        ...


class ProviderMode(StrEnum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"


class SimulatedProvider:
    """In-process stand-in for the external system. It never sleeps or does I/O."""

    def __init__(self, mode: ProviderMode = ProviderMode.SUCCESS) -> None:
        self.mode = ProviderMode(mode)

    def send(self, ticket: Ticket) -> str:
        if self.mode is ProviderMode.TIMEOUT:
            raise ProviderTimeout("Simulated provider timeout")
        if self.mode is ProviderMode.ERROR:
            raise ProviderUnavailable("Simulated provider unavailable")
        return f"EXT-{uuid.uuid4().hex[:12].upper()}"


def get_provider() -> TicketProvider:
    """Build the provider configured by `settings.TICKET_PROVIDER_MODE`."""
    raw_mode = str(settings.TICKET_PROVIDER_MODE).strip().lower()
    try:
        mode = ProviderMode(raw_mode)
    except ValueError:
        allowed = ", ".join(m.value for m in ProviderMode)
        raise ImproperlyConfigured(
            f"TICKET_PROVIDER_MODE={raw_mode!r} is invalid; use one of: {allowed}"
        ) from None
    return SimulatedProvider(mode)
