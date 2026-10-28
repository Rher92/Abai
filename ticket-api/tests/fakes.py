from tickets.models import Ticket


class FakeProvider:
    """Test double that records calls and returns or raises what it is told."""

    def __init__(self, result: str = "EXT-FAKE-1", error: Exception | None = None):
        self.result = result
        self.error = error
        self.calls: list = []

    def send(self, ticket: Ticket) -> str:
        self.calls.append(ticket.id)
        if self.error is not None:
            raise self.error
        return self.result
