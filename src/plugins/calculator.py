import re

import disnake
from disnake_plugins import Plugin

from src import log
from src.bot import Bot

PATTERN = r"^\s*\d+(\s*[\+\-\*/\^]\s*\(*\d+\)*\s*)*\s*$"
REGEX = re.compile(PATTERN)

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    if not REGEX.match(message.content):
        return None
    try:
        result = eval(message.content.replace("^", "**"))  # nosec # noqa: S307
    except Exception as e:
        logger.error(
            f"{message.guild} ({message.guild.id}) "
            f"#{message.channel} ({message.channel.id}) "
            f"@{message.author} ({message.author.id}): "
            f"{message.content!r} ({message.id}) "
            f"{e}"
        )
        return None
    if message.content == str(result):
        return None
    logger.info(
        f"{message.guild} ({message.guild.id}) "
        f"#{message.channel} ({message.channel.id}) "
        f"@{message.author} ({message.author.id}): "
        f"{message.content!r} ({message.id}) "
        f"= {result!r}"
    )
    await message.reply(result, mention_author=False)


setup, teardown = plugin.create_extension_handlers()
