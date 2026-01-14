"""Configuration for backend API data source."""

import os
import sys
from typing import Optional


class BackendConfig:
    """Configuration manager for backend API."""
    
    @classmethod
    def validate_required_env(cls) -> None:
        """Validate that all required environment variables are set."""
        if not os.environ.get("BACKEND_BASE_URL"):
            print("Error: BACKEND_BASE_URL environment variable is not set", file=sys.stderr)
            sys.exit(1)
    
    def __init__(self):
        self.base_url: Optional[str] = os.environ.get("BACKEND_BASE_URL")
        self.timeout: float = float(os.environ.get("BACKEND_TIMEOUT", "10.0"))
        
        if not self.base_url:
            print("Error: BACKEND_BASE_URL environment variable is not set", file=sys.stderr)
            sys.exit(1)
        
        # Ensure base_url doesn't end with a slash
        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")
    
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
