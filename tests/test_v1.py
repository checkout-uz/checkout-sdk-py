from unittest.mock import MagicMock, patch

import pytest

from checkout_uz import CheckoutAPIError, V1Client


def _mock_response(status_code=200, json_data=None):
    resp = MagicMock()
    resp.ok = 200 <= status_code < 300
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    return resp


@pytest.fixture
def client():
    return V1Client(api_key="test_key_123")


def test_requires_api_key():
    with pytest.raises(ValueError):
        V1Client(api_key="")


def test_create_payment_sends_correct_request(client):
    expected = {"status": "success", "payment": {"_id": 1, "_uuid": "abc"}}
    with patch.object(client._session, "post", return_value=_mock_response(200, expected)) as mock_post:
        result = client.create_payment(amount=50000, description="test order")

    assert result == expected
    args, kwargs = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v1/create_payment"
    assert kwargs["headers"]["Authorization"] == "Bearer test_key_123"
    assert kwargs["json"] == {"amount": 50000, "description": "test order"}


def test_optional_none_params_are_omitted(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success"})) as mock_post:
        client.create_payment(amount=1000)

    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {"amount": 1000}


def test_error_response_raises(client):
    with patch.object(client._session, "post", return_value=_mock_response(401, {"error": "Unauthorized: Invalid or missing Bearer token"})):
        with pytest.raises(CheckoutAPIError) as exc_info:
            client.get_balance()

    assert exc_info.value.status_code == 401
    assert "Unauthorized" in exc_info.value.message


def test_status_payment_requires_id_or_uuid(client):
    with pytest.raises(ValueError):
        client.status_payment()


def test_status_payment_by_uuid(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success"})) as mock_post:
        client.status_payment(uuid="abc-123")

    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {"uuid": "abc-123"}


def test_network_error_raises_checkout_api_error(client):
    import requests
    with patch.object(client._session, "post", side_effect=requests.ConnectionError("boom")):
        with pytest.raises(CheckoutAPIError):
            client.get_balance()


def test_pay_via_card(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success"})) as mock_post:
        client.pay_via_card(order_id=5, card_number="8600123412341234", card_expiry="1230")

    args, kwargs = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v1/pay_via_card"
    assert kwargs["json"] == {"order_id": 5, "card_number": "8600123412341234", "card_expiry": "1230"}


def test_confirm_card_payment(client):
    with patch.object(client._session, "post", return_value=_mock_response(200, {"status": "success"})) as mock_post:
        client.confirm_card_payment(payment_token="tok", sms_code="123456")

    args, kwargs = mock_post.call_args
    assert args[0] == "https://checkout.uz/api/v1/confirm_card_payment"
    assert kwargs["json"] == {"payment_token": "tok", "sms_code": "123456"}
