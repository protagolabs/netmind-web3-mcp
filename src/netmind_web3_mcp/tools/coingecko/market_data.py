"""CoinGecko API tools for cryptocurrency market data."""

import httpx
import json
import asyncio
from .config import get_config


async def query_coingecko_market_data(
    vs_currency: str = "usd",
    ids: str = None,
    names: str = None,
    symbols: str = None,
    include_tokens: str = "top",
    category: str = None,
    order: str = "market_cap_desc",
    per_page: int = 100,
    page: int = 1,
    price_change_percentage: str = "1h",
    locale: str = "en",
    precision: str = None,
) -> str:
    """Query CoinGecko for cryptocurrency market data with history chart data.
    
    References:
    - Market Data: https://docs.coingecko.com/reference/coins-markets
    - Market Chart: https://docs.coingecko.com/reference/coins-id-market-chart
    """
    config = get_config()
    base_url = config.get_base_url()
    headers = config.get_headers()
    timeout = config.get_timeout()
    semaphore = config.get_semaphore()
    
    # Build parameters
    params = {"vs_currency": vs_currency}
    if ids:
        params["ids"] = ids
    if names:
        params["names"] = names
    if symbols:
        params["symbols"] = symbols
        params["include_tokens"] = include_tokens
    if category:
        params["category"] = category
    if order:
        params["order"] = order
    if per_page:
        params["per_page"] = per_page
    if page:
        params["page"] = page
    if price_change_percentage:
        params["price_change_percentage"] = price_change_percentage
    if locale:
        params["locale"] = locale
    if precision:
        params["precision"] = precision
    
    # Get market data
    response = httpx.get(f"{base_url}/coins/markets", params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    market_data = response.json()
    
    # Fetch history chart data concurrently
    async def fetch_history_chart(client, coin):
        coin_id = coin.get("id")
        if not coin_id:
            coin["history_chart"] = []
            return
        
        async with semaphore:
            try:
                url = f"{base_url}/coins/{coin_id}/market_chart"
                resp = await client.get(url, params={"vs_currency": vs_currency, "days": 7}, 
                                       headers=headers, timeout=timeout)
                resp.raise_for_status()
                coin["history_chart"] = resp.json()
            except Exception:
                coin["history_chart"] = []
    
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[fetch_history_chart(client, coin) for coin in market_data])
    
    return json.dumps(market_data, indent=2)
