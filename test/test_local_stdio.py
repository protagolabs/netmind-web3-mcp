"""Local test using stdio transport mode.

This test starts the server as a subprocess and communicates via stdio.
Useful for testing the server in stdio mode locally.
"""

import json
import traceback
import os
import sys
from pathlib import Path
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
import asyncio

# Get the project root and src path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Load environment variables from .env file
from netmind_web3_mcp.utils.env_loader import ensure_test_env

try:
    ensure_test_env(project_root=project_root)
except ValueError as e:
    print(f"❌ {e}")
    sys.exit(1)

# Set up environment for subprocess
env = os.environ.copy()
env.update({
    "MCP_TRANSPORT": "stdio",  # Explicitly set stdio mode
    "PYTHONPATH": str(src_path),
})

# Use -m flag to run as module, which allows relative imports to work
server = StdioServerParameters(
    command=sys.executable,
    args=["-m", "netmind_web3_mcp.server"],
    env=env
)


async def main():
    """Test tools via stdio transport."""
    print("=" * 60)
    print("Local Test: stdio Transport Mode")
    print("=" * 60)
    
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected to server via stdio")
            
            # List available tools
            response = await session.list_tools()
            tools = [dict(t) for t in response.tools]
            print(f"\n📋 Available tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')[:60]}...")
            
            # Test cases
            test_cases = [
                {
                    "name": "query_coingecko_market_data (single coin)",
                    "tool": "query_coingecko_market_data",
                    "args": {
                        "ids": "bitcoin",
                        "vs_currency": "usd",
                        "price_change_percentage": "1h"
                    }
                },
                {
                    "name": "query_coingecko_market_data (multiple coins)",
                    "tool": "query_coingecko_market_data",
                    "args": {
                        "ids": "bitcoin,ethereum,solana",
                        "vs_currency": "usd",
                        "price_change_percentage": "1h,24h,7d"
                    }
                },
                # Uncomment to test token address query
                # {
                #     "name": "query_token_addressList",
                #     "tool": "query_token_addressList",
                #     "args": {
                #         "tokenName": "USDT"
                #     }
                # },
            ]
            
            for test_case in test_cases:
                print(f"\n{'=' * 60}")
                print(f"🛠️  Testing: {test_case['name']}")
                print(f"{'=' * 60}")
                try:
                    response = await session.call_tool(
                        test_case["tool"],
                        arguments=test_case["args"]
                    )
                    
                    print("✅ Tool call succeeded!")
                    result_text = response.content[0].text
                    
                    # Try to parse and show summary
                    try:
                        result_json = json.loads(result_text)
                        if isinstance(result_json, list):
                            print(f"📊 Result: {len(result_json)} items")
                            if len(result_json) > 0:
                                print(f"📄 First item preview:")
                                print(json.dumps(result_json[0], indent=2, ensure_ascii=False)[:500])
                        elif isinstance(result_json, dict):
                            print(f"📊 Result keys: {list(result_json.keys())[:10]}")
                            print(f"📄 Preview:")
                            print(json.dumps(result_json, indent=2, ensure_ascii=False)[:500])
                        else:
                            print(f"📄 Result: {result_text[:500]}...")
                    except json.JSONDecodeError:
                        print(f"📄 Result (text): {result_text[:500]}...")
                    
                except Exception as e:
                    print(f"❌ Tool call failed: {e}")
                    print(f"Detailed error: {traceback.format_exc()}")
                    continue
            
            print(f"\n{'=' * 60}")
            print("✅ All tests completed!")
            print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
