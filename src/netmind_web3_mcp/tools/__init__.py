"""Tools package for netmind-web3-mcp."""

from .backend import (
    query_token_addressList,
    query_reply_by_news_summary,
)

from .coingecko import (
    query_coingecko_market_data,
    query_coingecko_top_token_traders,
    query_coingecko_pool_trades,
    query_coingecko_token_trades,
)
from .sugar import (
    query_sugar_get_all_tokens,
    query_sugar_get_token_prices,
    query_sugar_get_prices,
    query_sugar_get_pools_for_swaps,
    query_sugar_get_pool_list,
    query_sugar_get_latest_pool_epochs,
    query_sugar_get_pool_epochs,
    query_sugar_get_quote,
)

__all__ = [
    "query_token_addressList",
    "query_reply_by_news_summary",  
    "query_coingecko_market_data",
    "query_coingecko_top_token_traders",
    "query_coingecko_pool_trades",
    "query_coingecko_token_trades",
    "query_sugar_get_all_tokens",
    "query_sugar_get_token_prices",
    "query_sugar_get_prices",  
    "query_sugar_get_pools_for_swaps",
    "query_sugar_get_pool_list",
    "query_sugar_get_latest_pool_epochs",
    "query_sugar_get_pool_epochs",
    "query_sugar_get_quote",
]
