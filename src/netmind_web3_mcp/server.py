import httpx
import os
import json
import asyncio
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("netmind-web3-mcp")


@mcp.tool()
async def query_token_addressList(tokenName: str = None, tokenAddress: str = None) -> str:
    """Query address list based on token name or address.
     
    Args:
    tokenName: Symbol of the token
    tokenAddress: Address of the token
    
    At least one of tokenName or tokenAddress must be provided.
    """
    
    if not tokenName and not tokenAddress:
        raise ValueError("At least one of tokenName or tokenAddress must be provided")
    
    baseUrl = os.environ.get("BACKEND_URL")
    if not baseUrl:
        raise ValueError("BACKEND_URL environment variable is not set")
    
    params = []
    if tokenName:   
        params.append(f"tokenName={tokenName}")
    if tokenAddress:
        params.append(f"tokenAddress={tokenAddress}")
    
    if params:
        baseUrl += "?" + "&".join(params)
    
    response = httpx.get(baseUrl, timeout=10.0)
    response.raise_for_status()
    return response.text

@mcp.tool()
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
    """Query CoinGecko for cryptocurrency market data with OHLC data.
    
    This function fetches market data and also includes OHLC (Open, High, Low, Close) data 
    for the past 7 days for each coin.
    
    References:
    - Market Data: https://docs.coingecko.com/reference/coins-markets
    - OHLC Data: https://docs.coingecko.com/reference/coins-id-ohlc-range

    Args:
        vs_currency: The target currency of the market data (e.g., "usd", "eur"). Required.
        ids: The IDs of the coins to fetch, comma-separated if querying more than 1 coin (e.g., "bitcoin,ethereum").
        names: The names of the coins to fetch, comma-separated (e.g., "Bitcoin,Ethereum"). URL-encode spaces.
        symbols: The symbols of the coins to fetch, comma-separated (e.g., "btc,eth").
        include_tokens: For symbols lookups, specify "all" to include all matching tokens. Default "top" returns top-ranked tokens.
        category: Filter based on coins' category (e.g., "layer-1"). Refer to /coins/categories/list for available categories.
        order: Sort result by field. Options: market_cap_asc, market_cap_desc, volume_asc, volume_desc, id_asc, id_desc. Default: market_cap_desc.
        per_page: Total results per page. Valid values: 1-250. Default: 100.
        page: Page through results. Default: 1.
        price_change_percentage: Include price change percentage timeframe, comma-separated if query more than 1 timeframe. Valid values: 1h, 24h, 7d, 14d, 30d, 200d, 1y. Default: 1h.
        locale: Language background. Default: en.
        precision: Decimal place for currency price value. Options: full, 0-18. Default: full.
    
    Returns:
        JSON string containing market data with an additional "ohlc_7d" field for each coin.
        The OHLC data format: [[timestamp, open, high, low, close], ...]
    """
    
    apiKey = os.environ.get("COINGECKO_API_KEY")
    if not apiKey:
        raise ValueError("COINGECKO_API_KEY environment variable is not set")

    baseUrl = "https://pro-api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
    }
    
    # Add optional parameters
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

    # API key should be passed via header, not query parameter
    headers = {
        "x-cg-pro-api-key": apiKey
    }
    
    # Get market data
    response = httpx.get(baseUrl, params=params, headers=headers, timeout=20.0)
    response.raise_for_status()
    market_data = response.json()
    
    # Calculate date range: 7 days ago to today
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    from_date = seven_days_ago.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    # Limit concurrent requests to avoid rate limiting (max 10 concurrent)
    semaphore = asyncio.Semaphore(10)
    
    # Fetch OHLC data for all coins concurrently
    async def fetch_ohlc(client, coin):
        coin_id = coin.get("id")
        if not coin_id:
            coin["ohlc_7d"] = []
            return
        
        async with semaphore:
            try:
                ohlc_url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/ohlc/range"
                ohlc_params = {
                    "vs_currency": vs_currency,
                    "from": from_date,
                    "to": to_date,
                    "interval": "daily"
                }
                ohlc_response = await client.get(ohlc_url, params=ohlc_params, headers=headers, timeout=20.0)
                ohlc_response.raise_for_status()
                coin["ohlc_7d"] = ohlc_response.json()
            except Exception:
                # If OHLC fetch fails for any reason, set to empty array
                coin["ohlc_7d"] = []
    
    # Execute all OHLC requests concurrently using a shared client
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[fetch_ohlc(client, coin) for coin in market_data])
    
    return json.dumps(market_data, indent=2)


def main():
    if not os.environ.get("BACKEND_URL"):
        raise ValueError(
            "Environment variable BACKEND_URL is not set. Please set it."
        )
    
    if not os.environ.get("COINGECKO_API_KEY"):
        raise ValueError(
            "Environment variable COINGECKO_API_KEY is not set. Please set it."
        )
    
    print("Starting Netmind Web3 MCP server...")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()