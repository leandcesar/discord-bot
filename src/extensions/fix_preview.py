import re

import disnake
from disnake_plugins import Plugin

from src.bot import Bot

plugin = Plugin[Bot]()

URL_REGEXES = {
    "instagram.com": re.compile(
        r"\b(?P<scheme>https?://)(?:www\.)?(?P<domain>instagram\.com)(?P<path>/[\w\.-]+/[\w\.-]+)"
    ),
    "twitter.com": re.compile(
        r"\b(?P<scheme>https?://)(?:www\.)?(?P<domain>twitter\.com)(?P<path>/[\w\.-]+/status/\d+)"
    ),
    "x.com": re.compile(r"\b(?P<scheme>https?://)(?:www\.)?(?P<domain>x\.com)(?P<path>/[\w\.-]+/status/\d+)"),
}

DOMAIN_REPLACEMENTS = {
    "instagram.com": "instagramez.com",
    "twitter.com": "fxtwitter.com",
    "x.com": "fxtwitter.com",
}


def find_and_replace_urls(text: str) -> list[str]:
    new_urls = []
    for domain, regex in URL_REGEXES.items():
        for match in regex.finditer(text):
            scheme = match.group("scheme")
            path = match.group("path")
            new_domain = DOMAIN_REPLACEMENTS[domain]
            new_urls.append(f"{scheme}{new_domain}{path}")
    return new_urls


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    urls = find_and_replace_urls(message.content)
    if not urls:
        return None
    content = "\n".join(urls)
    await message.edit(suppress_embeds=True)
    await plugin.bot.reply(message, content, mention_author=False)


setup, teardown = plugin.create_extension_handlers()
