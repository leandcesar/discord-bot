import re
from functools import reduce

import disnake
from disnake_plugins import Plugin

from src.bot import Bot

plugin = Plugin[Bot]()

INSTAGRAM_URL_REGEX = re.compile(r"https?://(?:www\.)?instagram\.com/\S+/\S+")
TWITTER_URL_REGEX = re.compile(r"https?://(?:www\.)?twitter\.com/\S+status/\S+")
X_URL_REGEX = re.compile(r"https?://(?:www\.)?x\.com/\S+status/\S+")


def find_urls(text: str) -> list[str]:
    urls = []
    for regex in (INSTAGRAM_URL_REGEX, TWITTER_URL_REGEX, X_URL_REGEX):
        urls.extend(regex.findall(text))
    return urls


def replace_all(texts: list[str], *olds_news: tuple[str, str]) -> list[str]:
    return [reduce(lambda t, pair: t.replace(*pair), olds_news, text) for text in texts]


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    content = message.content
    urls = find_urls(content)
    if not urls:
        return None
    urls = replace_all(urls, ("instagram.com", "instagramez.com"), ("twitter", "fxtwitter"), ("x", "fxtwitter"))
    content = "\n".join(urls)
    await message.edit(suppress_embeds=True)
    await plugin.bot.reply(message, content)


setup, teardown = plugin.create_extension_handlers()
