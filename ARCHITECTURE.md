# Architecture Documentation

## Directory Structure

```
src/netmind_web3_mcp/
├── __init__.py              # Package initialization
├── server.py                # Main server file (registers tools and starts service)
└── tools/                   # Tools module directory
    ├── __init__.py          # Tools package exports
    ├── backend/             # Backend API data source
    │   ├── __init__.py
    │   ├── config.py        # Configuration management
    │   ├── token_address.py # Token address query tool
    │   └── news.py          # News query tool
    ├── coingecko/           # CoinGecko API data source
    │   ├── __init__.py
    │   ├── config.py        # Configuration & concurrency control
    │   └── market_data.py   # Market data, traders, trades tools
    └── sugar/               # Sugar DeFi data source
        ├── __init__.py
        ├── config.py
        ├── cache.py         # Cache system
        ├── tokens.py        # Token queries
        ├── pools.py         # Pool queries
        └── quotes.py        # Swap quotes
```

## Design Principles

### 1. Data Source Isolation
Each data source has its own independent package, containing:
- **Configuration module** (`config.py`): Responsible for environment variable reading, configuration validation, and resource initialization
- **Tool module**: Implements specific business logic

### 2. Configuration Management
Each data source's `config.py` provides:
- **Environment variable reading**: Load configuration from environment variables
- **Configuration validation**: Ensure required configuration exists
- **Resource initialization**: Such as semaphores, connection pools, etc.
- **Singleton pattern**: Use global configuration instance to avoid duplicate initialization

### 3. Extensibility
To add a new data source, simply:
1. Create a new package under `tools/` (e.g., `tools/new_source/`)
2. Create `config.py` to manage configuration
3. Create tool file to implement functionality
4. Export in `tools/__init__.py`
5. Register in `server.py`

## Configuration Details

### Backend Configuration (`tools/backend/config.py`)

**Environment Variables**:
- `BACKEND_BASE_URL` (required): Backend API base URL
- `BACKEND_TIMEOUT` (optional): Request timeout, default 10.0 seconds

**Features**:
- Validates backend URL configuration
- Manages request timeout settings

### CoinGecko Configuration (`tools/coingecko/config.py`)

**Environment Variables**:
- `COINGECKO_API_KEY` (required): CoinGecko Pro API key
- `COINGECKO_TIMEOUT` (optional): Request timeout, default 10.0 seconds
- `COINGECKO_MAX_CONCURRENT` (optional): Maximum concurrent requests, default 10
- `COINGECKO_BASE_URL` (optional): Custom API base URL

**Features**:
- Validates API key configuration
- Manages concurrency control (semaphore)
- Generates authentication headers
- Manages API base URL

## Usage Examples

### Adding a New Data Source

1. **Create package structure**:
```bash
mkdir -p src/netmind_web3_mcp/tools/new_source
```

2. **Create configuration file** (`tools/new_source/config.py`):
```python
import os
import sys
from typing import Optional

class NewSourceConfig:
    @classmethod
    def validate_required_env(cls) -> None:
        """Validate that all required environment variables are set."""
        if not os.environ.get("NEW_SOURCE_API_KEY"):
            print("Error: NEW_SOURCE_API_KEY environment variable is not set", file=sys.stderr)
            sys.exit(1)
    
    def __init__(self):
        self.api_key = os.environ.get("NEW_SOURCE_API_KEY")
        # ... other configuration
    
    def validate(self) -> bool:
        return self.api_key is not None

_config: Optional[NewSourceConfig] = None

def get_config() -> NewSourceConfig:
    global _config
    if _config is None:
        _config = NewSourceConfig()
    return _config
```

3. **Create tool file** (`tools/new_source/tool.py`):
```python
from .config import get_config

async def query_new_source_data():
    config = get_config()
    # Use configuration to implement functionality
    pass
```

4. **Update exports** (`tools/new_source/__init__.py`):
```python
from .config import NewSourceConfig
from .tool import query_new_source_data

__all__ = ["NewSourceConfig", "query_new_source_data"]
```

5. **Register tool** (`server.py`):
```python
from .tools.new_source import query_new_source_data
from .tools.new_source.config import NewSourceConfig

# Add to _validate_required_env_vars()
NewSourceConfig.validate_required_env()

# Register tool
mcp.tool()(query_new_source_data)
```

## Advantages

1. **Modularity**: Each data source is independent and does not interfere with others
2. **Configurable**: Flexible configuration through environment variables
3. **Extensible**: Simple and clear to add new data sources
4. **Maintainable**: Clear code structure, easy to maintain
5. **Resource Management**: Each data source independently manages its own resources (such as semaphores)
