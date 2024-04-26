import disnake
from disnake.ext import commands

from bot.core import Bot


class Uptime(disnake.Embed):
    def __init__(self, *, description: str, **kwargs) -> None:
        super().__init__(
            title="Uptime",
            description=description,
            color=disnake.Colour.light_gray(),
        )


class Misc(commands.Cog):
    @commands.slash_command()
    async def uptime(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Check how long the bot has been online. {{UPTIME}}
        """
        locale_name = inter.locale.name.replace("_", "-")
        message = inter.bot.i18n.get(key="UPTIME_MESSAGE")[locale_name]
        timestamp = int(inter.bot.init_time.timestamp())
        await inter.send(embed=Uptime(description=f"{message} <t:{timestamp}:R>"))


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
