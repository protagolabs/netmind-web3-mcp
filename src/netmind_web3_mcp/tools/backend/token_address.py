"""Token address query tools using backend API."""

import httpx
from .config import get_config


async def query_token_addressList(tokenName: str = None, tokenAddress: str = None) -> str:
    """Query address list based on token name or address.
     
    Args:
        tokenName: Symbol of the token
        tokenAddress: Address of the token
    
    At least one of tokenName or tokenAddress must be provided.
    """
    if not tokenName and not tokenAddress:
        raise ValueError("At least one of tokenName or tokenAddress must be provided")
    
    config = get_config()
    base_url = config.get_base_url()
    
    params = []
    if tokenName:
        params.append(f"tokenName={tokenName}")
    if tokenAddress:
        params.append(f"tokenAddress={tokenAddress}")
    
    url = f"{base_url}?{'&'.join(params)}" if params else base_url
    
    response = httpx.get(url, timeout=config.get_timeout())
    response.raise_for_status()
    return response.text
