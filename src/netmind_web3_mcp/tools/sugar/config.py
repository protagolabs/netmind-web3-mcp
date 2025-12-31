"""Configuration for Sugar MCP data source."""

import os
import sys
from typing import Optional, List
from .cache import CacheConfig


def is_stdio_mode() -> bool:
    """Check if the server is running in stdio transport mode."""
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    return transport.lower() == "stdio"


class SugarConfig:
    """Configuration manager for Sugar MCP."""
    
    @classmethod
    def validate_required_env(cls) -> None:
        """Validate that all required environment variables are set."""
        if not os.environ.get("SUGAR_PK"):
            print("Error: SUGAR_PK environment variable is not set", file=sys.stderr)
            sys.exit(1)
        
        if not os.environ.get("SUGAR_RPC_URI_8453"):
            print("Error: SUGAR_RPC_URI_8453 environment variable is not set", file=sys.stderr)
            sys.exit(1)
    
    def __init__(self):
        # Required environment variables (already validated by validate_required_env, but keep for safety)
        self.private_key: Optional[str] = os.environ.get("SUGAR_PK")
        self.rpc_uri_8453: Optional[str] = os.environ.get("SUGAR_RPC_URI_8453")
        
        # Cache configuration
        self.skip_cache_init: bool = os.environ.get("SKIP_CACHE_INIT", "false").lower() == "true"
        self.cache_duration_minutes: int = int(os.environ.get("SUGAR_CACHE_DURATION_MINUTES", "30"))
        
        cache_chains_str = os.environ.get("SUGAR_CACHE_ENABLED_CHAINS")
        if cache_chains_str:
            self.cache_enabled_chains: Optional[List[str]] = [chain.strip() for chain in cache_chains_str.split(",")]
        else:
            # Default to Base chain only
            self.cache_enabled_chains: Optional[List[str]] = ["8453"]
        
        self.cache_filter_invalid_pools: bool = os.environ.get("SUGAR_CACHE_FILTER_INVALID_POOLS", "true").lower() == "true"
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        return CacheConfig(
            duration_minutes=self.cache_duration_minutes,
            enabled_chain_ids=self.cache_enabled_chains,
            filter_invalid_pools=self.cache_filter_invalid_pools
        )


def validate_cache_parameter(use_cache: bool, tool_name: str) -> None:
    """Validate that cache parameter is compatible with current transport mode.
    
    Args:
        use_cache: Whether cache is requested
        tool_name: Name of the tool for error message
    
    Raises:
        ValueError: If use_cache=True but cache is not available (e.g., in stdio mode)
    """
    if use_cache and is_stdio_mode():
        raise ValueError(
            f"Cache is not available in stdio transport mode. "
            f"Please set use_cache=False for {tool_name}, or use SSE transport mode to enable cache."
        )


_config: Optional[SugarConfig] = None


def get_config() -> SugarConfig:
    global _config
    if _config is None:
        _config = SugarConfig()
    return _config

