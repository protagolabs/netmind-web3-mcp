# Netmind Web3 MCP Server

This is an **MCP (Model Context Protocol)** server, that provide some web3 tools.


## Components

### Environment Variables
- `BACKEND_URL`: The Backend URL.


### Tools
- query_token_addressList: Query address list based on token name or address.
  
 
### Usage
```json
{
  "mcpServers": {
    "netmind-web3-mcp": {
      "env": {
        "BACKEND_URL": "",
      },
      "command": "uvx",
      "args": [
        "netmind-web3-mcp"
      ]
    }
  }
}
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