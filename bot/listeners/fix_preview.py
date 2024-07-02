import re

import disnake
from disnake.ext import commands

from bot import Bot
from bot.ext import application_webhook

PATTERNS_AND_REPLACEMENTS = [
    (
        re.compile(r"https?://(?:www\.)?instagram\.com/\S+"),
        lambda match: match.group(0).replace("instagram.com", "ddinstagram.com"),
    ),
    (
        re.compile(r"https?://(?:www\.)?(?:open\.)?spotify\.com/\S+"),
        lambda match: match.group(0).replace("/intl-pt/", "/"),
    ),
    (
        re.compile(r"https?://(?:www\.|vm\.)?tiktok\.com/\S+"),
        lambda match: match.group(0).replace("tiktok", "vxtiktok"),
    ),
    (
        re.compile(r"https?://(?:www\.)?twitter\.com/\S+"),
        lambda match: match.group(0).replace("twitter", "fxtwitter"),
    ),
    (
        re.compile(r"https?://(?:www\.)?x\.com/\S+"),
        lambda match: match.group(0).replace("x", "fxtwitter"),
    ),
]


class FixPreview(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot:
            return None
        content = message.content
        for pattern, replacement in PATTERNS_AND_REPLACEMENTS:
            content = pattern.sub(replacement, content)
        if content == message.content:
            return None
        webhook = await application_webhook(self.bot, message.channel)
        files = [await attachment.to_file() for attachment in message.attachments]
        await webhook.send(
            content,
            username=message.author.display_name,
            avatar_url=message.author.display_avatar.url,
            files=files,
        )
        await message.edit(suppress_embeds=True)


def setup(bot: Bot) -> None:
    bot.add_cog(FixPreview(bot))
