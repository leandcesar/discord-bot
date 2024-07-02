import aiohttp

from bot import config


class G4F:
    __slots__ = ("_history", "model", "prompt", "provider", "history_size")

    def __init__(
        self,
        prompt: str | None = None,
        *,
        model: str = "gpt-3.5-turbo-16k",
        provider: str = "Chatgpt4Online",
        history_size: int | None = None,
    ) -> None:
        self._history: list[dict[str, str]] = []
        self.prompt: str | None = prompt
        self.model: str = model
        self.provider: str = provider
        self.history_size: int | None = history_size

    @property
    def history(self) -> list[dict[str, str]]:
        self._history = self._history[-self.history_size :] if self.history_size else []
        return self._history

    async def chat_completions(self, message: str) -> str:
        prompt = {"role": "system", "content": self.prompt}
        user_input = {"role": "user", "content": message}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.G4F_API_URL}/{config.G4F_API_VERSION}/chat/completions",
                json={
                    "model": self.model,
                    "provider": self.provider,
                    "stream": False,
                    "messages": [prompt] + self.history + [user_input],
                },
                timeout=60,
            ) as response:
                data = await response.json()
                contents = [choice["message"].get("content", "") for choice in data.get("choices", [])]
                content = " ".join(contents)
                assistant_output = {"role": "assistant", "content": content}
                self.history.append(user_input)
                self.history.append(assistant_output)
                return content
