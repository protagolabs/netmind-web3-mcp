"""Sugar MCP pool-related tools."""

from math import e
from typing import Optional
from netmind_sugar.chains import get_chain, LiquidityPool, LiquidityPoolForSwap
from web3 import Web3
from .models import (
    LiquidityPoolInfo,
    LiquidityPoolForSwapInfo,
    LiquidityPoolEpochInfo,
)
from .cache import (
    _get_cached_pools,
    _get_pool_from_cache,
    _get_pools_from_chain,
    _get_pool_from_chain,
)
from .config import validate_cache_parameter


def _safe_get_amount_in_stable(amount_obj, default=0.0):
    """Safely extract amount_in_stable from an amount object."""
    if amount_obj is None:
        return default
    if isinstance(amount_obj, (int, float)):
        return float(amount_obj)
    if hasattr(amount_obj, 'amount_in_stable') and amount_obj.amount_in_stable is not None:
        return amount_obj.amount_in_stable
    return default


def _convert_pools_to_swap_format(pools: list) -> list:
    """Convert cached LiquidityPool objects to LiquidityPoolForSwap format."""
    result = []
    for p in pools:
        try:
            pool_type = p.type
            if isinstance(pool_type, str):
                pool_type = int(pool_type)
            elif pool_type is None:
                pool_type = 0
            else:
                pool_type = int(pool_type)
            
            pool_obj = LiquidityPoolForSwap(
                chain_id=str(p.chain_id),
                chain_name=str(p.chain_name),
                lp=str(p.lp),
                type=pool_type,
                token0_address=str(p.token0.token_address),
                token1_address=str(p.token1.token_address)
            )
            
            if not isinstance(pool_obj.type, int):
                raise TypeError(f"Pool type must be int, got {type(pool_obj.type)}: {pool_obj.type}")
            
            result.append(pool_obj)
        except Exception as e:
            print(f"Error converting pool {p.lp}: {e}, type={type(p.type)}, value={p.type}")
            raise
    return result


async def query_sugar_get_pools_for_swaps(
    limit: int,
    offset: int,
    chainId: str = "8453",
    use_cache: bool = True,
) -> list | str:
    """Retrieve all raw liquidity pools suitable for swaps.

    Args:
        limit: The maximum number of pools to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached data. Defaults to True. Not available in stdio mode.

    Returns:
        List[LiquidityPoolForSwapInfo] | str: A list of simplified pool objects for swaps or "Not Find"
    """
    validate_cache_parameter(use_cache, "query_sugar_get_pools_for_swaps")
    pools = _get_cached_pools(chainId) if use_cache else _get_pools_from_chain(chainId)
    
    if not pools:
        return "Not Find"
    
    pools_for_swap = _convert_pools_to_swap_format(pools)
    paginated_pools = pools_for_swap[offset:offset + limit]
    
    result = [LiquidityPoolForSwapInfo.from_pool(p) for p in paginated_pools]
    if not result:
        return "Not Find"
    return result


async def query_sugar_get_pool_list(
    lp: Optional[str] = None,
    token_address_list: Optional[list[str]] = None,
    pool_type: str = "all",
    sort_by: str = "tvl",
    limit: int = 10,
    offset: int = 0,
    chainId: str = "8453",
    use_cache: bool = True,
) -> list | str:
    """Retrieve liquidity pools based on specified criteria.

    Args:
        lp: Address of the liquidity pool
        token_address_list: List of token addresses to filter pools. Only one or two tokens are supported for filtering. If None, no token filtering is applied
        pool_type: The type of pools to retrieve ('v2', 'v3' or 'all')
        sort_by: The criterion to sort the pools by ('tvl', 'volume', or 'apr')
        limit: The maximum number of pools to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached data. Defaults to True. Not available in stdio mode.

    Returns:
        list[LiquidityPoolInfo] | str: A list of liquidity pool information or "Not Find"
    """
    # limit is max 10
    limit = min(limit, 10)
    
    validate_cache_parameter(use_cache, "query_sugar_get_pool_list")
    if lp is not None:
        lp = Web3.to_checksum_address(lp)
        pool = _get_pool_from_cache(chainId, lp) if use_cache else _get_pool_from_chain(chainId, lp)
        return [LiquidityPoolInfo.from_pool(pool)] if pool else "Not Find"

    pools = _get_cached_pools(chainId) if use_cache else _get_pools_from_chain(chainId)
    if not pools:
        return "Not Find"

    if token_address_list is not None:
        if len(token_address_list) == 1:
            pools = [p for p in pools if p.token0.token_address == token_address_list[0] or p.token1.token_address == token_address_list[0]]
        elif len(token_address_list) == 2:
            pools = [p for p in pools if (
                (p.token0.token_address == token_address_list[0] and p.token1.token_address == token_address_list[1]) or
                (p.token0.token_address == token_address_list[1] and p.token1.token_address == token_address_list[0])
            )]
        else:
            raise ValueError("Only one or two tokens are supported for filtering.")

    if pool_type not in ["v2", "v3", "all"]:
        raise ValueError("Unsupported pool_type. Use 'v2', 'v3', or 'all'.")
    
    if pool_type != "all":
        pools = [p for p in pools if (pool_type == "v3") == p.is_cl]

    sort_keys = {
        "tvl": lambda p: p.tvl,
        "volume": lambda p: _safe_get_amount_in_stable(p.volume),
        "apr": lambda p: p.apr,
    }
    if sort_by not in sort_keys:
        raise ValueError("Unsupported sort_by criteria. Use 'tvl', 'volume', or 'apr'.")
    pools.sort(key=sort_keys[sort_by], reverse=True)

    pools = pools[offset:offset+limit]
    if not pools:
        return "Not Find"
    return [LiquidityPoolInfo.from_pool(p) for p in pools]


async def query_sugar_get_latest_pool_epochs(
    offset: int,
    limit: int = 10,
    chainId: str = "8453",
) -> list | str:
    """Retrieve the latest epoch data for all pools.

    Args:
        limit: The maximum number of epochs to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolEpochInfo] | str: A list of epochs or "Not Find"
    """
    with get_chain(chainId) as chain:
        epochs = chain.get_latest_pool_epochs_page(limit, offset)
        # Filter out None values in case the API returns None entries
        result = [LiquidityPoolEpochInfo.from_epoch(p) for p in epochs if p is not None]
        if not result:
            return "Not Find"
        return result


async def query_sugar_get_pool_epochs(
    lp: str,
    offset: int = 0,
    limit: int = 10,
    chainId: str = "8453",
) -> list | str:
    """Retrieve historical epoch data for a given liquidity pool.

    Args:
        lp: Address of the liquidity pool
        offset: Offset for pagination
        limit: Number of epochs to retrieve
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolEpochInfo] | str: A list of epoch entries or "Not Find"
    """
    lp = Web3.to_checksum_address(lp)
    with get_chain(chainId) as chain:
        epochs = chain.get_pool_epochs_page(lp, offset, limit)
        # Filter out None values in case the API returns None entries
        result = [LiquidityPoolEpochInfo.from_epoch(p) for p in epochs if p is not None]
        if not result:
            return "Not Find"
        return result
    
