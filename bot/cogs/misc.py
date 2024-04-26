import disnake
from disnake.ext import commands
from disnake.i18n import Localized

from bot.core import Bot


class Uptime(disnake.Embed):
    def __init__(self, *, description: str, **kwargs) -> None:
        super().__init__(
            title="Uptime",
            description=description,
            color=disnake.Colour.light_gray(),
        )


class Misc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name=Localized(key="COMMAND_UPTIME"), description=Localized("", key="COMMAND_UPTIME_DESC")
    )
    async def uptime(self, inter: disnake.GuildCommandInteraction) -> None:
        locale_name = inter.locale.name.replace("_", "-")
        message = inter.bot.i18n.get(key="COMMAND_UPTIME_MESSAGE")[locale_name]
        timestamp = int(self.bot.init_time.timestamp())

        await inter.send(embed=Uptime(description=f"{message} <t:{timestamp}:R>"))


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
