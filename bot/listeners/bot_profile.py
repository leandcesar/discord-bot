import disnake
from disnake.ext import commands

from bot import Bot


class BotProfile(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_update(self, before: disnake.Guild, after: disnake.Guild) -> None:
        if before.icon != after.icon:
            avatar = after.icon.with_size(512).with_format("png")
            await self.bot.user.edit(avatar=avatar)
        if before.name != after.name:
            await after.me.edit(nick=after.name)


def setup(bot: Bot) -> None:
    bot.add_cog(BotProfile(bot))
