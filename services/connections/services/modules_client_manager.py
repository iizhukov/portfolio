from typing import Optional

from shared.clients import ModulesClient


_client: Optional[ModulesClient] = None


def set_client(client: ModulesClient | None) -> None:
    global _client
    _client = client


def get_client() -> Optional[ModulesClient]:
    return _client

