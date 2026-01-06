"""News query tools using backend API."""

import httpx
from .config import get_config


async def query_reply_by_news_summary(content: str) -> str:
    """Query news reply by news summary based on Web3 entity name.
    
    Args:
        content: Web3 entity identifier for news retrieval. Only a single entity identifier is allowed.
                 Can be Token symbol/name, chain name, or project name (e.g., "ETH", "Bitcoin", "Solana", "Uniswap").
                 Do not pass complete sentences, event descriptions, or analysis intentions.
                 Only pass a single entity name.
    
    Returns:
        News reply information in JSON format.
    
    Example:
        - Token symbol: content="ETH"
        - Token name: content="Bitcoin"
        - Chain name: content="Solana"
        - Project name: content="Uniswap"
    """
    if not content or not content.strip():
        raise ValueError("content parameter is required and cannot be empty")
    
    # Validate that content is a single entity (not a sentence)
    content = content.strip()
    if len(content.split()) > 3:  # Simple validation: if more than 3 words, likely a sentence
        raise ValueError(
            "content should be a single Web3 entity identifier (Token symbol/name, chain name, or project name). "
            "Do not pass complete sentences, event descriptions, or analysis intentions."
        )
    
    config = get_config()
    base_url = config.get_base_url()
    
    # Append the route path to the base URL
    route_path = "/news/getReplyByNewsSummary"
    url = f"{base_url}{route_path}"
    
    # POST request with content parameter as form-urlencoded data
    # Some backends expect form-urlencoded instead of JSON
    data = {"content": content}
    
    response = httpx.post(url, data=data, timeout=config.get_timeout())
    response.raise_for_status()
    return response.text

