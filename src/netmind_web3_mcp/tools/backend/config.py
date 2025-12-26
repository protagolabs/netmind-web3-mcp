"""Configuration for backend API data source."""

import os
import sys
from typing import Optional


class BackendConfig:
    """Configuration manager for backend API."""
    
    @classmethod
    def check_env(cls) -> None:
        """Check if required environment variables are set."""
        if not os.environ.get("BACKEND_URL"):
            print("Error: BACKEND_URL environment variable is not set", file=sys.stderr)
            sys.exit(1)
    
    def __init__(self):
        self.base_url: Optional[str] = os.environ.get("BACKEND_URL")
        self.timeout: float = float(os.environ.get("BACKEND_TIMEOUT", "10.0"))
        
        if not self.base_url:
            print("Error: BACKEND_URL environment variable is not set", file=sys.stderr)
            sys.exit(1)
    
    def get_base_url(self) -> str:
        return self.base_url
    
    def get_timeout(self) -> float:
        return self.timeout


_config: Optional[BackendConfig] = None


def get_config() -> BackendConfig:
    global _config
    if _config is None:
        _config = BackendConfig()
    return _config
