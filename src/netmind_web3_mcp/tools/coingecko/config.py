"""Configuration for CoinGecko API data source."""

import os
import sys
import asyncio
from typing import Optional


class CoinGeckoConfig:
    """Configuration manager for CoinGecko API."""
    
    @classmethod
    def validate_required_env(cls) -> None:
        """Validate that all required environment variables are set."""
        if not os.environ.get("COINGECKO_API_KEY"):
            print("Error: COINGECKO_API_KEY environment variable is not set", file=sys.stderr)
            sys.exit(1)
    
    def __init__(self):
        self.api_key: Optional[str] = os.environ.get("COINGECKO_API_KEY")
        self.base_url: str = os.environ.get("COINGECKO_BASE_URL", "https://pro-api.coingecko.com/api/v3")
        self.timeout: float = float(os.environ.get("COINGECKO_TIMEOUT", "10.0"))
        self.max_concurrent: int = int(os.environ.get("COINGECKO_MAX_CONCURRENT", "10"))
        self._semaphore: Optional[asyncio.Semaphore] = None
        
        if not self.api_key:
            print("Error: COINGECKO_API_KEY environment variable is not set", file=sys.stderr)
            sys.exit(1)
    
    def get_api_key(self) -> str:
        return self.api_key
    
    def get_headers(self) -> dict:
        return {"x-cg-pro-api-key": self.api_key}
    
    def get_base_url(self) -> str:
        return self.base_url
    
    def get_timeout(self) -> float:
        return self.timeout
    
    def get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore


_config: Optional[CoinGeckoConfig] = None


def get_config() -> CoinGeckoConfig:
    global _config
    if _config is None:
        _config = CoinGeckoConfig()
    return _config
