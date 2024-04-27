from enum import Enum

import disnake
from disnake.ext import commands
from disnake.i18n import Localized

from bot.core import Bot

# Source: https://discord.com/blog/beginners-guide-to-custom-emojis#heading-4
MAX_IMAGE_BYTES_SIZE = 256 * 1000
NO_PERM_GIF = "https://media1.tenor.com/m/8wwLg1lZS_gAAAAC/denied-incredibles.gif"
LARGE_GIF = "https://media1.tenor.com/m/SGCLBFPTK4sAAAAC/im-big-boned-eric-cartman.gif"


class Uptime(disnake.Embed):
    def __init__(self, *, description: str, **kwargs) -> None:
        super().__init__(
            title="Uptime",
            description=description,
            color=disnake.Colour.light_gray(),
        )


class Emote(disnake.Embed):
    def __init__(
        self,
        *,
        name: str,
        image: disnake.File,
        inter: disnake.GuildCommandInteraction,
    ) -> None:
        locale = inter.locale.name.replace("_", "-")
        title = inter.bot.i18n.get(key="COMMAND_EMOTE_TITLE")[locale]
        title = title.format(name)

        super().__init__(
            title=title,
            color=disnake.Colour.green(),
        )
        self.set_image(file=image)


class EmoteErrorEnum(Enum):
    WITHOUT_PERMISSION = 1
    LARGE_IMAGE = 2


class EmoteError(disnake.Embed):
    def __init__(
        self,
        *,
        name: str,
        err_enum: EmoteErrorEnum,
        inter: disnake.GuildCommandInteraction,
    ) -> None:
        locale = inter.locale.name.replace("_", "-")
        gif_error = None
        description = "IDK"

        title = inter.bot.i18n.get(key="COMMAND_EMOTE_ERR_TITLE")[locale]
        title = title.format("name")

        match err_enum:
            case EmoteErrorEnum.WITHOUT_PERMISSION:
                gif_error = NO_PERM_GIF
                description = inter.bot.i18n.get(key="COMMAND_EMOTE_ERR_WITHOUT_PERM")[locale]

            case EmoteErrorEnum.LARGE_IMAGE:
                gif_error = LARGE_GIF
                description = inter.bot.i18n.get(key="COMMAND_EMOTE_ERR_LARGE_IMAGE")[locale].format(
                    "https://discord.com/blog/beginners-guide-to-custom-emojis#heading-4"
                )

        super().__init__(
            title=title,
            description=description,
            color=disnake.Colour.red(),
        )

        self.set_image(url=gif_error)


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

    @commands.slash_command(name=Localized(key="COMMAND_EMOTE"), description=Localized(key="COMMAND_EMOTE_DESC"))
    async def emote(
        self,
        inter: disnake.GuildCommandInteraction,
        name: str = commands.Param(
            name=Localized(key="COMMAND_EMOTE_ARG_NAME"), description=Localized(key="COMMAND_EMOTE_ARG_NAME_DESC")
        ),
        image: disnake.Attachment = commands.Param(
            name=Localized(key="COMMAND_EMOTE_ARG_IMAGE"), description=Localized(key="COMMAND_EMOTE_ARG_IMAGE_DESC")
        ),
    ) -> None:
        if not inter.permissions.manage_emojis:
            await inter.send(embed=EmoteError(name=name, err_enum=EmoteErrorEnum.WITHOUT_PERMISSION, inter=inter))
            return

        if image.size >= MAX_IMAGE_BYTES_SIZE:
            await inter.send(embed=EmoteError(name=name, err_enum=EmoteErrorEnum.LARGE_IMAGE, inter=inter))
            return

        image_bin = await image.read()
        emote = None

        try:
            emote = await inter.guild.create_custom_emoji(name=name, image=image_bin)
        except Exception as err:
            await inter.send(err)
        else:
            image_file = await image.to_file()
            await inter.send(embed=Emote(name=emote.name, image=image_file, inter=inter))


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
