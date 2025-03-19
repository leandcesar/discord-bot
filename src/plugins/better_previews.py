import re
from collections import namedtuple

import disnake
from disnake_plugins import Plugin

from src import log
from src.bot import Bot
from src.components import application_webhook

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()

UrlRewriteRule = namedtuple("UrlRewriteRule", ["pattern", "old", "new"])

URL_REWRITE_RULES: list[UrlRewriteRule] = [
    UrlRewriteRule(re.compile(r"https?://(?:www\.)?instagram\.com/\S+"), "instagram.com", "instagramez.com"),
    UrlRewriteRule(re.compile(r"https?://(?:www\.)?twitter\.com/\S+status/\S+"), "twitter", "fxtwitter"),
    UrlRewriteRule(re.compile(r"https?://(?:www\.)?x\.com/\S+status/\S+"), "x", "fxtwitter"),
]


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    content = message.content
    for rule in URL_REWRITE_RULES:
        content = rule.pattern.sub(lambda match: match.group(0).replace(rule.old, rule.new), content)
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
    logger.debug(
        f"{message.content!r} ({message.id}) -> {content!r}",
        extra={"context": message},
    )


setup, teardown = plugin.create_extension_handlers()
