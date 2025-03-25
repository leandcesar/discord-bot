from __future__ import annotations

from src import log

logger = log.get_logger(__name__)

__all__ = (
    "BotError",
    "HTTPError",
)


class BotError(Exception):
    pass


class HTTPError(Exception):
    def __init__(self, method: str, url: str, status: int) -> None:
        logger.error(f"{method} request to {url} failed - {status}")
        super().__init__(f"Request to {url} failed - {status}")
        self.status = status
