"""Data models for Sugar MCP tools."""

from typing import Optional, List, Tuple
from pydantic import Field, BaseModel
from netmind_sugar.chains import Token, Price, LiquidityPool, Quote, LiquidityPoolForSwap
from netmind_sugar.pool import Amount, LiquidityPoolEpoch


class TokenInfo(BaseModel):
    chain_id: str = Field(..., description="Chain ID, e.g., '10' for OPChain, '8453' for BaseChain")
    chain_name: str = Field(..., description="Chain name, e.g., 'OPChain', 'BaseChain'")
    token_address: str = Field(..., description="Token contract address")
    symbol: str = Field(..., description="Token symbol, e.g., 'USDC', 'VELO'")
    decimals: int = Field(..., description="Number of decimals for the token")
    listed: bool = Field(..., description="Whether the token is listed")
    wrapped_token_address: str = Field(default="", description="Wrapped token address")

    @staticmethod
    def from_token(t: Token):
        return TokenInfo(
            chain_id=t.chain_id,
            chain_name=t.chain_name,
            token_address=t.token_address,
            symbol=t.symbol,
            decimals=t.decimals,
            listed=t.listed,
            wrapped_token_address=t.wrapped_token_address if t.wrapped_token_address else "",
        )


class PriceInfo(BaseModel):
    token: TokenInfo = Field(..., description="Token information")
    price: float = Field(..., description="Price in stable token")

    @staticmethod
    def from_price(p: Price):
        token_info = TokenInfo.from_token(p.token)
        return PriceInfo(token=token_info, price=p.price)


class AmountInfo(BaseModel):
    token: TokenInfo = Field(..., description="Token information")
    amount: int = Field(..., description="Amount in wei")
    price: PriceInfo = Field(..., description="Price information")
    amount_in_stable: float = Field(..., description="Amount in stable token")

    @staticmethod
    def from_amount(a: Amount):
        price_info = PriceInfo.from_price(a.price)
        return AmountInfo(
            token=TokenInfo.from_token(a.token),
            amount=a.amount,
            price=price_info,
            amount_in_stable=a.amount_in_stable
        )


class LiquidityPoolInfo(BaseModel):
    chain_id: str = Field(..., description="Chain ID")
    chain_name: str = Field(..., description="Chain name")
    lp: str = Field(..., description="Liquidity pool address")
    factory: str = Field(..., description="Factory address")
    symbol: str = Field(..., description="Pool symbol")
    type: int = Field(..., description="Pool type")
    is_stable: bool = Field(..., description="Whether the pool is stable")
    is_cl: bool = Field(..., description="Whether the pool is concentrated liquidity")
    total_supply: float = Field(..., description="Total supply of the pool")
    decimals: int = Field(..., description="Number of decimals for the pool")
    token0: TokenInfo = Field(..., description="Token0 information")
    reserve0: AmountInfo = Field(..., description="Token0 reserve amount")
    token1: TokenInfo = Field(..., description="Token1 information")
    reserve1: AmountInfo = Field(..., description="Token1 reserve amount")
    token0_fees: AmountInfo = Field(..., description="Token0 fees")
    token1_fees: AmountInfo = Field(..., description="Token1 fees")
    pool_fee: float = Field(..., description="Pool fee")
    gauge_total_supply: float = Field(..., description="Gauge total supply")
    emissions: Optional[AmountInfo] = Field(None, description="Emissions information")
    emissions_token: Optional[TokenInfo] = Field(None, description="Emissions token information")
    weekly_emissions: Optional[AmountInfo] = Field(None, description="Weekly emissions information")
    nfpm: str = Field(..., description="NFPM information")
    alm: str = Field(..., description="ALM information")
    tvl: float = Field(..., description="Total value locked in stable token")
    total_fees: float = Field(..., description="Total fees in stable token")
    pool_fee_percentage: float = Field(..., description="Pool fee percentage")
    volume_pct: float = Field(..., description="Volume percentage")
    volume: float = Field(..., description="Volume in stable token")
    token0_volume: float = Field(..., description="Token0 volume in stable token")
    token1_volume: float = Field(..., description="Token1 volume in stable token")
    gauge_staked_pct: float = Field(..., description="Gauge staked percentage")
    apr: float = Field(..., description="Annual percentage rate")

    @staticmethod
    def from_pool(p: LiquidityPool):
        return LiquidityPoolInfo(
            chain_id=p.chain_id,
            chain_name=p.chain_name,
            lp=p.lp,
            factory=p.factory,
            symbol=p.symbol,
            type=p.type,
            is_stable=p.is_stable,
            is_cl=p.is_cl,
            total_supply=p.total_supply,
            decimals=p.decimals,
            token0=TokenInfo.from_token(p.token0),
            reserve0=AmountInfo.from_amount(p.reserve0) if p.reserve0 else None,
            token1=TokenInfo.from_token(p.token1),
            reserve1=AmountInfo.from_amount(p.reserve1) if p.reserve1 else None,
            token0_fees=AmountInfo.from_amount(p.token0_fees) if p.token0_fees else None,
            token1_fees=AmountInfo.from_amount(p.token1_fees) if p.token1_fees else None,
            pool_fee=p.pool_fee,
            gauge_total_supply=p.gauge_total_supply,
            emissions=AmountInfo.from_amount(p.emissions) if p.emissions else None,
            emissions_token=TokenInfo.from_token(p.emissions_token) if p.emissions_token else None,
            weekly_emissions=AmountInfo.from_amount(p.weekly_emissions) if p.weekly_emissions else None,
            nfpm=p.nfpm,
            alm=p.alm,
            tvl=p.tvl,
            total_fees=p.total_fees,
            pool_fee_percentage=p.pool_fee_percentage,
            volume_pct=p.volume_pct,
            volume=p.volume_pct * (p.token0_fees.amount_in_stable + p.token1_fees.amount_in_stable if p.token0_fees and p.token1_fees else 0),
            token0_volume=p.token0_volume,
            token1_volume=p.token1_volume,
            gauge_staked_pct=(p.gauge_total_supply / p.total_supply * 100 if p.total_supply > 0 else 0),
            apr=p.apr
        )


