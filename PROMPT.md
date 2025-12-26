# Netmind Web3 MCP Server - Agent Prompt

This is an **MCP (Model Context Protocol) server** that provides Web3 tools for cryptocurrency market data and token information queries.

## Available Tools

### 1. `query_token_addressList`

Query token address information based on token name or address.

**Parameters:**

- `tokenName` (optional, string): Token symbol (e.g., "USDT", "BTC")
- `tokenAddress` (optional, string): Token contract address

**Requirements:**

- At least one of `tokenName` or `tokenAddress` must be provided

**Returns:**

- Token address information in JSON format

**Example Usage:**

- Query by token name: `query_token_addressList(tokenName="USDT")`
- Query by address: `query_token_addressList(tokenAddress="0x...")`
- Query by both: `query_token_addressList(tokenName="USDT", tokenAddress="0x...")`

---

### 2. `query_coingecko_market_data`

Query CoinGecko Pro API for comprehensive cryptocurrency market data including real-time prices, market metrics, and 7-day historical price charts.

**Key Features:**

- Multi-coin batch queries with automatic concurrent processing
- Historical price chart data (7 days) included for each coin
- Flexible filtering and sorting options
- Support for multiple currencies and timeframes

**Parameters:**

- `vs_currency` (optional, string, default: "usd"): Target currency (e.g., "usd", "eur", "btc")
- `ids` (optional, string): Comma-separated coin IDs (e.g., "bitcoin,ethereum,solana")
- `names` (optional, string): Comma-separated coin names (e.g., "Bitcoin,Ethereum")
- `symbols` (optional, string): Comma-separated coin symbols (e.g., "btc,eth,sol")
- `include_tokens` (optional, string, default: "top"): For symbol queries, use "all" to include all matching tokens
- `category` (optional, string): Filter by category (e.g., "layer-1", "defi")
- `order` (optional, string, default: "market_cap_desc"): Sort order
  - Options: `market_cap_asc`, `market_cap_desc`, `volume_asc`, `volume_desc`, `id_asc`, `id_desc`
- `per_page` (optional, int, default: 100): Results per page (1-250)
- `page` (optional, int, default: 1): Page number
- `price_change_percentage` (optional, string, default: "1h"): Comma-separated timeframes
  - Options: `1h`, `24h`, `7d`, `14d`, `30d`, `200d`, `1y`
- `locale` (optional, string, default: "en"): Language
- `precision` (optional, string): Decimal precision (0-18 or "full")

**Returns:**

- Array of coin objects, each containing:
  - Market data: current_price, market_cap, total_volume, price_change_percentage, etc.
  - Historical chart data: `history_chart` object with 7-day price, market cap, and volume time series

**Example Usage:**

- Single coin: `query_coingecko_market_data(ids="bitcoin", vs_currency="usd")`
- Multiple coins: `query_coingecko_market_data(ids="bitcoin,ethereum,solana", price_change_percentage="1h,24h,7d")`
- By symbol: `query_coingecko_market_data(symbols="btc,eth", vs_currency="usd")`
- Top coins by market cap: `query_coingecko_market_data(order="market_cap_desc", per_page=50)`

---

## When to Use Each Tool

**Use `query_token_addressList` when:**

- You need to find token contract addresses
- You want to verify token information by name or address
- You're working with token addresses in transactions or smart contracts

**Use `query_coingecko_market_data` when:**

- You need current cryptocurrency prices and market data
- You want historical price trends and charts
- You need to compare multiple cryptocurrencies
- You're analyzing market trends, volumes, or price changes
- You need market cap, trading volume, or other market metrics

## Technical Notes

- All tools require proper environment variable configuration (see README.md)
- `query_coingecko_market_data` automatically fetches 7-day historical charts for all queried coins
- Concurrent requests are automatically handled with rate limiting (max 10 concurrent)
- Errors are handled gracefully - failed requests return empty arrays instead of raising exceptions
- All data is returned in JSON format

## Integration

This server supports both stdio and SSE transport modes:

- **stdio**: For local development and direct integration
- **SSE**: For remote connections and web-based clients

Default mode is SSE, listening on `127.0.0.1:8000` by default.
