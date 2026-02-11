"""Authentication helpers for MCP server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from mcp.server.auth.provider import AccessToken, TokenVerifier


@dataclass(frozen=True)
class StaticTokenVerifier(TokenVerifier):
    """Verify a static bearer token from Authorization header."""

    token: str
    scopes: Iterable[str] = ()
    client_id: str = "static-token"

    async def verify_token(self, token: str) -> AccessToken | None:
        if token != self.token:
            return None
        return AccessToken(
            token=token,
            client_id=self.client_id,
            scopes=list(self.scopes),
        )
