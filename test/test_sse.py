"""SSE transport mode test.

This test connects to an SSE server (local or remote).
Edit the SSE_URL variable below to point to your server.
"""

import json
import traceback
import os
import sys
import asyncio
from pathlib import Path
from mcp.client.sse import sse_client
from mcp import ClientSession
import httpx

# Add src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Load environment variables from .env file
from netmind_web3_mcp.utils.env_loader import load_env_file
load_env_file(project_root=project_root)

# ============================================================================
# Configuration: Edit this URL to point to your SSE server
# ============================================================================
# Default: Local server
SSE_URL = "http://127.0.0.1:8000/sse"

# Uncomment and set for remote server:
# SSE_URL = "https://your-remote-server.com/sse"

# Or use environment variable to override:
SSE_URL = os.environ.get("MCP_SSE_URL", SSE_URL)
# ============================================================================


async def check_server_connection(url: str) -> bool:
    """Check if the server is reachable before attempting SSE connection."""
    try:
        # Try a simple HTTP GET to check if server is running
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Try to connect to the base URL (without /sse)
            base_url = url.rsplit("/sse", 1)[0]
            response = await client.get(base_url, follow_redirects=True)
            return response.status_code < 500
    except Exception:
        return False


def is_local_url(url: str) -> bool:
    """Check if URL is a local server."""
    return "127.0.0.1" in url or "localhost" in url or url.startswith("http://127.0.0.1") or url.startswith("http://localhost")


