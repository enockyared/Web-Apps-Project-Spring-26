from dataclasses import dataclass
from typing import Optional

import requests
from flask import current_app
from app.extensions import cache


@dataclass
class SecurityQuote:
    ticker: str
    date: str
    price: float
    issuer: str


def _get_api_key() -> str:
    api_key = current_app.config.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("Alpha Vantage API key is not configured.")
    return api_key


def get_company_name(ticker: str) -> Optional[str]:
    cache_key = f"company_name:{ticker.upper()}"
    cached_value = cache.get(cache_key)
    if cached_value is not None:
        return cached_value

    api_key = _get_api_key()
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": api_key,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "Name" not in data:
        return None

    company_name = data["Name"]
    cache.set(cache_key, company_name)
    return company_name


def get_price_data(ticker: str) -> Optional[dict]:
    cache_key = f"price_data:{ticker.upper()}"
    cached_value = cache.get(cache_key)
    if cached_value is not None:
        return cached_value

    api_key = _get_api_key()
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "apikey": api_key,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "Note" in data:
        raise ValueError(f"Alpha Vantage rate limit hit: {data['Note']}")

    if "Information" in data:
        raise ValueError(f"Alpha Vantage info response: {data['Information']}")

    if "Error Message" in data:
        return None

    if "Time Series (Daily)" not in data:
        return None

    latest_date = next(iter(data["Time Series (Daily)"]))
    latest_data = data["Time Series (Daily)"][latest_date]

    price_data = {
        "date": latest_date,
        "open": float(latest_data["1. open"]),
        "high": float(latest_data["2. high"]),
        "low": float(latest_data["3. low"]),
        "close": float(latest_data["4. close"]),
        "volume": int(latest_data["5. volume"]),
    }

    cache.set(cache_key, price_data)
    return price_data

def get_quote(ticker: str) -> Optional[SecurityQuote]:
    issuer = get_company_name(ticker)
    price_data = get_price_data(ticker)

    if issuer is None or price_data is None:
        return None

    return SecurityQuote(
        ticker=ticker.upper(),
        issuer=issuer,
        date=price_data["date"],
        price=price_data["close"],
    )