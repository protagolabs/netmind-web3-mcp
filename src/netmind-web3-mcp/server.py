import httpx
import os
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("netmind-web3-mcp")


@mcp.tool()
async def query_token_addressList(tokenName: str = None, tokenAddress: str = None) -> str:
    """Query address list based on token name or address.
     
    Args:
    tokenName: Symbol of the token
    tokenAddress: Address of the token
    
    At least one of tokenName or tokenAddress must be provided.
    """
    
    if not tokenName and not tokenAddress:
        raise ValueError("At least one of tokenName or tokenAddress must be provided")
    
    baseUrl = os.environ["BACKEND_URL"]
    params = []
    
    if tokenName:   
        params.append(f"tokenName={tokenName}")
    if tokenAddress:
        params.append(f"tokenAddress={tokenAddress}")
    
    if params:
        baseUrl += "?" + "&".join(params)
    
    return httpx.get(baseUrl).text

def main():
    if not os.environ.get("BACKEND_URL"):
        raise ValueError(
            "Environment variable BACKEND_URL is not set. Please set it."  
        )
    
    print("Starting Netmind Web3 MCP server...")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()