async def main():
    """Test tools via SSE server."""
    print("=" * 60)
    print("SSE Transport Mode Test")
    print("=" * 60)
    print(f"🔗 Connecting to: {SSE_URL}")
    print("=" * 60)
    
    # Setup proxy bypass for localhost if needed
    if is_local_url(SSE_URL):
        no_proxy = os.environ.get("NO_PROXY", "")
        if "127.0.0.1" not in no_proxy and "localhost" not in no_proxy:
            no_proxy_list = [x.strip() for x in no_proxy.split(",") if x.strip()]
            no_proxy_list.extend(["127.0.0.1", "localhost", "::1"])
            os.environ["NO_PROXY"] = ",".join(no_proxy_list)
            os.environ["no_proxy"] = os.environ["NO_PROXY"]
    
    # Check if server is reachable first (only for local servers)
    if is_local_url(SSE_URL):
        print("\n🔍 Checking server connection...")
        server_reachable = await check_server_connection(SSE_URL)
        if not server_reachable:
            print("❌ Server is not reachable!")
            print(f"\n💡 Make sure the server is running:")
            print(f"   python -m netmind_web3_mcp.server")
            print(f"\nOr check if the server is running on a different port:")
            print(f"   MCP_PORT=9000 python -m netmind_web3_mcp.server")
            print(f"\nThen edit SSE_URL in this file to match:")
            print(f"   SSE_URL = \"http://127.0.0.1:9000/sse\"")
            return
        
        print("✅ Server is reachable, attempting SSE connection...")
        print("=" * 60)
    
    try:
        async with sse_client(SSE_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                server_type = "local" if is_local_url(SSE_URL) else "remote"
                print(f"✅ Connected to {server_type} SSE server")
                
                # List available tools
                response = await session.list_tools()
                tools = [dict(t) for t in response.tools]
                print(f"\n📋 Available tools: {len(tools)}")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool.get('description', 'No description')[:60]}...")
                
                # Test cases
                test_cases = [
                    # {
                    #     "name": "query_token_addressList",
                    #     "tool": "query_token_addressList",
                    #     "args": {
                    #         "token_symbol": "USDT"
                    #     }
                    # },
                    {   
                        "name": "query_reply_by_news_summary",
                        "tool": "query_reply_by_news_summary",
                        "args": {
                            "content": "Mask"
                        }
                    },
                    # {
                    #     "name": "query_coingecko_market_data (single coin)",
                    #     "tool": "query_coingecko_market_data",
                    #     "args": {
                    #         "ids": "bitcoin",
                    #         "vs_currency": "usd",
                    #         "price_change_percentage": "1h"
                    #     }
                    # },
                    # {
                    #     "name": "query_coingecko_market_data (multiple coins)",
                    #     "tool": "query_coingecko_market_data",
                    #     "args": {
                    #         "ids": "bitcoin,ethereum,solana,cardano,polkadot",
                    #         "vs_currency": "usd",
                    #         "price_change_percentage": "1h,24h,7d"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_quote",
                    #     "tool": "query_sugar_get_quote",
                    #     "args": {
                    #         "from_token": "usdc",
                    #         "to_token": "aero",
                    #         "amount": 1000000000000000,
                    #         "chainId": "8453",
                    #         "use_cache": True
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_token_list",
                    #     "tool": "query_sugar_get_all_tokens",
                    #     "args": {
                    #         "limit": 10,
                    #         "offset": 0,
                    #         "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_token_prices",
                    #     "tool": "query_sugar_get_token_prices",
                    #     "args": {
                    #         "token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    #         "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_prices",
                    #     "tool": "query_sugar_get_prices",
                    #     "args": {
                    #         "limit": 10,
                    #         "offset": 0,
                    #         "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_latest_pool_epochs",
                    #     "tool": "query_sugar_get_latest_pool_epochs",
                    #     "args": {
                    #         "offset": 0,
                    #         "limit": 10,
                    #         "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_pool_epochs",
                    #     "tool": "query_sugar_get_pool_epochs",
                    #     "args": {
                    #         "lp": "0x2722C8f9B5E2aC72D1f225f8e8c990E449ba0078",
                    #         "offset": 0,
                    #         "limit": 10,    
                    #         "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_pools",
                    #     "tool": "query_sugar_get_pools",
                    #     "args": {
                    #          "limit": 10,   
                    #          "offset": 0,
                    #          "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_pool_by_address",
                    #     "tool": "query_sugar_get_pool_by_address",
                    #     "args": {
                    #         "address": "0x2722C8f9B5E2aC72D1f225f8e8c990E449ba0078",
                    #         "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_pools_for_swaps",
                    #     "tool": "query_sugar_get_pools_for_swaps",
                    #     "args": {
                    #         "limit": 10,
                    #         "offset": 0,
                    #         "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_pools_by_token",
                    #     "tool": "query_sugar_get_pools_by_token",
                    #     "args": {
                    #         "token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    #         "chainId": "8453"
                    #     }
                    # },
                    # {
                    #     "name": "query_sugar_get_pools_by_pair",
                    #     "tool": "query_sugar_get_pools_by_pair",
                    #     "args": {
                    #         "token0_address": "0x4200000000000000000000000000000000000006",
                    #         "token1_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    #         "chainId": "8453"
                    #     }
                    # },  
                    # {
                    #     "name": "query_sugar_get_pool_list",
                    #     "tool": "query_sugar_get_pool_list",
                    #     "args": {
                    #         "chainId": "8453"
                    #     }
                    # }
                ]
                
                for test_case in test_cases:
                    try:
                        # Call tool; newer mcp clients may return a structured CallToolResult
                        result = await session.call_tool(test_case["tool"], arguments=test_case["args"])

                        # Normalize result into a JSON-serializable Python object
                        result_obj = None
                        try:
                            if isinstance(result, (dict, list, str, int, float, bool)) or result is None:
                                result_obj = result
                            elif hasattr(result, "model_dump_json"):
                                # Pydantic v2 style
                                result_obj = json.loads(result.model_dump_json())
                            elif hasattr(result, "model_dump"):
                                # Pydantic v2 dict
                                result_obj = result.model_dump()
                            elif hasattr(result, "json"):
                                # Pydantic v1 style
                                result_obj = json.loads(result.json())
                            else:
                                # Fallback: best-effort serialization
                                result_obj = json.loads(json.dumps(result, default=lambda o: getattr(o, "__dict__", str(o))))
                        except Exception:
                            # As a last resort, store string representation
                            result_obj = str(result)
                        
                        # Save full result to file to avoid truncation
                        output_file = f"test_output_{test_case['tool']}.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            if isinstance(result_obj, (dict, list)):
                                json.dump(result_obj, f, indent=2, ensure_ascii=False)
                            else:
                                f.write(str(result_obj))
                        
                        print(f"📄 Full result saved to: {output_file}")
                        
                        # Show summary
                        if isinstance(result_obj, list):
                            print(f"📊 Result: {len(result_obj)} items")
                            if len(result_obj) > 0:
                                print(f"📄 First item preview:")
                                print(json.dumps(result_obj[0], indent=2, ensure_ascii=False)[:500])
                        elif isinstance(result_obj, dict):
                            print(f"📊 Result keys: {list(result_obj.keys())[:10]}")
                            print(f"📄 Preview:")
                            print(json.dumps(result_obj, indent=2, ensure_ascii=False)[:500])
                        else:
                            # Fallback preview for non-JSON-like results
                            preview_text = str(result_obj)
                            print(f"📄 Result preview: {preview_text[:500]}...")
                        
                    except Exception as e:
                        print(f"❌ Tool call failed: {e}")
                        print(f"Detailed error: {traceback.format_exc()}")
                        continue
                
                print(f"\n{'=' * 60}")
                print("✅ All tests completed!")
                print(f"{'=' * 60}")
                
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"❌ Failed to connect to SSE server: {error_type}")
        print(f"   Error message: {error_msg}")
        
        # Provide specific solutions based on error type
        if "ConnectError" in error_type or "connection" in error_msg.lower():
            print(f"\n💡 Connection failed. Possible causes:")
            if is_local_url(SSE_URL):
                print(f"   1. Server is not running")
                print(f"      → Start the server: python -m netmind_web3_mcp.server")
                print(f"   2. Server is running on a different port")
                print(f"      → Edit SSE_URL in this file to match the server port")
                print(f"   3. Firewall is blocking the connection")
                print(f"      → Check firewall settings")
            else:
                print(f"   1. Remote server is not accessible")
                print(f"      → Check if the server URL is correct")
                print(f"   2. Network connectivity issues")
                print(f"      → Check your internet connection")
                print(f"   3. Firewall is blocking the connection")
                print(f"      → Check firewall settings")
        
        # Check if it's a proxy error
        if "Privoxy" in error_msg or "proxy" in error_msg.lower() or "500" in error_msg:
            print(f"\n⚠️  Proxy detected! Local requests are being intercepted.")
            print(f"💡 Solution: Set NO_PROXY environment variable:")
            if is_local_url(SSE_URL):
                print(f"   NO_PROXY=127.0.0.1,localhost python test/test_sse.py")
            print(f"\nOr disable proxy temporarily:")
            print(f"   unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY")
            print(f"   python test/test_sse.py")
        
        print(f"\n📋 Troubleshooting steps:")
        if is_local_url(SSE_URL):
            print(f"   1. Verify server is running:")
            print(f"      python -m netmind_web3_mcp.server")
            print(f"   2. Check server logs for errors")
            print(f"   3. Try a different port:")
            print(f"      MCP_PORT=9000 python -m netmind_web3_mcp.server")
            print(f"      Then edit SSE_URL in this file: SSE_URL = \"http://127.0.0.1:9000/sse\"")
            print(f"   4. Check if port is already in use:")
            print(f"      lsof -i :8000  # or netstat -an | grep 8000")
        else:
            print(f"   1. Verify the remote server URL is correct")
            print(f"   2. Check if the server is accessible from your network")
            print(f"   3. Try accessing the server URL in a browser")
        
        print(f"\nDetailed error: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())

