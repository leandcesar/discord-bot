import datetime as dt
import re
import typing as t
from dataclasses import dataclass

from src.util.dataclass import to_instance
from src.util.http import APIHTTPClient


@dataclass
class Intent:
    id: str
    name: str
    confidence: float


@dataclass
class Message:
    text: str
    intents: list[Intent]
    entities: dict[str, t.Any]

    def __post_init__(self):
        self.intents = [Intent(**intent) for intent in self.intents]


class WitAI(APIHTTPClient):
    def __init__(self, access_token: str | None, **kwargs) -> None:
        self.access_token = access_token
        super().__init__(**kwargs)

    async def _fetch_intents_and_entities(self, message: str, /) -> Message:
        # Docs: https://wit.ai/docs/http/20240304/#get__message_link
        data = await self.request(
            "GET",
            "https://api.wit.ai/message",
            params={"v": 20250321, "q": message},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        return to_instance(data, Message)  # type: ignore[arg-type]

    async def detect_datetime(self, message: str, /) -> dt.datetime | None:
        message = re.sub(r"(\d+)\s?m\b", r"\1 minutes ", message)
        message = re.sub(r"(\d+)\s?s\b", r"\1 seconds ", message)
        intents_and_entities = await self._fetch_intents_and_entities(message)
        if intents_and_entities.entities and "wit$datetime:datetime" in intents_and_entities.entities:
            entity = intents_and_entities.entities["wit$datetime:datetime"][0]
            return dt.datetime.fromisoformat(entity["value"])
        if intents_and_entities.entities and "wit$duration:duration" in intents_and_entities.entities:
            entity = intents_and_entities.entities["wit$duration:duration"][0]
            seconds = entity["normalized"]["value"]
            return dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=seconds)
        return None
