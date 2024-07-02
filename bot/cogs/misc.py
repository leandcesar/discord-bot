import disnake
from disnake.ext import commands

from bot import Bot
from bot.ext import Embed


class Misc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.slash_command()
    async def uptime(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Check how long the bot has been online. {{UPTIME}}
        """
        timestamp = int(self.bot.started_at.timestamp())
        embed = Embed.from_interaction(inter, description=f"<t:{timestamp}:R>")
        await inter.send(embed=embed, ephemeral=True)


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