class LiquidityPoolForSwapInfo(BaseModel):
    chain_id: str = Field(..., description="Chain ID")
    chain_name: str = Field(..., description="Chain name")
    lp: str = Field(..., description="Liquidity pool address")
    type: int = Field(..., description="Pool type")
    token0_address: str = Field(..., description="Token0 address")
    token1_address: str = Field(..., description="Token1 address")

    @staticmethod
    def from_pool(p: LiquidityPoolForSwap):
        return LiquidityPoolForSwapInfo(
            chain_id=p.chain_id,
            chain_name=p.chain_name,
            lp=p.lp,
            type=p.type,
            token0_address=p.token0_address,
            token1_address=p.token1_address
        )


class LiquidityPoolEpochInfo(BaseModel):
    ts: int = Field(..., description="Timestamp of the epoch")
    lp: str = Field(..., description="Liquidity pool address")
    pool: LiquidityPoolInfo = Field(..., description="Liquidity pool information")
    votes: int = Field(..., description="Number of votes")
    emissions: int = Field(..., description="Emissions amount")
    incentives: List[AmountInfo] = Field(..., description="List of incentives amounts")
    fees: List[AmountInfo] = Field(..., description="List of fees amounts")

    @staticmethod
    def from_epoch(e: LiquidityPoolEpoch):
        return LiquidityPoolEpochInfo(
            ts=e.ts,
            lp=e.lp,
            pool=LiquidityPoolInfo.from_pool(e.pool),
            votes=e.votes,
            emissions=e.emissions,
            incentives=[AmountInfo.from_amount(i) for i in e.incentives],
            fees=[AmountInfo.from_amount(f) for f in e.fees]
        )


class QuoteInputInfo(BaseModel):
    from_token: TokenInfo = Field(..., description="From token information")
    to_token: TokenInfo = Field(..., description="To token information")
    path: List[Tuple[LiquidityPoolForSwapInfo, bool]] = Field(..., description="Swap path as list of (pool, reversed) tuples")
    amount_in: int = Field(..., description="Input amount in wei")

    @staticmethod
    def from_quote_input(q: Quote):
        return QuoteInputInfo(
            from_token=TokenInfo.from_token(q.input.from_token),
            to_token=TokenInfo.from_token(q.input.to_token),
            path=[(LiquidityPoolForSwapInfo.from_pool(p), rev) for p, rev in q.input.path],
            amount_in=q.input.amount_in
        )


class QuoteInfo(BaseModel):
    input: QuoteInputInfo = Field(..., description="Quote input information")
    amount_out: int = Field(..., description="Output amount in wei")

    @staticmethod
    def from_quote(q: Quote):
        return QuoteInfo(
            input=QuoteInputInfo.from_quote_input(q),
            amount_out=q.amount_out
        )
