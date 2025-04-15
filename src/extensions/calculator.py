import disnake
from disnake_plugins import Plugin

from src.bot import Bot

plugin = Plugin[Bot]()


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    content = message.content.lower().replace(" ", "").replace(",", ".").replace("^", "**").replace("x", "*")
    if not all(char in "0123456789+-/*^()." for char in content):
        return None
    if not any(char in "0123456789" for char in content):
        return None
    content = eval(content)  # nosec # noqa: S307
    if message.content == str(content):
        return None
    await plugin.bot.reply(message, content, mention_author=False)


setup, teardown = plugin.create_extension_handlers()
