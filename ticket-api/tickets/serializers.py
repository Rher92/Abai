from collections.abc import Mapping

from rest_framework import serializers

from .models import Ticket


class TicketCreateSerializer(serializers.ModelSerializer):
    """Input contract for POST /tickets.

    Only `subject`, `description` and `email` are accepted. DRF's CharField
    trims outer whitespace before the length validators run, so "   " is
    rejected as blank and the 120/2000 limits apply to the trimmed text.
    Any other key, including backend-managed fields such as `status`, is
    rejected instead of being silently ignored.
    """

    class Meta:
        model = Ticket
        fields = ["subject", "description", "email"]
        extra_kwargs = {
            "subject": {"min_length": 1},
            "description": {"min_length": 1},
        }

    def to_internal_value(self, data):
        unknown_errors = {}
        if isinstance(data, Mapping):
            unknown_errors = {
                name: ["This field is not allowed."]
                for name in sorted(set(data) - set(self.fields))
            }
        try:
            value = super().to_internal_value(data)
        except serializers.ValidationError as exc:
            # Report unknown fields together with the regular field errors.
            if unknown_errors and isinstance(exc.detail, dict):
                raise serializers.ValidationError({**exc.detail, **unknown_errors}) from None
            raise
        if unknown_errors:
            raise serializers.ValidationError(unknown_errors)
        return value


class TicketSerializer(serializers.ModelSerializer):
    """Output representation of a persisted ticket (read-only)."""

    class Meta:
        model = Ticket
        fields = [
            "id",
            "subject",
            "description",
            "email",
            "status",
            "created_at",
            "external_id",
        ]
        read_only_fields = fields
