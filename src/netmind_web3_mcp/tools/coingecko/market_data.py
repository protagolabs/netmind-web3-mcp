"""CoinGecko API tools for cryptocurrency market data."""

from typing import Optional
import httpx
import json
import asyncio
from .config import get_config


async def query_coingecko_market_data(
    vs_currency: str = "usd",
    ids: Optional[str] = None,
    names: Optional[str] = None,
    symbols: Optional[str] = None,
    include_tokens: str = "top",
    category: Optional[str] = None,
    order: str = "market_cap_desc",
    per_page: int = 100,
    page: int = 1,
    price_change_percentage: str = "1h",
    locale: str = "en",
    precision: Optional[str] = None,
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


async def query_coingecko_top_token_traders(
    token_address: str,
    network_id: str = "base",
    traders: int = 10,
    sort: str = "realized_pnl_usd_desc",
    include_address_label: bool = False,
) -> str:
    """Query CoinGecko for top token traders by token address.
    
    This endpoint allows you to query top token traders based on the provided token contract address on a network.
    
    References:
    - Top Token Traders: https://docs.coingecko.com/reference/top-token-traders-token-address
    
    Args:
        token_address: Token contract address (required)
        network_id: Network ID (default: "base"). Refers to /networks endpoint
        traders: Number of top token traders to return (default: 10, max: 50)
        sort: Sort the traders by field (default: "realized_pnl_usd_desc")
            Options: "realized_pnl_usd_desc", "unrealized_pnl_usd_desc", 
                     "total_buy_usd_desc", "total_sell_usd_desc"
        include_address_label: Include address label data (default: False)
    
    Returns:
        JSON string containing top traders data with attributes like:
        - address: Trader wallet address
        - name: Trader name
        - label: Address label (e.g., ENS name)
        - type: Trader type
        - realized_pnl_usd: Realized profit/loss in USD
        - unrealized_pnl_usd: Unrealized profit/loss in USD
        - token_balance: Current token balance
        - average_buy_price_usd: Average buy price
        - average_sell_price_usd: Average sell price
        - total_buy_count: Total number of buy transactions
        - total_sell_count: Total number of sell transactions
        - total_buy_token_amount: Total tokens bought
        - total_sell_token_amount: Total tokens sold
        - total_buy_usd: Total USD spent on buys
        - total_sell_usd: Total USD received from sells
        - explorer_url: Link to blockchain explorer
    
    Note:
        - Top traders data is currently in Beta
        - Only tokens created after 1st September 2022 are supported
        - Stablecoins and wrapped native tokens (e.g. wSOL, wETH) are not supported
        - Exclusive for Paid Plan subscribers (Analyst plan or above)
        - Cache/Update frequency: every 60 seconds
    
    Example:
        query_coingecko_top_token_traders(
            token_address="0x6921b130d297cc43754afba22e5eac0fbf8db75b",
            network_id="base",
            traders=10,
            sort="realized_pnl_usd_desc"
        )
    """
    if not token_address or not token_address.strip():
        raise ValueError("token_address parameter is required and cannot be empty")
    
    # Validate traders parameter
    if traders < 1 or traders > 50:
        raise ValueError("traders parameter must be between 1 and 50")
    
    # Validate sort parameter
    valid_sorts = [
        "realized_pnl_usd_desc",
        "unrealized_pnl_usd_desc",
        "total_buy_usd_desc",
        "total_sell_usd_desc",
    ]
    if sort not in valid_sorts:
        raise ValueError(f"sort must be one of: {', '.join(valid_sorts)}")
    
    config = get_config()
    base_url = config.get_base_url()
    headers = config.get_headers()
    timeout = config.get_timeout()
    
    # Build URL with path parameters
    url = f"{base_url}/onchain/networks/{network_id}/tokens/{token_address}/top_traders"
    
    # Build query parameters
    params = {
        "traders": str(traders),
        "sort": sort,
        "include_address_label": str(include_address_label).lower(),
    }
    
    response = httpx.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    result = response.json()
    
    return json.dumps(result, indent=2)


async def query_coingecko_pool_trades(
    pool_address: str,
    network: str = "eth",
    trade_volume_in_usd_greater_than: float = 0.0,
    token: str = "base",
) -> str:
    """Query CoinGecko for past 24 hour trades by pool address.
    
    This endpoint allows you to query the last 300 trades in the past 24 hours based on the provided pool address.
    
    References:
    - Pool Trades: https://docs.coingecko.com/reference/pool-trades-contract-address
    
    Args:
        pool_address: Pool contract address (required)
        network: Network ID (default: "eth"). Refers to /networks endpoint
        trade_volume_in_usd_greater_than: Filter trades by trade volume in USD greater than this value (default: 0.0)
        token: Return trades for token. Use this to invert the chart (default: "base")
            Options: "base", "quote", or token address
    
    Returns:
        JSON string containing trades data with attributes like:
        - id: Trade ID
        - type: Trade type
        - attributes:
          - block_number: Block number
          - tx_hash: Transaction hash
          - tx_from_address: Transaction from address
          - from_token_amount: Amount of from token
          - to_token_amount: Amount of to token
          - price_from_in_currency_token: Price of from token in currency token
          - price_to_in_currency_token: Price of to token in currency token
          - price_from_in_usd: Price of from token in USD
          - price_to_in_usd: Price of to token in USD
          - block_timestamp: Block timestamp
          - kind: Trade kind (buy/sell)
          - volume_in_usd: Trade volume in USD
          - from_token_address: From token contract address
          - to_token_address: To token contract address
    
    Note:
        - Cache/Update Frequency: Real-time (Cacheless) for Pro API (Basic, Analyst, Lite, Pro, Enterprise)
        - Returns last 300 trades in past 24 hours
    
    Example:
        query_coingecko_pool_trades(
            pool_address="0x06da0fd433c1a5d7a4faa01111c044910a184553",
            network="eth"
        )
    """
    if not pool_address or not pool_address.strip():
        raise ValueError("pool_address parameter is required and cannot be empty")
    
    config = get_config()
    base_url = config.get_base_url()
    headers = config.get_headers()
    timeout = config.get_timeout()
    
    # Build URL with path parameters
    url = f"{base_url}/onchain/networks/{network}/pools/{pool_address}/trades"
    
    # Build query parameters
    params = {
        "trade_volume_in_usd_greater_than": str(trade_volume_in_usd_greater_than),
        "token": token,
    }
    
    response = httpx.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    result = response.json()
    
    return json.dumps(result, indent=2)


async def query_coingecko_token_trades(
    token_address: str,
    network: str = "eth",
    trade_volume_in_usd_greater_than: float = 0.0,
) -> str:
    """Query CoinGecko for past 24 hour trades by token address.
    
    This endpoint allows you to query the last 300 trades in the past 24 hours, across all pools, 
    based on the provided token contract address on a network.
    
    References:
    - Token Trades: https://docs.coingecko.com/reference/token-trades-contract-address
    
    Args:
        token_address: Token contract address (required)
        network: Network ID (default: "eth"). Refers to /networks endpoint
        trade_volume_in_usd_greater_than: Filter trades by trade volume in USD greater than this value (default: 0.0)
    
    Returns:
        JSON string containing trades data with attributes like:
        - id: Trade ID
        - type: Trade type
        - attributes:
          - pool_address: Pool contract address
          - pool_dex: DEX name (e.g., "sushiswap")
          - block_number: Block number
          - tx_hash: Transaction hash
          - tx_from_address: Transaction from address
          - from_token_amount: Amount of from token
          - to_token_amount: Amount of to token
          - price_from_in_currency_token: Price of from token in currency token
          - price_to_in_currency_token: Price of to token in currency token
          - price_from_in_usd: Price of from token in USD
          - price_to_in_usd: Price of to token in USD
          - block_timestamp: Block timestamp
          - kind: Trade kind (buy/sell)
          - volume_in_usd: Trade volume in USD
          - from_token_address: From token contract address
          - to_token_address: To token contract address
    
    Note:
        - Exclusive for all Paid Plan Subscribers (Analyst, Lite, Pro and Enterprise)
        - Cache/Update Frequency: Real-time (Cacheless) for Pro API (Analyst, Lite, Pro, Enterprise)
        - Returns last 300 trades in past 24 hours across all pools
    
    Example:
        query_coingecko_token_trades(
            token_address="0xdac17f958d2ee523a2206206994597c13d831ec7",
            network="eth"
        )
    """
    if not token_address or not token_address.strip():
        raise ValueError("token_address parameter is required and cannot be empty")
    
    config = get_config()
    base_url = config.get_base_url()
    headers = config.get_headers()
    timeout = config.get_timeout()
    
    # Build URL with path parameters
    url = f"{base_url}/onchain/networks/{network}/tokens/{token_address}/trades"
    
    # Build query parameters
    params = {
        "trade_volume_in_usd_greater_than": str(trade_volume_in_usd_greater_than),
    }
    
    response = httpx.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    result = response.json()
    
    return json.dumps(result, indent=2)
