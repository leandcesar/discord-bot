import re

import disnake
from disnake_plugins import Plugin

from src.bot import Bot
from src.util.webhook import application_webhook

plugin = Plugin[Bot]()

INSTAGRAM_URL_REGEX = re.compile(r"https?://(?:www\.)?instagram\.com/\S+/\S+")
TWITTER_URL_REGEX = re.compile(r"https?://(?:www\.)?twitter\.com/\S+status/\S+")
X_URL_REGEX = re.compile(r"https?://(?:www\.)?x\.com/\S+status/\S+")
URLS_REPLACE_REGEX: list[tuple[re.Pattern, str, str]] = [
    (INSTAGRAM_URL_REGEX, "instagram.com", "instagramez.com"),
    (TWITTER_URL_REGEX, "twitter", "fxtwitter"),
    (X_URL_REGEX, "x", "fxtwitter"),
]


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    content = message.content
    for url_replace_regex in URLS_REPLACE_REGEX:
        content = url_replace_regex[0].sub(
            lambda match: match.group(0).replace(url_replace_regex[1], url_replace_regex[2]),
            content,
        )
    if content == message.content:
        return None
    webhook = await application_webhook(plugin.bot, message.channel)
    files = [await attachment.to_file() for attachment in message.attachments]
    await webhook.send(
        content,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url,
        files=files,
    )
    await message.edit(suppress_embeds=True)


setup, teardown = plugin.create_extension_handlers()
