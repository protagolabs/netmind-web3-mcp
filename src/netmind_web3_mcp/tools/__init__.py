"""Tools package for netmind-web3-mcp."""

from .backend import query_token_addressList
from .coingecko import query_coingecko_market_data
from .sugar import (
    query_sugar_get_all_tokens,
    query_sugar_get_token_prices,
    query_sugar_get_prices,
    query_sugar_get_pools,
    query_sugar_get_pool_by_address,
    query_sugar_get_pools_for_swaps,
    query_sugar_get_pools_by_token,
    query_sugar_get_pools_by_pair,
    query_sugar_get_pool_list,
    query_sugar_get_latest_pool_epochs,
    query_sugar_get_pool_epochs,
    query_sugar_get_quote,
)

__all__ = [
    "query_token_addressList",
    "query_coingecko_market_data",
    "query_sugar_get_all_tokens",
    "query_sugar_get_token_prices",
    "query_sugar_get_prices",
    "query_sugar_get_pools",
    "query_sugar_get_pool_by_address",
    "query_sugar_get_pools_for_swaps",
    "query_sugar_get_pools_by_token",
    "query_sugar_get_pools_by_pair",
    "query_sugar_get_pool_list",
    "query_sugar_get_latest_pool_epochs",
    "query_sugar_get_pool_epochs",
    "query_sugar_get_quote",
]
