from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .exceptions import CheckoutAPIError

DEFAULT_TIMEOUT = 20


class _BaseHTTPClient:
    """Shared request/response handling for all CHECKOUT.UZ API clients.

    Every CHECKOUT.UZ endpoint accepts a JSON body over POST and replies
    with a JSON body. Any HTTP status outside the 2xx range is treated as
    an error (the API always sends an explicit non-2xx status alongside
    an ``error``/``message`` field on failure - this holds across every
    endpoint in both v1 and v2).
    """

    def __init__(self, base_url: str, token: str, timeout: int = DEFAULT_TIMEOUT, session: Optional[requests.Session] = None):
        if not token:
            raise ValueError("An API token is required")
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._session = session or requests.Session()

    def _post(self, method_name: str, params: Optional[Dict[str, Any]] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}/{method_name}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)

        # Drop keys explicitly set to None so optional params are simply
        # omitted rather than sent as JSON null.
        body = {k: v for k, v in (params or {}).items() if v is not None}

        try:
            resp = self._session.post(url, json=body, headers=headers, timeout=self._timeout)
        except requests.RequestException as exc:
            raise CheckoutAPIError(f"Network error while calling {method_name}: {exc}") from exc

        try:
            data = resp.json()
        except ValueError:
            data = None

        if not resp.ok:
            message = "Unknown error"
            if isinstance(data, dict):
                message = data.get("error") or data.get("message") or message
            raise CheckoutAPIError(message, status_code=resp.status_code, response=data)

        return data if isinstance(data, dict) else {}
