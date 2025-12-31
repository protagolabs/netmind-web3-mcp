"""Sugar MCP pool-related tools."""

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


def _filter_pools_by_token(pools: list, token_address: str) -> list:
    """Filter pools that contain a specific token."""
    return [p for p in pools if p.token0.token_address == token_address or p.token1.token_address == token_address]


def _filter_pools_by_pair(pools: list, token0_address: str, token1_address: str) -> list:
    """Filter pools that contain a specific token pair."""
    return [p for p in pools if (
        (p.token0.token_address == token0_address and p.token1.token_address == token1_address) or
        (p.token0.token_address == token1_address and p.token1.token_address == token0_address)
    )]


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


async def query_sugar_get_pools(
    limit: int = 30,
    offset: int = 0,
    chainId: str = "8453",
    use_cache: bool = True,
) -> list:
    """Retrieve all raw liquidity pools.

    Args:
        limit: The maximum number of pools to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached data. Defaults to True. Not available in stdio mode.

    Returns:
        List[LiquidityPoolInfo]: A list of pool objects
    """
    validate_cache_parameter(use_cache, "query_sugar_get_pools")
    pools = _get_cached_pools(chainId) if use_cache else _get_pools_from_chain(chainId)
    paginated_pools = pools[offset:offset + limit]
    return [LiquidityPoolInfo.from_pool(p) for p in paginated_pools]


async def query_sugar_get_pool_by_address(
    address: str,
    chainId: str = "8453",
    use_cache: bool = True,
) -> LiquidityPoolInfo | None:
    """Retrieve a raw liquidity pool by its contract address.

    Args:
        address: The address of the liquidity pool contract
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached data. Defaults to True. Not available in stdio mode.

    Returns:
        Optional[LiquidityPoolInfo]: The matching LiquidityPool object, or None if not found
    """
    validate_cache_parameter(use_cache, "query_sugar_get_pool_by_address")
    address = Web3.to_checksum_address(address)
    pool = _get_pool_from_cache(chainId, address) if use_cache else _get_pool_from_chain(chainId, address)
    return LiquidityPoolInfo.from_pool(pool) if pool else None


async def query_sugar_get_pools_for_swaps(
    limit: int,
    offset: int,
    chainId: str = "8453",
    use_cache: bool = True,
) -> list:
    """Retrieve all raw liquidity pools suitable for swaps.

    Args:
        limit: The maximum number of pools to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached data. Defaults to True. Not available in stdio mode.

    Returns:
        List[LiquidityPoolForSwapInfo]: A list of simplified pool objects for swaps
    """
    validate_cache_parameter(use_cache, "query_sugar_get_pools_for_swaps")
    pools = _get_cached_pools(chainId) if use_cache else _get_pools_from_chain(chainId)
    
    if not pools:
        return []
    
    pools_for_swap = _convert_pools_to_swap_format(pools)
    paginated_pools = pools_for_swap[offset:offset + limit]
    
    return [LiquidityPoolForSwapInfo.from_pool(p) for p in paginated_pools]


async def query_sugar_get_pools_by_token(
    token_address: str,
    limit: int = 30,
    offset: int = 0,
    chainId: str = "8453",
    use_cache: bool = True,
) -> list | None:
    """Retrieve liquidity pools that contain a specific token.

    Args:
        token_address: The address of the token to filter pools by
        limit: The maximum number of pools to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached data. Defaults to True. Not available in stdio mode.

    Returns:
        list[LiquidityPoolInfo] | None: A list of liquidity pool information or None if not found
    """
    validate_cache_parameter(use_cache, "query_sugar_get_pools_by_token")
    token_address = Web3.to_checksum_address(token_address)
    if not token_address:
        raise ValueError("Token address must be provided.")

    pools = _get_cached_pools(chainId) if use_cache else _get_pools_from_chain(chainId)
    if not pools:
        return None

    pools = _filter_pools_by_token(pools, token_address)
    pools = sorted(pools, key=lambda p: p.tvl, reverse=True)
    pools = pools[offset:offset+limit]
    return [LiquidityPoolInfo.from_pool(p) for p in pools]


