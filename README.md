# Netmind Web3 MCP Server

This is an **MCP (Model Context Protocol)** server that provides Web3 tools.

## Components

### Tools

**Backend Tools:**

- `query_token_addressList` - Query token addresses by name or address (supports multiple values)
- `query_reply_by_news_summary` - Query news by Web3 entity name

**CoinGecko Tools:**

- `query_coingecko_market_data` - Market data with 7-day historical charts
- `query_coingecko_top_token_traders` - Top token traders analysis (requires Analyst plan)
- `query_coingecko_pool_trades` - Past 24h trades by pool address
- `query_coingecko_token_trades` - Past 24h trades by token address (requires paid plan)

**Sugar DeFi Tools:**

- Token queries, price data, pool information, and swap quotes (8 tools)

### Environment Variables

All environment variables should be configured in the `.env` file in the project root.

**Required:**

- `BACKEND_BASE_URL`: The backend base URL (domain only, route path is appended in code).
- `COINGECKO_API_KEY`: CoinGecko Pro API Key (format: CG-xxxxx).
- `SUGAR_PK`: Private key for the Sugar service (required for Sugar tools).
- `SUGAR_RPC_URI_8453`: RPC URI for Base chain (required for Sugar tools).

**Optional:**

- `MCP_TRANSPORT`: Transport mode - "stdio" or "sse" (default: sse).
- `MCP_HOST`: Server host for SSE transport (default: 127.0.0.1).
- `MCP_PORT`: Server port for SSE transport (default: 8000).
- `MCP_AUTH_TOKEN`: Shared bearer token for SSE/Streamable HTTP authentication.

See `env.example` for all available configuration options.

## Quick Start

1. **Setup environment:**

   ```bash
   source .venv/bin/activate
   pip install -e .  # or: uv pip install -e .
   cp env.example .env
   # Edit .env with your API keys
   ```

2. **Start server:**

   ```bash
   python -m netmind_web3_mcp.server
   ```

   Server starts in SSE mode on `http://127.0.0.1:8000` by default.

## Usage

**Basic usage:**

```bash
# Start with SSE transport (default: 127.0.0.1:8000)
python -m netmind_web3_mcp.server

# Start with SSE transport on custom host and port
MCP_HOST=0.0.0.0 MCP_PORT=9000 python -m netmind_web3_mcp.server

# Start with stdio transport
MCP_TRANSPORT=stdio python -m netmind_web3_mcp.server
```

### MCP Client Configuration

For stdio transport (local development):

```json
{
  "mcpServers": {
    "netmind-web3-mcp": {
      "env": {
        "BACKEND_BASE_URL": "***",
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

### Token Authentication (SSE/Streamable HTTP)

If the server sets `MCP_AUTH_TOKEN`, clients must send an Authorization header:

```http
Authorization: Bearer <token>
```

Notes:

- stdio transport does not support HTTP headers, so token auth only applies to SSE/Streamable HTTP.
- For the included `test/test_sse.py`, set `MCP_CLIENT_AUTH_TOKEN` (or reuse `MCP_AUTH_TOKEN`).
- To generate a short random token, run `python test/generate_token.py` and copy the output.

### Debugging with MCP Inspector

Access the built-in Inspector at `http://127.0.0.1:8000/inspector` after starting the server.

**Alternative:** Use `mcp dev test/test_mcp_inspector.py` (automatically starts server in background).

### Testing

```bash
python test/test_local_stdio.py  # stdio transport
python test/test_sse.py         # SSE transport
```

See `test/README.md` for details.
