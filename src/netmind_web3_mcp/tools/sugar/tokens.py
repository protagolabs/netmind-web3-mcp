"""Sugar MCP token-related tools."""

from netmind_sugar.chains import get_chain, Token, Price
from web3 import Web3
from .models import TokenInfo, PriceInfo


async def query_sugar_get_all_tokens(
    limit: int,
    offset: int,
    chainId: str = "8453",
) -> list:
    """Retrieve all tokens supported by the protocol.

    Args:
        limit: Maximum number of tokens to return
        offset: The starting point to retrieve tokens
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[TokenInfo]: A list of Token objects
    """
    with get_chain(chainId) as chain:
        tokens = chain.get_tokens_page(limit, offset)
        tokens = list(
            map(
                lambda t: TokenInfo.from_token(
                    Token.from_tuple(t, chain_id=chain.chain_id, chain_name=chain.name)
                ),
                tokens,
            )
        )
        return tokens


async def query_sugar_get_token_prices(
    token_address: str,
    chainId: str = "8453",
) -> list:
    """Retrieve prices for a specific token in terms of the stable token.

    Args:
        token_address: The address of the token to retrieve prices for
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[PriceInfo]: A list of Price objects with token-price mappings
    """
    token_address = Web3.to_checksum_address(token_address)
    with get_chain(chainId) as chain:
        append_stable = False
        append_native = False

        tokens = [chain.get_token(token_address)]
        if chain.settings.stable_token_addr.lower() != token_address.lower():
            tokens.append(chain.get_token(chain.settings.stable_token_addr))
            append_stable = True

        if chain.settings.native_token_symbol.lower() != token_address.lower():
            tokens.append(
                Token.make_native_token(
                    chain.settings.native_token_symbol,
                    chain.settings.wrapped_native_token_addr,
                    chain.settings.native_token_decimals,
                    chain_id=chain.chain_id,
                    chain_name=chain.name,
                )
            )
            append_native = True

        prices = chain.get_prices(tokens)
        prices = [PriceInfo.from_price(p) for p in prices]
        if append_stable:
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.stable_token_addr.lower()
            ]

        if append_native:
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.native_token_symbol.lower()
            ]
        return prices


async def query_sugar_get_prices(
    limit: int,
    offset: int,
    listed_only: bool = False,
    chainId: str = "8453",
) -> list:
    """Retrieve prices for a list of tokens in terms of the stable token.

    Args:
        limit: Maximum number of prices to return
        offset: The starting point to retrieve prices
        listed_only: If True, only return prices for tokens that are marked as 'listed'
        chainId: The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[PriceInfo]: A list of Price objects with token-price mappings
    """
    with get_chain(chainId) as chain:
        tokens = chain.get_tokens_page(limit, offset)
        tokens = list(
            map(
                lambda t: Token.from_tuple(
                    t, chain_id=chain.chain_id, chain_name=chain.name
                ),
                tokens,
            )
        )

        append_stable = False
        append_native = False

        token_address_list = [t.token_address.lower() for t in tokens]
        if chain.settings.stable_token_addr.lower() not in token_address_list:
            tokens.append(chain.get_token(chain.settings.stable_token_addr))
            append_stable = True

        if chain.settings.native_token_symbol.lower() not in token_address_list:
            tokens.append(
                Token.make_native_token(
                    chain.settings.native_token_symbol,
                    chain.settings.wrapped_native_token_addr,
                    chain.settings.native_token_decimals,
                    chain_id=chain.chain_id,
                    chain_name=chain.name,
                )
            )
            append_native = True

        prices = chain.get_prices(tokens)
        prices = [PriceInfo.from_price(p) for p in prices]
        if append_stable:
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.stable_token_addr.lower()
            ]

        if append_native:
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.native_token_symbol.lower()
            ]

        return prices

