import re

import disnake
from disnake.ext import commands

from bot.core import Bot
from bot.services import tiktok


def find_all_twitter_urls(text: str) -> list[str]:
    return re.findall(r"https?://(?:www\.)?twitter\.com/\S+", text)


def find_all_tiktok_urls(text: str) -> list[str]:
    return re.findall(r"https?://(?:www\.|vm\.)?tiktok\.com/\S+", text)


class Events(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot or not message.content:
            return None
        for twitter_url in find_all_twitter_urls(message.content):
            content = twitter_url.replace("twitter.com", "fxtwitter.com")
            await message.reply(content, mention_author=False)
            await message.edit(suppress_embeds=True)
            return None  # only first to prevent spam
        for tiktok_url in find_all_tiktok_urls(message.content):
            video_binary = await tiktok.download_video(tiktok_url)
            if video_binary:
                file = disnake.File(fp=video_binary, filename="video.mp4")
                await message.reply(file=file, mention_author=False)
                await message.edit(suppress_embeds=True)
                video_binary.close()
                return None  # only first to prevent spam


def setup(bot: Bot) -> None:
    bot.add_cog(Events(bot))
