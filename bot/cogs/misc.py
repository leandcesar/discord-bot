import disnake
from disnake.ext import commands
from disnake.i18n import Localized

from bot.cogs.stalker import ago
from bot.core import Bot


class Misc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name=Localized(key="COMMAND_UPTIME"), description=Localized("", key="COMMAND_UPTIME_DESC")
    )
    async def uptime(self, inter: disnake.GuildCommandInteraction) -> None:
        dt = ago(self.bot.init_time)
        days = dt.days
        hours, rem = divmod(dt.seconds, 3600)
        mins, secs = divmod(rem, 60)
        response = f"{days} days {hours:02d}:{mins:02d}:{secs:02d}"
        await inter.send(response)


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
