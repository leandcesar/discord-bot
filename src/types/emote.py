from __future__ import annotations

import re

import disnake
from disnake.ext import commands

CUSTOM_EMOTE_REGEX = re.compile(r"<a?:\w+:(\d+)>")
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


class Emote:
    def __init__(
        self,
        *,
        emoji: str | None = None,
        custom_emoji: disnake.Emoji | None = None,
    ) -> None:
        self.emoji: str | None = None
        self.custom_emoji: disnake.Emoji | None = None
        if emoji:
            self.emoji = emoji
            self.custom_emoji = None
        elif custom_emoji:
            self.emoji = None
            self.custom_emoji = custom_emoji
        else:
            raise ValueError("")  # TODO: add message

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, value: str) -> Emote:  # noqa: N805
        emoji_match = UNICODE_EMOJI_REGEX.match(value)
        if emoji_match:
            return cls(emoji=value)  # type: ignore
        custom_emote_match = CUSTOM_EMOTE_REGEX.match(value)
        if custom_emote_match:
            emoji_id = custom_emote_match.group(1)
            emoji = await inter.guild.fetch_emoji(emoji_id)
            return cls(custom_emoji=emoji)  # type: ignore
        else:
            raise ValueError("")  # TODO: add message

    def __repr__(self) -> str:
        return repr(self.emoji or self.custom_emoji)

    def __str__(self) -> str:
        return str(self.emoji or self.custom_emoji)
