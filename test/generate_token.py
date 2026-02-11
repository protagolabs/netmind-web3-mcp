"""Generate a random auth token for MCP."""

from __future__ import annotations

import base64
import secrets


def main() -> None:
    token = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    print(token)


if __name__ == "__main__":
    main()
