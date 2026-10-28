"""API error types and the JSON error contract.

Every error response has the same shape:

    {"error": {"code": "<machine_code>", "message": "<human text>", "details": ...}}
"""
import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("tickets")


class ProviderTimeoutError(exceptions.APIException):
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    default_detail = "The ticket provider timed out. The ticket is still pending; retry later."
    default_code = "provider_timeout"


class ProviderUnavailableError(exceptions.APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "The ticket provider is unavailable. The ticket is still pending; retry later."
    default_code = "provider_unavailable"


def _error_body(code: str, message: str, details=None) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


def api_exception_handler(exc, context):
    """DRF exception handler that wraps every error in the common JSON shape."""
    response = exception_handler(exc, context)

    if response is None:
        # Unexpected failure: keep the contract and avoid leaking internals.
        logger.error("unhandled_error type=%s", type(exc).__name__)
        return Response(
            _error_body("server_error", "Internal server error."),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # DRF converts these Django exceptions internally; mirror that here to read their codes.
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.ValidationError):
        response.data = _error_body("invalid_input", "Invalid input.", response.data)
    else:
        detail = exc.detail if isinstance(exc, exceptions.APIException) else str(exc)
        code = getattr(detail, "code", None) or getattr(exc, "default_code", "error")
        response.data = _error_body(code, str(detail))
    return response
