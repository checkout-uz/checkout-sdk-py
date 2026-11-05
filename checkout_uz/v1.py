from __future__ import annotations

from typing import Any, Dict, Optional

from ._http import _BaseHTTPClient

V1_BASE_URL = "https://checkout.uz/api/v1"


class V1Client(_BaseHTTPClient):
    """Client for the original CHECKOUT.UZ merchant API (``/api/v1``).

    Authenticated with a shop's API key (found in the shop's settings on
    checkout.uz), sent as ``Authorization: Bearer <api_key>``.
    """

    def __init__(self, api_key: str, **kwargs: Any):
        super().__init__(V1_BASE_URL, api_key, **kwargs)

    def create_payment(
        self,
        amount: float,
        description: Optional[str] = None,
        webhook_url: Optional[str] = None,
        return_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new payment invoice. ``amount`` is in UZS (1000-10,000,000)."""
        return self._post("create_payment", {
            "amount": amount,
            "description": description,
            "webhook_url": webhook_url,
            "return_url": return_url,
        })

    def status_payment(self, id: Optional[int] = None, uuid: Optional[str] = None) -> Dict[str, Any]:
        """Look up an invoice by its numeric ``id`` or its ``uuid`` (pay_token). Provide exactly one."""
        if id is None and uuid is None:
            raise ValueError("Provide either id or uuid")
        return self._post("status_payment", {"id": id, "uuid": uuid})

    def get_balance(self) -> Dict[str, Any]:
        """Return the shop's current balance per currency."""
        return self._post("get_balance")

    def get_history(self, limit: int = 10) -> Dict[str, Any]:
        """Return the shop's most recent invoices (newest first)."""
        return self._post("get_history", {"limit": limit})

    def get_stats(self) -> Dict[str, Any]:
        """Return aggregate order count / total income for the shop."""
        return self._post("get_stats")

    def get_payment_methods(self) -> Dict[str, Any]:
        """List the payment methods enabled for this shop."""
        return self._post("get_payment_methods")

    def pay_via_card(self, order_id: int, card_number: str, card_expiry: str) -> Dict[str, Any]:
        """Start a direct card payment (Uzcard/Humo) for a pending invoice. Sends an SMS code to the cardholder."""
        return self._post("pay_via_card", {
            "order_id": order_id,
            "card_number": card_number,
            "card_expiry": card_expiry,
        })

    def confirm_card_payment(self, payment_token: str, sms_code: str) -> Dict[str, Any]:
        """Confirm a card payment started with :meth:`pay_via_card` using the SMS code the cardholder received."""
        return self._post("confirm_card_payment", {
            "payment_token": payment_token,
            "sms_code": sms_code,
        })
