import json
import traceback
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
import asyncio

server = StdioServerParameters(
    command='python3',
    args=['src/netmind_web3_mcp/server.py'],
    env={
        # 
        "BACKEND_URL": "https://xyz-api.protago-dev.com/tokenAddress/queryTokenAddressList",
        "COINGECKO_API_KEY": "CG-dkuNv3fGtwfvnhZWuRkREvpe",
        }   
)


async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            
            await session.initialize()
            response = await session.list_tools()
            tools = [dict(t) for t in response.tools]
            #print(json.dumps(tools, indent=4, ensure_ascii=False))
            tools_to_call = [
                    # ('query_token_addressList', 
                    #  #
                    #  {
                    #      'tokenName': "USDT",
                    #     # 'tokenAddress': "0xfde4c96c8593536e31f229ea8f37b2ada2699bb2",
                    #  }
                    # ),
                    # ('query_coingecko_market_data', 
                    #  {
                    #      "ids": "bitcoin",
                    #      "vs_currency": "usd",
                    #      "price_change_percentage": "1h"
                    #  }
                    # ),
                    ('query_coingecko_market_data', 
                     {
                         "ids": "bitcoin,ethereum,solana,cardano,polkadot",
                         "vs_currency": "usd",
                         "price_change_percentage": "1h,24h,7d"
                     }
                    )
                ]
            
            for tool_name, args in tools_to_call:
                print(f"\n🛠️ call tool ...: {tool_name}")
                try:
                    response = await session.call_tool(tool_name, arguments=args)
                    
                    print("✅ call succeeded!")
                    print("📄 result content:", response.content[0].text)
                    # for content in response.content:
                    #     print(json.dumps(json.loads(content.text), indent=1, ensure_ascii=False))
                    # print(f"📊 result count: {len(response.content)}")
                    
                except Exception as e:
                    print(f"❌ call tool {tool_name} failed: {e}")
                    print(f"Detailed error information: {traceback.format_exc()}")
                    continue


if __name__ == "__main__":
    asyncio.run(main())