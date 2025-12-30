# Netmind Web3 MCP Server

This is an **MCP (Model Context Protocol)** server, that provide some web3 tools.


## Components

### Tools
- **query_token_addressList**: Query address list based on token name or address.
- **query_coingecko_market_data**: Query CoinGecko for cryptocurrency market data with history chart data.
- **Sugar MCP tools**: DeFi data query tools including tokens, pools, and quotes (12 tools).

### Environment Variables

All environment variables should be configured in the `.env` file in the project root.

**Required:**
- `BACKEND_URL`: The backend URL for token address queries.
- `COINGECKO_API_KEY`: CoinGecko Pro API Key (format: CG-xxxxx).
- `SUGAR_PK`: Private key for the Sugar service (required for Sugar tools).
- `SUGAR_RPC_URI_8453`: RPC URI for Base chain (required for Sugar tools).

**Optional:**
- `MCP_TRANSPORT`: Transport mode - "stdio" or "sse" (default: sse).
- `MCP_HOST`: Server host for SSE transport (default: 127.0.0.1).
- `MCP_PORT`: Server port for SSE transport (default: 8000).

See `env.example` for all available configuration options.

## Usage

### Quick Start

1. **Activate the virtual environment:**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Verify you're using the virtual environment Python
   which python  # Should show: .../netmind-web3-mcp/.venv/bin/python
   python --version  # Should match your virtual environment Python version
   ```

2. **Install the package in development mode:**
   
   **If using pip:**
   ```bash
   # Install pip in virtual environment if not available
   python -m ensurepip --upgrade
   
   # This installs the package and all dependencies
   pip install -e .
   ```
   
   **If using uv (recommended for uv-managed environments):**
   ```bash
   # Install package in editable mode with uv
   uv pip install -e .
   ```
   
   **Important:** 
   - You must activate the virtual environment first
   - You must install the package before running the server
   - This makes the `netmind_web3_mcp` module available to Python and installs all dependencies
   - If you get `ModuleNotFoundError`, verify installation: `python -c "import netmind_web3_mcp; print('OK')"`

3. **Copy and configure environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and fill in your actual values
   ```

4. **Start the server:**
   ```bash
   python -m netmind_web3_mcp.server
   ```

The server will start in SSE mode by default, listening on `127.0.0.1:8000`.

The server automatically:
- Loads environment variables from `.env` file if it exists
- Checks all required environment variables before starting
- Provides clear error messages if configuration is missing

### Starting the Server

**⚠️ Important:** Make sure you've activated the virtual environment before starting the server:
```bash
source .venv/bin/activate
```

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

### Debugging with MCP Inspector

MCP Inspector is a web-based debugging tool that allows you to interactively test and debug your MCP server.

**Method 1: Using Built-in Inspector (Simplest)**

The easiest way is to use the built-in Inspector that comes with the server:

1. **Start the server:**
   ```bash
   source .venv/bin/activate
   python -m netmind_web3_mcp.server
   ```

2. **Open Inspector in browser:**
   - Navigate to: `http://127.0.0.1:8000/inspector`
   - The Inspector UI will be available automatically

**Method 2: Using `mcp dev` command**

If you prefer to use the `mcp dev` command:

1. **Start the server in one terminal:**
   ```bash
   source .venv/bin/activate
   python -m netmind_web3_mcp.server
   ```
   The server will start on `http://127.0.0.1:8000` by default.

2. **Start Inspector in another terminal:**
   ```bash
   source .venv/bin/activate
   mcp dev test/test_mcp_inspector.py
   ```
   The script will automatically start the server in the background.

3. **Connect to server in Inspector UI:**
   - When Inspector opens, it should automatically connect to `http://127.0.0.1:8000/sse`
   - Or manually enter the SSE URL if needed

**Note:** The `test/test_mcp_inspector.py` script automatically starts the server in the background, so you don't need to start it separately.

**Alternative: Using package installation**

If you prefer to install the package first:

```bash
# Install package in editable mode
pip install -e .

# Then use mcp dev with the server file directly
mcp dev --with-editable . src/netmind_web3_mcp/server.py
```

**Note:** The `test/test_mcp_inspector.py` wrapper script handles path setup, environment loading, and automatically starts the server in the background, so you don't need to modify `server.py` or start the server separately.

**Method 2: Manual server + Inspector connection**

1. **Start the server in SSE mode** (in terminal 1):
   ```bash
   python -m netmind_web3_mcp.server
   ```
   The server will start on `http://127.0.0.1:8000` by default.

2. **Access Inspector in browser:**
   - Open your browser and navigate to: `http://127.0.0.1:8000/inspector`
   - Or check the server logs for the exact Inspector URL

**Troubleshooting:**

- If `mcp` command is not found or has path issues:
  ```bash
  # Reinstall MCP CLI
  pip install --force-reinstall "mcp[cli]"
  
  # Or use Python module directly
  python -m mcp.cli dev python -m netmind_web3_mcp.server
  ```

- If connection fails:
  - Verify the server is running: `curl http://127.0.0.1:8000/sse`
  - Check firewall settings
  - Ensure `MCP_TRANSPORT=sse` is set (or use default)

- For custom ports:
  ```bash
  # Start server on custom port
  MCP_PORT=9000 python -m netmind_web3_mcp.server
  # Then access: http://127.0.0.1:9000/inspector
  ```

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
