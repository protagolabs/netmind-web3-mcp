"""Main MCP server for Netmind Web3 tools."""

import os
from pathlib import Path
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from .tools import (
    query_token_addressList,
    query_reply_by_news_summary,
    query_coingecko_market_data,
    query_coingecko_top_token_traders,
    query_coingecko_pool_trades,
    query_coingecko_token_trades,
    query_sugar_get_all_tokens,
    query_sugar_get_token_prices,
    query_sugar_get_prices,
    query_sugar_get_pools_for_swaps,
    query_sugar_get_pool_list,
    query_sugar_get_latest_pool_epochs,
    query_sugar_get_pool_epochs,
    query_sugar_get_quote,
)
from .tools.backend.config import BackendConfig
from .tools.coingecko.config import CoinGeckoConfig
from .tools.sugar.config import SugarConfig
from .tools.sugar.cache import ensure_cache_system_started
from .utils.auth import StaticTokenVerifier
from .utils.env_loader import load_env_file


def _build_auth_settings(host: str, port: int):
    token = os.environ.get("MCP_AUTH_TOKEN", "").strip()
    if not token:
        return None, None

    base_url = f"http://{host}:{port}"
    auth_settings = AuthSettings(
        issuer_url=base_url,
        resource_server_url=base_url,
    )
    token_verifier = StaticTokenVerifier(token=token)
    return auth_settings, token_verifier


def _create_mcp_instance():
    """Create FastMCP instance with configuration from environment variables.
    
    Note: host and port are only used for SSE transport mode.
    For stdio transport, these parameters are ignored.
    """
    # Only read host/port if SSE transport is used (or default values for stdio)
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_PORT", "8000"))
    
    auth_settings, token_verifier = _build_auth_settings(host, port)
    mcp = FastMCP(
        "netmind-web3-mcp",
        host=host,
        port=port,
        auth=auth_settings,
        token_verifier=token_verifier,
    )
    
    # Register backend tools
    mcp.tool()(query_token_addressList)
    mcp.tool()(query_reply_by_news_summary)
    
    # Register CoinGecko tools
    mcp.tool()(query_coingecko_market_data)
    mcp.tool()(query_coingecko_top_token_traders)
    mcp.tool()(query_coingecko_pool_trades)
    mcp.tool()(query_coingecko_token_trades)
    
    # Register Sugar MCP tools
    mcp.tool()(query_sugar_get_all_tokens)
    mcp.tool()(query_sugar_get_token_prices)
    mcp.tool()(query_sugar_get_prices)
    mcp.tool()(query_sugar_get_pools_for_swaps)
    mcp.tool()(query_sugar_get_pool_list)
    mcp.tool()(query_sugar_get_latest_pool_epochs)
    mcp.tool()(query_sugar_get_pool_epochs)
    mcp.tool()(query_sugar_get_quote)
    
    return mcp


def _validate_required_env_vars():
    """Validate that all required environment variables are set.
    
    This function is called by the startup script and server main function.
    Add new module checks here when adding new data sources.
    """
    BackendConfig.validate_required_env()
    CoinGeckoConfig.validate_required_env()
    SugarConfig.validate_required_env()


# Module-level instance (for testing and import access)
# Created when module is imported, using current environment variables
mcp = _create_mcp_instance()


def main():
    """Start the MCP server.
    
    Automatically loads environment variables from .env file if it exists.
    Uses the module-level mcp instance, which is created with current environment variables.
    """
    # Load environment variables from .env file
    # Detect project root: server.py -> netmind_web3_mcp/ -> src/ -> project_root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    load_env_file(project_root=project_root)

    # Recreate MCP instance after loading env so auth settings are applied
    mcp_instance = _create_mcp_instance()

    _validate_required_env_vars()
    
    # Eagerly initialize Sugar cache system on server startup
    ensure_cache_system_started()
    
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    mcp_instance.run(transport=transport)


if __name__ == "__main__":
    main()
