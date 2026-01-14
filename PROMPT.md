# Netmind Web3 MCP Server - Agent Prompt

This is an **MCP (Model Context Protocol) server** that provides Web3 tools for cryptocurrency market data and token information queries.

## Available Tools

### 1. `query_token_addressList`

Query token address information based on token name or address.

**Parameters:**

- `tokenName` (optional, string): Token symbol(s). Can be a single token symbol or comma-separated values (e.g., "DINO" or "DINO,BALD")
- `tokenAddress` (optional, string): Token contract address(es). Can be a single address or comma-separated values (e.g., "0x..." or "0x...,0x...")

**Requirements:**

- At least one of `tokenName` or `tokenAddress` must be provided
- Multiple values can be provided as comma-separated strings

**Returns:** Token address information in JSON format

**Examples:**
- `query_token_addressList(tokenName="DINO")`
- `query_token_addressList(tokenName="DINO,BALD")` (multiple values)
- `query_token_addressList(tokenAddress="0x...")`

---

### 2. `query_reply_by_news_summary`

Query news reply by news summary based on Web3 entity name.

**Parameters:**

- `content` (required, string): Web3 entity identifier for news retrieval. Only a single entity identifier is allowed.
  - Can be Token symbol/name (e.g., "ETH", "Bitcoin")
  - Can be chain name (e.g., "Solana")
  - Can be project name (e.g., "Uniswap")
  - **Important**: Do not pass complete sentences, event descriptions, or analysis intentions. Only pass a single entity name.

**Requirements:**

- `content` parameter is required and cannot be empty
- Only a single entity identifier is allowed (not multiple entities or sentences)

**Returns:** News reply information in JSON format

**Examples:**
- `query_reply_by_news_summary(content="ETH")`
- `query_reply_by_news_summary(content="Bitcoin")`
- `query_reply_by_news_summary(content="Solana")`

---

### 3. `query_coingecko_market_data`

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

**Returns:** Array of coin objects with market data and 7-day historical charts

**Examples:**
- `query_coingecko_market_data(ids="bitcoin")`
- `query_coingecko_market_data(ids="bitcoin,ethereum,solana", price_change_percentage="1h,24h,7d")`
- `query_coingecko_market_data(symbols="btc,eth")`

---

### 4. `query_coingecko_top_token_traders`

Query CoinGecko for top token traders by token address on a network.

**Parameters:**

- `token_address` (required, string): Token contract address
- `network_id` (optional, string, default: "base"): Network ID (refers to /networks endpoint)
- `traders` (optional, int, default: 10): Number of top token traders to return (1-50, max: 50)
- `sort` (optional, string, default: "realized_pnl_usd_desc"): Sort the traders by field
  - Options: `realized_pnl_usd_desc`, `unrealized_pnl_usd_desc`, `total_buy_usd_desc`, `total_sell_usd_desc`
- `include_address_label` (optional, bool, default: False): Include address label data (e.g., ENS names)

**Requirements:**

- `token_address` parameter is required
- CoinGecko Pro API key with Analyst plan or above (paid subscription required)
- Only tokens created after 1st September 2022 are supported
- Stablecoins and wrapped native tokens (e.g. wSOL, wETH) are not supported

**Returns:** Top traders data with PnL, trading stats, and explorer links

**Examples:**
- `query_coingecko_top_token_traders(token_address="0x...")`
- `query_coingecko_top_token_traders(token_address="0x...", traders=20, include_address_label=True)`

**Note:** Requires Analyst plan or above. Beta feature, updates every 60s.

---

### 5. `query_coingecko_pool_trades`

Query CoinGecko for past 24 hour trades by pool address.

**Parameters:**

- `pool_address` (required, string): Pool contract address
- `network` (optional, string, default: "eth"): Network ID (refers to /networks endpoint)
- `trade_volume_in_usd_greater_than` (optional, float, default: 0.0): Filter trades by trade volume in USD greater than this value
- `token` (optional, string, default: "base"): Return trades for token. Use this to invert the chart
  - Options: `"base"`, `"quote"`, or token address

**Requirements:**

- `pool_address` parameter is required
- CoinGecko Pro API key (Basic, Analyst, Lite, Pro, Enterprise)

**Returns:** Last 300 trades in past 24 hours with price, volume, and transaction data

**Examples:**
- `query_coingecko_pool_trades(pool_address="0x...")`
- `query_coingecko_pool_trades(pool_address="0x...", trade_volume_in_usd_greater_than=1000.0)`

**Note:** Real-time data, last 300 trades.

---

### 6. `query_coingecko_token_trades`

Query CoinGecko for past 24 hour trades by token address across all pools.

**Parameters:**

- `token_address` (required, string): Token contract address
- `network` (optional, string, default: "eth"): Network ID (refers to /networks endpoint)
- `trade_volume_in_usd_greater_than` (optional, float, default: 0.0): Filter trades by trade volume in USD greater than this value

**Requirements:**

- `token_address` parameter is required
- CoinGecko Pro API key with Paid Plan (Analyst, Lite, Pro, Enterprise)

**Returns:** Last 300 trades in past 24 hours across all pools with DEX and pool info

**Examples:**
- `query_coingecko_token_trades(token_address="0x...")`
- `query_coingecko_token_trades(token_address="0x...", trade_volume_in_usd_greater_than=5000.0)`

**Note:** Requires paid plan. Real-time data across all pools.

---

## When to Use Each Tool

**Use `query_token_addressList` when:**

- You need to find token contract addresses
- You want to verify token information by name or address
- You're working with token addresses in transactions or smart contracts

**Use `query_reply_by_news_summary` when:**

- You need to get news information about a specific Web3 entity
- You want to retrieve news summaries for tokens, chains, or projects
- You need news-related information for a single Web3 entity (by symbol, name, chain, or project name)

**Use `query_coingecko_market_data` when:**

- You need current cryptocurrency prices and market data
- You want historical price trends and charts
- You need to compare multiple cryptocurrencies
- You're analyzing market trends, volumes, or price changes
- You need market cap, trading volume, or other market metrics

**Use `query_coingecko_top_token_traders` when:**

- You need to analyze top traders for a specific token
- You want to see trader PnL (profit and loss) data
- You need to understand trading patterns and volumes
- You want to identify whale addresses or significant traders
- You're analyzing on-chain trading activity for a token

**Use `query_coingecko_pool_trades` when:**

- You need to see recent trades for a specific liquidity pool
- You want to analyze trading activity within a pool
- You need to track buy/sell patterns for a pool
- You're monitoring pool trading volume and price movements
- You want to filter trades by volume threshold

**Use `query_coingecko_token_trades` when:**

- You need to see recent trades for a token across all pools
- You want to analyze trading activity across multiple DEXes
- You need to track token trading patterns across different pools
- You're monitoring token trading volume and price movements across all pools
- You want to filter trades by volume threshold

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
