import re

import disnake
from disnake.ext import commands
from disnake.ext.commands.errors import BadArgument

CUSTOM_EMOTE_REGEX = re.compile(r"<(a?):(\w+):(\d+)>")
UNICODE_EMOJI_REGEX = re.compile(
    r"[\U0001F600-\U0001F64F]"
    r"|[\U0001F300-\U0001F5FF]"
    r"|[\U0001F680-\U0001F6FF]"
    r"|[\U0001F1E0-\U0001F1FF]"
    r"|[\U00002702-\U000027B0]"
    r"|[\U000024C2-\U0001F251]"
    r"|[\U0001F900-\U0001F9FF]"
    r"|[\U0001FA70-\U0001FAFF]"
    r"|[\U00002600-\U000026FF]"
    r"|[\U00002B50-\U00002B55]",
    flags=re.UNICODE,
)


class Emote(disnake.PartialEmoji):
    @staticmethod
    def _validate(value: str) -> bool:
        return bool(UNICODE_EMOJI_REGEX.match(value) or CUSTOM_EMOTE_REGEX.match(value))

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, value: str) -> disnake.PartialEmoji:  # noqa: N805
        if not cls._validate(value):
            raise BadArgument(f"Invalid emoji or custom emote: {value!r}")
        instance = cls.from_str(value)  # type: ignore
        instance._state = inter._state
        return instance
