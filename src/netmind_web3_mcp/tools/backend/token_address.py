"""Token address query tools using backend API."""

from typing import Optional
import httpx
from .config import get_config


async def query_token_addressList(
    token_symbol: Optional[str] = None,
    token_address: Optional[str] = None,
) -> str:
    """Query address list based on token symbol or address.
    
    Args:
        token_symbol: Token symbol(s). Can be a single token symbol or comma-separated values (e.g., "DINO" or "DINO,BALD")
        token_address: Token contract address(es). Can be a single address or comma-separated values (e.g., "0x..." or "0x...,0x...")
    
    At least one of token_symbol or token_address must be provided.
    Multiple values can be provided as comma-separated strings.
    
    Example:
        - Single token: token_symbol="DINO"
        - Multiple tokens: token_symbol="DINO,BALD"
        - Single address: token_address="0x85e90a5430af45776548adb82ee4cd9e33b08077"
        - Multiple addresses: token_address="0x85e90a5430af45776548adb82ee4cd9e33b08077,0xfe20c1b85aba875ea8cecac8200bf86971968f3a"
    """
    if not token_symbol and not token_address:
        raise ValueError("At least one of token_symbol or token_address must be provided")
    
    config = get_config()
    base_url = config.get_base_url()
    
    # Append the route path to the base URL
    route_path = "/tokenAddress/queryTokenAddressList"
    url = f"{base_url}{route_path}"
    
    # Build query parameters using httpx params for proper URL encoding
    params = {}
    if token_symbol:
        params["tokenName"] = token_symbol
    if token_address:
        params["tokenAddress"] = token_address
    
    response = httpx.get(url, params=params, timeout=config.get_timeout())
    response.raise_for_status()
    return response.text