async def query_sugar_get_pools_by_pair(
    token0_address: str,
    token1_address: str,
    limit: int = 30,
    offset: int = 0,
    chainId: str = "8453",
    use_cache: bool = True,
) -> list | None:
    """Retrieve liquidity pools that contain a specific token pair.

    Args:
        token0_address: The address of the first token in the pair
        token1_address: The address of the second token in the pair
        limit: The maximum number of pools to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached data. Defaults to True. Not available in stdio mode.

    Returns:
        list[LiquidityPoolInfo] | None: A list of liquidity pool information or None if not found
    """
    validate_cache_parameter(use_cache, "query_sugar_get_pools_by_pair")
    token0_address = Web3.to_checksum_address(token0_address)
    token1_address = Web3.to_checksum_address(token1_address)
    if not token0_address or not token1_address:
        raise ValueError("Both token addresses must be provided.")

    pools = _get_cached_pools(chainId) if use_cache else _get_pools_from_chain(chainId)
    if not pools:
        return None

    pools = _filter_pools_by_pair(pools, token0_address, token1_address)
    pools = sorted(pools, key=lambda p: p.tvl, reverse=True)
    pools = pools[offset:offset+limit]
    return [LiquidityPoolInfo.from_pool(p) for p in pools]


async def query_sugar_get_pool_list(
    token_address_list: list[str] = None,
    pool_type: str = "all",
    sort_by: str = "tvl",
    limit: int = 30,
    offset: int = 0,
    chainId: str = "8453",
    use_cache: bool = True,
) -> list | None:
    """Retrieve liquidity pools based on specified criteria.

    Args:
        token_address_list: List of token addresses to filter pools. Only one or two tokens are supported for filtering. If None, no token filtering is applied
        pool_type: The type of pools to retrieve ('v2', 'v3' or 'all')
        sort_by: The criterion to sort the pools by ('tvl', 'volume', or 'apr')
        limit: The maximum number of pools to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        use_cache: Whether to use cached data. Defaults to True. Not available in stdio mode.

    Returns:
        list[LiquidityPoolInfo] | None: A list of liquidity pool information or None if not found
    """
    validate_cache_parameter(use_cache, "query_sugar_get_pool_list")
    pools = _get_cached_pools(chainId) if use_cache else _get_pools_from_chain(chainId)
    if not pools:
        return None

    if token_address_list is not None:
        if len(token_address_list) == 1:
            token_address = Web3.to_checksum_address(token_address_list[0])
            pools = _filter_pools_by_token(pools, token_address)
        elif len(token_address_list) == 2:
            token0_address = Web3.to_checksum_address(token_address_list[0])
            token1_address = Web3.to_checksum_address(token_address_list[1])
            pools = _filter_pools_by_pair(pools, token0_address, token1_address)
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
    return [LiquidityPoolInfo.from_pool(p) for p in pools]


async def query_sugar_get_latest_pool_epochs(
    offset: int,
    limit: int = 10,
    chainId: str = "8453",
) -> list:
    """Retrieve the latest epoch data for all pools.

    Args:
        limit: The maximum number of epochs to retrieve
        offset: The starting point for pagination
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolEpochInfo]: A list of the most recent epochs across all pools
    """
    with get_chain(chainId) as chain:
        epochs = chain.get_latest_pool_epochs_page(limit, offset)
        return [LiquidityPoolEpochInfo.from_epoch(p) for p in epochs]


async def query_sugar_get_pool_epochs(
    lp: str,
    offset: int = 0,
    limit: int = 10,
    chainId: str = "8453",
) -> list:
    """Retrieve historical epoch data for a given liquidity pool.

    Args:
        lp: Address of the liquidity pool
        offset: Offset for pagination
        limit: Number of epochs to retrieve
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolEpochInfo]: A list of epoch entries for the specified pool
    """
    lp = Web3.to_checksum_address(lp)
    with get_chain(chainId) as chain:
        epochs = chain.get_pool_epochs_page(lp, offset, limit)
        return [LiquidityPoolEpochInfo.from_epoch(p) for p in epochs]

