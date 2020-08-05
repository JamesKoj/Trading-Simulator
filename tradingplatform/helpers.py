import requests
import urllib.parse
import os


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/"
                                f"{urllib.parse.quote_plus(symbol)}/quote?token={os.environ.get('API_TOKEN')}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"