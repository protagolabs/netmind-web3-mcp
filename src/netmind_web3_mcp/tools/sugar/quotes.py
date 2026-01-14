"""Sugar MCP quote-related tools."""

from typing import Optional
from netmind_sugar.chains import get_chain
from .models import QuoteInfo
from .cache import _get_cached_pools
from .pools import _convert_pools_to_swap_format
from .config import validate_cache_parameter


async def query_sugar_get_quote(
    from_token: str,
    to_token: str,
    amount: int,
    chainId: str = "8453",
    use_cache: bool = True,
) -> Optional[QuoteInfo]:
    """Retrieve the best quote for swapping a given amount from one token to another.

    Args:
        from_token: The token to swap from. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. 
                    For BaseChain, this can be 'usdc', 'aero', or 'eth'. 
                    For Unichain, this can be 'o_usdt' or 'usdc'. 
                    For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'
        to_token: The token to swap to. Same options as from_token
        amount: The amount to swap (unit is wei)
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached pool addresses. Defaults to True. Not available in stdio mode.

    Returns:
        Optional[QuoteInfo]: The best available quote, or None if no valid quote was found
    """
    validate_cache_parameter(use_cache, "query_sugar_get_quote")
    # Validate token support by chain
    chain_tokens = {
        "10": ["usdc", "velo", "eth", "o_usdt"],
        "130": ["o_usdt", "usdc"],
        "1135": ["o_usdt", "lsk", "eth", "usdt"],
        "8453": ["usdc", "aero", "eth"],
    }
    
    if chainId in chain_tokens:
        supported_tokens = chain_tokens[chainId]
        if from_token not in supported_tokens or to_token not in supported_tokens:
            raise ValueError(f"Only {', '.join(repr(t) for t in supported_tokens)} are supported on chain {chainId}.")

    with get_chain(chainId) as chain:
        from_token_obj = getattr(chain, from_token, None)
        to_token_obj = getattr(chain, to_token, None)
        if from_token_obj is None or to_token_obj is None:
            raise ValueError("Invalid token specified.")

        if use_cache:
            cached_pools = _get_cached_pools(chainId)
            if cached_pools:
                try:
                    pools_for_swap = _convert_pools_to_swap_format(cached_pools)
                    original_get_pools_for_swaps = chain.get_pools_for_swaps
                    chain.get_pools_for_swaps = lambda: pools_for_swap
                    
                    try:
                        quote = chain.get_quote(from_token_obj, to_token_obj, amount)
                        return QuoteInfo.from_quote(quote) if quote else None
                    finally:
                        chain.get_pools_for_swaps = original_get_pools_for_swaps
                except Exception as e:
                    print(f"Warning: Failed to use cached pools, falling back to chain query: {e}")
        
        quote = chain.get_quote(from_token_obj, to_token_obj, amount)
        return QuoteInfo.from_quote(quote) if quote else None

