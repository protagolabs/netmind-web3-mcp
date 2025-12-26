"""Helper module to load environment variables from .env file."""

import os
import sys
from pathlib import Path
from typing import Optional, List


def load_env_file(env_file_path: Optional[Path] = None, project_root: Optional[Path] = None) -> None:
    """Load environment variables from .env file if it exists.
    
    Args:
        env_file_path: Path to .env file. If None, looks for .env in project root.
        project_root: Project root directory. If None, tries to detect automatically.
                     Used when env_file_path is None.
    
    The function will:
    - Skip empty lines and comments (lines starting with #)
    - Parse key=value pairs
    - Remove quotes from values if present
    - Only set variables that are not already in the environment (won't override existing values)
    """
    if env_file_path is None:
        if project_root is None:
            # Try to detect project root
            # If called from within the package, go up to project root
            current_file = Path(__file__)
            # Go from utils/env_loader.py -> netmind_web3_mcp/ -> src/ -> project_root
            project_root = current_file.parent.parent.parent.parent
        
        env_file_path = project_root / ".env"
    
    if env_file_path.exists():
        with open(env_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                
                # Parse key=value pairs
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Only set if not already in environment (won't override existing values)
                    if key and key not in os.environ:
                        os.environ[key] = value


def ensure_test_env(required_vars: Optional[List[str]] = None, project_root: Optional[Path] = None) -> None:
    """Ensure required environment variables are set for testing.
    
    Loads from .env file and checks if required variables are present.
    Raises an error if required variables are missing.
    
    Args:
        required_vars: List of required environment variable names.
                      Defaults to ["BACKEND_URL", "COINGECKO_API_KEY"]
        project_root: Project root directory for .env file location.
    """
    load_env_file(project_root=project_root)
    
    if required_vars is None:
        required_vars = ["BACKEND_URL", "COINGECKO_API_KEY"]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set them in .env file or as environment variables.\n"
            f"See env.example for reference."
        )

