import typing as t
from dataclasses import dataclass

from src.util.dataclass import to_instance
from src.util.http import APIHTTPClient, aiohttp


@dataclass
class Message:
    role: t.Literal["assistant", "system", "tool", "user"]
    content: str


@dataclass
class Choice:
    index: str
    message: Message
    logprobs: str | None
    finish_reason: str | None

    def __post_init__(self):
        self.message = Message(**self.message)


@dataclass
class Usage:
    queue_time: float
    prompt_tokens: int
    prompt_time: float
    completion_tokens: float
    completion_time: float
    total_tokens: float
    total_time: float


@dataclass
class ChatCompletion:
    id: str
    choices: list[Choice]
    usage: Usage

    def __post_init__(self):
        self.choices = [Choice(**choice) for choice in self.choices]
        self.usage = Usage(**self.usage)


@dataclass
class XGroq:
    id: str


@dataclass
class Transcription:
    text: str
    x_groq: XGroq

    def __post_init__(self):
        self.x_groq = XGroq(**self.x_groq)


class Groq(APIHTTPClient):
    def __init__(self, api_key: str | None, **kwargs) -> None:
        self.api_key = api_key
        super().__init__(**kwargs)

    async def _chat_completions(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float = 0.5,
        max_completion_tokens: int = 1024,
    ) -> ChatCompletion:
        # Docs: https://console.groq.com/docs/api-reference#chat-create
        data = await self.request(
            "POST",
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_completion_tokens": max_completion_tokens,
            },
        )
        return to_instance(data, ChatCompletion)  # type: ignore[arg-type]

    async def _audio_transcriptions(
        self,
        audio_data: bytes,
        audio_filename: str,
        *,
        model: str,
        temperature: float = 0.0,
        language: str = "pt",
    ) -> Transcription:
        # Docs: https://console.groq.com/docs/api-reference#audio-transcription
        form_data = aiohttp.FormData()
        form_data.add_field("file", audio_data, filename=audio_filename)
        form_data.add_field("model", model)
        form_data.add_field("temperature", str(temperature))
        form_data.add_field("language", language)
        data = await self.request(
            "POST",
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            data=form_data,
        )
        return to_instance(data, Transcription)  # type: ignore[arg-type]

    async def chat_completions(
        self,
        prompt: str,
        message: str,
        **kwargs,
    ) -> str:
        chat_completion = await self._chat_completions(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message},
            ],
            **kwargs,
        )
        return chat_completion.choices[0].message.content

    async def audio_transcriptions(
        self,
        audio_data: bytes,
        audio_filename: str,
        **kwargs,
    ) -> str:
        transcription = await self._audio_transcriptions(
            audio_data=audio_data,
            audio_filename=audio_filename,
            **kwargs,
        )
        return transcription.text
