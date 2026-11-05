from __future__ import annotations

from typing import Any, Optional


class CheckoutAPIError(Exception):
    """Raised whenever the CHECKOUT.UZ API returns an HTTP error status or a
    JSON body indicating failure (e.g. ``{"status": "error", ...}``).

    Attributes:
        status_code: The HTTP status code returned by the API (0 if the
            request never reached the server, e.g. a network error).
        message: A human-readable error message, taken from the API's
            ``error`` or ``message`` field when available.
        response: The full parsed JSON response body, if any was returned.
    """

    def __init__(self, message: str, status_code: int = 0, response: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"CheckoutAPIError(status_code={self.status_code!r}, message={self.message!r})"
