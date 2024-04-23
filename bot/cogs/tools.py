import re

import disnake
from disnake.ext import commands

from bot.core import Bot

REGEX_INSTAGRAM_URL = re.compile(r"https?://(?:www\.)?instagram\.com/\S+")
REGEX_TIKTOK_URL = re.compile(r"https?://(?:www\.|vm\.)?tiktok\.com/\S+")
REGEX_TWITTER_URL = re.compile(r"https?://(?:www\.)?twitter\.com/\S+")
REPLACE_INSTAGRAM_URL = ("instagram.com", "ddinstagram.com")
REPLACE_TIKTOK_URL = ("tiktok.com", "vxtiktok.com")
REPLACE_TWITTER_URL = ("twitter.com", "fxtwitter.com")


class Tools(commands.Cog):
    async def fix_embeds_url(self, message: disnake.Message) -> None:
        instagram_urls: list[str] = REGEX_INSTAGRAM_URL.findall(message.content)
        tiktok_urls: list[str] = REGEX_TIKTOK_URL.findall(message.content)
        twitter_urls: list[str] = REGEX_TWITTER_URL.findall(message.content)
        if not instagram_urls and not tiktok_urls and not twitter_urls:
            return None
        fix_instagram_urls = [instagram_url.replace(*REPLACE_INSTAGRAM_URL) for instagram_url in instagram_urls]
        fix_tiktok_urls = [tiktok_url.replace(*REPLACE_TIKTOK_URL) for tiktok_url in tiktok_urls]
        fix_twitter_urls = [twitter_url.replace(*REPLACE_TWITTER_URL) for twitter_url in twitter_urls]
        content = "\n".join(fix_instagram_urls + fix_tiktok_urls + fix_twitter_urls)
        await message.reply(content, mention_author=False)
        await message.edit(suppress_embeds=True)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot or not message.content:
            return None
        await self.fix_embeds_url(message)


def setup(bot: Bot) -> None:
    bot.add_cog(Tools(bot))
