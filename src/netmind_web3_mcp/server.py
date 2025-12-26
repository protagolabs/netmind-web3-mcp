"""Main MCP server for Netmind Web3 tools."""

import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from .tools import query_token_addressList, query_coingecko_market_data
from .tools.backend.config import BackendConfig
from .tools.coingecko.config import CoinGeckoConfig
from .utils.env_loader import load_env_file


def _create_mcp_instance():
    """Create FastMCP instance with configuration from environment variables.
    
    Note: host and port are only used for SSE transport mode.
    For stdio transport, these parameters are ignored.
    """
    # Only read host/port if SSE transport is used (or default values for stdio)
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_PORT", "8000"))
    
    mcp = FastMCP("netmind-web3-mcp", host=host, port=port)
    mcp.tool()(query_token_addressList)
    mcp.tool()(query_coingecko_market_data)
    return mcp


def _check_required_env_vars():
    """Check if all required environment variables are set.
    
    This function is called by the startup script and server main function.
    Add new module checks here when adding new data sources.
    """
    BackendConfig.check_env()
    CoinGeckoConfig.check_env()


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
    
    _check_required_env_vars()
    
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
