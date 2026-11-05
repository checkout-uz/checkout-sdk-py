from unittest.mock import MagicMock, patch

import pytest

from checkout_uz import CheckoutAPIError, ProfileClient, V2Client


def _mock_response(status_code=200, json_data=None):
    resp = MagicMock()
    resp.ok = 200 <= status_code < 300
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    return resp


@pytest.fixture
def client():
    return V2Client(api_key="test_key_123")


def test_create_payment_with_idempotency_key(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success"})) as mock_post:
        client.create_payment(amount=50000, expire_time=7200, idempotency_key="order-42")

    args, kwargs = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v2/create_payment"
    assert kwargs["json"] == {"amount": 50000, "expire_time": 7200}
    assert kwargs["headers"]["Idempotency-Key"] == "order-42"


def test_create_payment_without_idempotency_key_omits_header(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success"})) as mock_post:
        client.create_payment(amount=1000)

    _, kwargs = mock_post.call_args
    assert "Idempotency-Key" not in kwargs["headers"]


def test_get_history_filters(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success", "data": []})) as mock_post:
        client.get_history(limit=20, offset=10, status="paid", date_from="2026-01-01")

    args, kwargs = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v2/get_history"
    assert kwargs["json"] == {"limit": 20, "offset": 10, "status": "paid", "date_from": "2026-01-01"}


def test_cancel_payment(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success", "order_status": "canceled"})) as mock_post:
        result = client.cancel_payment(order_id=123)

    args, kwargs = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v2/cancel_payment"
    assert kwargs["json"] == {"order_id": 123}
    assert result["order_status"] == "canceled"


def test_refund_payment_error(client):
    with patch.object(client._session, "post", return_value=_mock_response(409, {"status": "error", "error": "More than 22 hours have passed"})):
        with pytest.raises(CheckoutAPIError) as exc_info:
            client.refund_payment(order_id=123)

    assert exc_info.value.status_code == 409


def test_get_fiscal(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success", "fiscal": {}})) as mock_post:
        client.get_fiscal(order_id=123)

    args, kwargs = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v2/get_fiscal"
    assert kwargs["json"] == {"order_id": 123}


def test_pay_via_card_inherited_endpoint_still_works(client):
    # pay_via_card/confirm_card_payment are inherited from v1 in the real API
    # (ApiV2 extends Api) but still routed under /api/v2/.
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success"})) as mock_post:
        client.pay_via_card(order_id=1, card_number="8600000000000000", card_expiry="1230")

    args, _ = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v2/pay_via_card"


def test_profile_client_uses_different_key_and_same_base_url():
    profile = ProfileClient(profile_api_key="profile_key_xyz")
    with patch.object(profile._session, "post", return_value=_mock_response(200, {"status": "success", "shops": []})) as mock_post:
        profile.get_shops()

    args, kwargs = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v2/get_shops"
    assert kwargs["headers"]["Authorization"] == "Bearer profile_key_xyz"


def test_profile_client_requires_key():
    with pytest.raises(ValueError):
        ProfileClient(profile_api_key="")
