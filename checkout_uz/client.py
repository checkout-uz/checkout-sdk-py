from __future__ import annotations

from typing import Any, Dict, Optional

from ._http import _BaseHTTPClient
from .v1 import V1Client
from .v2 import V2Client

V2_BASE_URL = "https://checkout.uz/api/v2"


class CheckoutClient:
    """Top-level entry point for the CHECKOUT.UZ merchant API.

    Holds a single shop API key and exposes both API versions:

    >>> client = CheckoutClient(api_key="ckio_...")
    >>> client.v1.create_payment(amount=50000)
    >>> client.v2.create_payment(amount=50000, expire_time=7200)

    For the account-level (not shop-level) v2 endpoints
    (``get_profile``/``get_shops``/``get_profile_stats``), use
    :class:`ProfileClient` instead - they use a different credential.
    """

    def __init__(self, api_key: str, timeout: int = 20):
        self.v1 = V1Client(api_key, timeout=timeout)
        self.v2 = V2Client(api_key, timeout=timeout)


class ProfileClient(_BaseHTTPClient):
    """Client for the account-level (profile) v2 endpoints.

    Authenticated with a **profile API key** (from account settings),
    sent as ``Authorization: Bearer <profile_api_key>``. This is a
    different credential from a shop's ``api_key`` used by
    :class:`CheckoutClient` - it is not tied to one shop and can read data
    across every shop the account owns.

    >>> profile = ProfileClient(profile_api_key="...")
    >>> profile.get_shops()
    """

    def __init__(self, profile_api_key: str, **kwargs: Any):
        super().__init__(V2_BASE_URL, profile_api_key, **kwargs)

    def get_profile(self) -> Dict[str, Any]:
        """Return the authenticated account's profile information."""
        return self._post("get_profile")

    def get_shops(self) -> Dict[str, Any]:
        """List every (non-deleted) shop owned by the authenticated account."""
        return self._post("get_shops")

    def get_profile_stats(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Return aggregate stats across all of the account's shops, broken down by shop and by provider."""
        return self._post("get_profile_stats", {"date_from": date_from, "date_to": date_to})
