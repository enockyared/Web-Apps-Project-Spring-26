from unittest.mock import Mock, patch

from app.extensions import cache
from app.service.alpha_vantage_client import (
    get_company_name,
    get_price_data,
    get_quote,
)


def test_get_company_name_success(app):
    with app.app_context():
        cache.clear()

        mock_response = Mock()
        mock_response.json.return_value = {
            "Name": "Apple Inc."
        }

        with patch("app.service.alpha_vantage_client.requests.get", return_value=mock_response) as mock_get:
            result = get_company_name("AAPL")

            assert result == "Apple Inc."
            assert mock_get.call_count == 1


def test_get_company_name_returns_none_for_unexpected_response(app):
    with app.app_context():
        cache.clear()

        mock_response = Mock()
        mock_response.json.return_value = {}

        with patch(
            "app.service.alpha_vantage_client.requests.get",
            return_value=mock_response,
        ) as mock_get:
            result = get_company_name("BAD")

            assert result is None
            assert mock_get.call_count == 1


def test_get_price_data_success(app):
    with app.app_context():
        cache.clear()

        mock_response = Mock()
        mock_response.json.return_value = {
            "Time Series (Daily)": {
                "2026-03-11": {
                    "1. open": "261.09",
                    "2. high": "262.13",
                    "3. low": "259.55",
                    "4. close": "260.81",
                    "5. volume": "25777354",
                }
            }
        }

        with patch("app.service.alpha_vantage_client.requests.get", return_value=mock_response) as mock_get:
            result = get_price_data("AAPL")

            assert result == {
                "date": "2026-03-11",
                "open": 261.09,
                "high": 262.13,
                "low": 259.55,
                "close": 260.81,
                "volume": 25777354,
            }
            assert mock_get.call_count == 1


def test_get_price_data_returns_none_for_unexpected_response(app):
    with app.app_context():
        cache.clear()

        mock_response = Mock()
        mock_response.json.return_value = {}

        with patch("app.service.alpha_vantage_client.requests.get", return_value=mock_response) as mock_get:
            result = get_price_data("BAD")

            assert result is None
            assert mock_get.call_count == 1


def test_get_company_name_uses_cache(app):
    with app.app_context():
        cache.clear()
        cache.set("company_name:AAPL", "Apple Inc.")

        with patch("app.service.alpha_vantage_client.requests.get") as mock_get:
            result = get_company_name("AAPL")

            assert result == "Apple Inc."
            mock_get.assert_not_called()


def test_get_price_data_uses_cache(app):
    with app.app_context():
        cache.clear()
        cached_price = {
            "date": "2026-03-11",
            "open": 261.09,
            "high": 262.13,
            "low": 259.55,
            "close": 260.81,
            "volume": 25777354,
        }
        cache.set("price_data:AAPL", cached_price)

        with patch("app.service.alpha_vantage_client.requests.get") as mock_get:
            result = get_price_data("AAPL")

            assert result == cached_price
            mock_get.assert_not_called()


def test_get_quote_success(app):
    with app.app_context():
        cache.clear()

        with patch("app.service.alpha_vantage_client.get_company_name", return_value="Apple Inc.") as mock_name:
            with patch(
                "app.service.alpha_vantage_client.get_price_data",
                return_value={
                    "date": "2026-03-11",
                    "open": 261.09,
                    "high": 262.13,
                    "low": 259.55,
                    "close": 260.81,
                    "volume": 25777354,
                },
            ) as mock_price:
                quote = get_quote("AAPL")

                assert quote is not None
                assert quote.ticker == "AAPL"
                assert quote.issuer == "Apple Inc."
                assert quote.date == "2026-03-11"
                assert quote.price == 260.81
                assert mock_name.called
                assert mock_price.called


def test_get_quote_returns_none_when_company_name_missing(app):
    with app.app_context():
        cache.clear()

        with patch("app.service.alpha_vantage_client.get_company_name", return_value=None):
            with patch(
                "app.service.alpha_vantage_client.get_price_data",
                return_value={
                    "date": "2026-03-11",
                    "open": 261.09,
                    "high": 262.13,
                    "low": 259.55,
                    "close": 260.81,
                    "volume": 25777354,
                },
            ):
                quote = get_quote("BAD")
                assert quote is None


def test_get_quote_returns_none_when_price_data_missing(app):
    with app.app_context():
        cache.clear()

        with patch("app.service.alpha_vantage_client.get_company_name", return_value="Apple Inc."):
            with patch("app.service.alpha_vantage_client.get_price_data", return_value=None):
                quote = get_quote("AAPL")
                assert quote is None