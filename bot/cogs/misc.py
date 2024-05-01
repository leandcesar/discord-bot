import disnake
from disnake.ext import commands

from bot.core import Bot
from bot.ext import Embed


class Misc(commands.Cog):
    @commands.slash_command()
    async def uptime(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Check how long the bot has been online. {{UPTIME}}
        """
        await inter.response.defer()
        message = inter.bot.localized("UPTIME_MESSAGE", locale=inter.locale)
        description = message.format(timestamp=f"<t:{inter.bot.init_timestamp}:R>")
        embed = Embed(inter, description=description)
        await inter.edit_original_response(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
