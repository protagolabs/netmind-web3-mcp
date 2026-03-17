"""Investment pool query tools using backend API."""

import os
from typing import Any
import httpx
from .config import get_config


async def query_investment_pool_json(trade_id: int, data: list[Any], message: str) -> str:
    """Submit investment pool JSON data for a given trade.

    Calls POST /investment/poolJson and returns the raw JSON response from the backend.

    Args:
        trade_id: The trade ID.
        data: List of pool data objects.
        message: Status message (e.g. "success").

    Returns:
        Response in JSON format.
    """
    config = get_config()
    base_url = config.get_base_url()

    url = f"{base_url}/investment/poolJson"

    pool_key = os.environ.get("BACKEND_POOL_KEY", "")
    headers = {"pool-key": pool_key}

    payload = {"tradeId": trade_id, "data": data, "message": message}

    response = httpx.post(url, json=payload, headers=headers, timeout=config.get_timeout())
    response.raise_for_status()
    return response.text
