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


class Emote(disnake.Embed):
    def __init__(self, *, name: str, image: disnake.File) -> None:
        print(name)
        super().__init__(
            title=f"New Emote `{name}`",
            color=disnake.Colour.green(),
        )
        self.set_image(file=image)


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

    @commands.slash_command(name="emote", description="IDK")
    async def emote(
        self,
        inter: disnake.GuildCommandInteraction,
        name: str = commands.Param(name="nome", description="Nome do emote."),
        image: disnake.Attachment = commands.Param(name="emote", description="Emote image"),
    ) -> None:
        if not inter.permissions.manage_emojis:
            await inter.send("Erro! Você não tem permissão")
            return

        image_bin = await image.read()

        try:
            await inter.guild.create_custom_emoji(name=name, image=image_bin)
        except Exception as err:
            await inter.send(err)
        else:
            image_file = await image.to_file()
            await inter.send(embed=Emote(name=name, image=image_file))


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
