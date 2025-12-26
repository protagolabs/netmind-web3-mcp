# Test Suite

This directory contains test cases for the Netmind Web3 MCP server, organized by test type.

## Test Organization

- **`test_local_stdio.py`**: Test tools via stdio transport (starts server as subprocess)
  ```bash
  python test/test_local_stdio.py
  ```

- **`test_sse.py`**: Test tools via SSE server (local or remote)
  
  **For local server:**
  1. Edit `test_sse.py` and set `SSE_URL = "http://127.0.0.1:8000/sse"` (default)
  2. Start the server in one terminal:
     ```bash
     python -m netmind_web3_mcp.server
     ```
  3. Run the test in another terminal:
     ```bash
     python test/test_sse.py
     ```
  
  **For remote server:**
  1. Edit `test_sse.py` and set `SSE_URL = "https://your-remote-server.com/sse"`
  2. Run the test:
     ```bash
     python test/test_sse.py
     ```
  
  **Or use environment variable to override:**
  ```bash
  MCP_SSE_URL=https://your-server.com/sse python test/test_sse.py
  ```

## Environment Variables

All tests require the following environment variables to be set:

- `BACKEND_URL`: Backend API URL for token address queries
- `COINGECKO_API_KEY`: CoinGecko Pro API key

**All environment variables should be configured in the `.env` file in the project root.**

1. Copy the example file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and fill in your actual values:
   ```bash
   BACKEND_URL=https://your-backend-api.com/tokenAddress/queryTokenAddressList
   COINGECKO_API_KEY=CG-your-actual-api-key
   ```

3. Tests will automatically load variables from `.env` file.

**Note**: Tests will fail with a clear error message if required variables are missing.

### Proxy Issues

If you encounter proxy errors (e.g., "500 Internal Privoxy Error") when testing locally:

**Solution 1: Set NO_PROXY environment variable**
```bash
NO_PROXY=127.0.0.1,localhost python test/test_sse.py
```

**Solution 2: Temporarily disable proxy**
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
python test/test_sse.py
```

**Note**: The test file automatically adds `127.0.0.1` and `localhost` to `NO_PROXY` for local servers, but you may need to set it explicitly if your system proxy settings override it.

## Running All Tests

### stdio Test
```bash
python test/test_local_stdio.py
```

### SSE Test (Local or Remote)

**For local server:**
1. Edit `test_sse.py` and ensure `SSE_URL = "http://127.0.0.1:8000/sse"` (or your custom port)
2. Start the server:
   ```bash
   python -m netmind_web3_mcp.server
   ```
3. Run the test:
   ```bash
   python test/test_sse.py
   ```

**For remote server:**
1. Edit `test_sse.py` and set `SSE_URL = "https://your-remote-server.com/sse"`
2. Run the test:
   ```bash
   python test/test_sse.py
   ```

**Or override via environment variable:**
```bash
MCP_SSE_URL=https://your-server.com/sse python test/test_sse.py
```

## Test Output

- Test results are printed to console
- Full JSON responses are saved to files: `test_output_*.json`

## Notes

- SSE tests require the server to be running first (for local servers)
- stdio tests automatically start the server as a subprocess
- Edit `SSE_URL` in `test_sse.py` to switch between local and remote servers
- All tests use the same test data and should produce similar results

