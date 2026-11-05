from __future__ import annotations

from typing import Any, Dict, Optional

from ._http import _BaseHTTPClient

V2_BASE_URL = "https://checkout.uz/api/v2"


class V2Client(_BaseHTTPClient):
    """Client for the CHECKOUT.UZ merchant API v2 (``/api/v2``).

    Authenticated with the same shop API key as v1
    (``Authorization: Bearer <api_key>``). v2 adds idempotent payment
    creation, pagination, cancellation/refunds and fiscal receipts on top
    of everything v1 offers.

    Note: :meth:`get_profile`, :meth:`get_shops` and :meth:`get_profile_stats`
    are account-level (not shop-level) and use a *different* credential -
    see :class:`checkout_uz.ProfileClient`.
    """

    def __init__(self, api_key: str, **kwargs: Any):
        super().__init__(V2_BASE_URL, api_key, **kwargs)

    def create_payment(
        self,
        amount: float,
        description: Optional[str] = None,
        expire_time: Optional[int] = None,
        webhook_url: Optional[str] = None,
        return_url: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new payment invoice.

        ``amount`` is in UZS (1000-10,000,000). ``expire_time`` is in
        seconds (60-432000, default 3600). If ``idempotency_key`` is given
        and the same key was used for this shop within the last 24 hours,
        the original invoice is returned instead of creating a new one
        (``idempotent_replay`` in the response tells you which happened).
        """
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        return self._post("create_payment", {
            "amount": amount,
            "description": description,
            "expire_time": expire_time,
            "webhook_url": webhook_url,
            "return_url": return_url,
        }, extra_headers=headers)

    def status_payment(self, id: Optional[int] = None, uuid: Optional[str] = None) -> Dict[str, Any]:
        """Look up an invoice by its numeric ``id`` or its ``uuid`` (pay_token). Provide exactly one."""
        if id is None and uuid is None:
            raise ValueError("Provide either id or uuid")
        return self._post("status_payment", {"id": id, "uuid": uuid})

    def get_balance(self) -> Dict[str, Any]:
        """Return the shop's current balance per currency (uppercase currency codes)."""
        return self._post("get_balance")

    def get_history(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return the shop's invoices, newest first.

        ``limit`` is 1-200. ``status`` filters by one of
        ``pending``/``paid``/``canceled``/``reversed``. ``date_from``/``date_to``
        accept any format ``strtotime()`` understands (e.g. ``"2026-01-01"``).
        The response's ``has_more`` tells you whether another page exists.
        """
        return self._post("get_history", {
            "limit": limit,
            "offset": offset,
            "status": status,
            "date_from": date_from,
            "date_to": date_to,
        })

    def get_stats(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Return aggregate order count / income for the shop, broken down by payment provider."""
        return self._post("get_stats", {"date_from": date_from, "date_to": date_to})

    def get_payment_methods(self) -> Dict[str, Any]:
        """List the payment methods enabled for this shop, including min/max amount and fiscal support."""
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

    def cancel_payment(self, order_id: int) -> Dict[str, Any]:
        """Cancel a **pending** invoice. Fails if the invoice is not in ``pending`` status."""
        return self._post("cancel_payment", {"order_id": order_id})

    def refund_payment(self, order_id: int) -> Dict[str, Any]:
        """Reverse a successful card/Payme/Click payment and deduct it back from the shop balance.

        Only available within a limited window after the original payment
        (currently 22 hours); the API returns an error past that point.
        """
        return self._post("refund_payment", {"order_id": order_id})

    def get_fiscal(self, order_id: int) -> Dict[str, Any]:
        """Fetch the fiscal (tax) receipt for a paid order. Supported for Payme, Click and Plum payments only."""
        return self._post("get_fiscal", {"order_id": order_id})
