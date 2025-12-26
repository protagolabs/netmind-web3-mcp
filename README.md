# Netmind Web3 MCP Server

This is an **MCP (Model Context Protocol)** server, that provide some web3 tools.


## Components

### Tools
- **query_token_addressList**: Query address list based on token name or address.
- **query_coingecko_market_data**: Query CoinGecko for cryptocurrency market data with history chart data.

### Environment Variables

All environment variables should be configured in the `.env` file in the project root.

**Required:**
- `BACKEND_URL`: The backend URL for token address queries.
- `COINGECKO_API_KEY`: CoinGecko Pro API Key (format: CG-xxxxx).

**Optional:**
- `MCP_TRANSPORT`: Transport mode - "stdio" or "sse" (default: sse).
- `MCP_HOST`: Server host for SSE transport (default: 127.0.0.1).
- `MCP_PORT`: Server port for SSE transport (default: 8000).

See `env.example` for all available configuration options.

## Usage

### Quick Start

1. **Copy and configure environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and fill in your actual values
   ```

2. **Start the server:**
   ```bash
   python -m netmind_web3_mcp.server
   ```

The server will start in SSE mode by default, listening on `127.0.0.1:8000`.

The server automatically:
- Loads environment variables from `.env` file if it exists
- Checks all required environment variables before starting
- Provides clear error messages if configuration is missing

### Starting the Server

**Basic usage:**

```bash
# Start with SSE transport (default: 127.0.0.1:8000)
python -m netmind_web3_mcp.server

# Start with SSE transport on custom host and port
MCP_HOST=0.0.0.0 MCP_PORT=9000 python -m netmind_web3_mcp.server

# Start with stdio transport
MCP_TRANSPORT=stdio python -m netmind_web3_mcp.server
```

**Alternative: Set environment variables directly**

```bash
export BACKEND_URL="https://your-backend-api.com/tokenAddress/queryTokenAddressList"
export COINGECKO_API_KEY="your_coingecko_api_key_here"
export MCP_TRANSPORT="sse"  # Optional, default is sse
export MCP_HOST="127.0.0.1"  # Optional, only for SSE
export MCP_PORT="8000"  # Optional, only for SSE
python -m netmind_web3_mcp.server
```

### MCP Client Configuration

For stdio transport (local development):

```json
{
  "mcpServers": {
    "netmind-web3-mcp": {
      "env": {
        "BACKEND_URL": "***",
        "COINGECKO_API_KEY": "***",
        "MCP_TRANSPORT": "stdio"
      },
      "command": "uvx",
      "args": [
        "git+https://github.com/protagolabs/netmind-web3-mcp.git"
      ]
    }
  }
}
```

For SSE transport (remote connections), connect to the SSE endpoint:
- Default: `http://127.0.0.1:8000/sse`
- Custom: `http://your-host:your-port/sse`

### Testing

See `test/README.md` for detailed testing instructions. All tests automatically load environment variables from `.env` file.

Quick test commands:
```bash
# Test with stdio transport
python test/test_local_stdio.py

# Test with SSE server (edit SSE_URL in test_sse.py first)
python test/test_sse.py
```

### Building and Publishing to PyPI

To build and publish this package to PyPI:

1. Install build dependencies:
```bash
pip install build twine
```

2. Build the package:
```bash
python -m build
```

3. Upload to PyPI:
```bash
twine upload dist/*
```

Or if using Poetry (as specified in pyproject.toml):
```bash
poetry build
poetry publish
```
