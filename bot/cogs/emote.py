from enum import Enum

import aiohttp
import disnake
from disnake.ext import commands
from disnake.i18n import Localized

from bot.core import Bot
from bot.services import pil

# Source: https://discord.com/blog/beginners-guide-to-custom-emojis#heading-4
MAX_IMAGE_BYTES_SIZE = 256 * 1000
NO_PERM_GIF = "https://media1.tenor.com/m/8wwLg1lZS_gAAAAC/denied-incredibles.gif"
LARGE_GIF = "https://media1.tenor.com/m/SGCLBFPTK4sAAAAC/im-big-boned-eric-cartman.gif"
CHOOSE_GIF = "https://media1.tenor.com/m/3C4bAf7b8C0AAAAC/the-matrix-morpheus.gif"


class EmoteEmbed(disnake.Embed):
    def __init__(
        self,
        *,
        name: str,
        image: disnake.File,
        inter: disnake.GuildCommandInteraction,
    ) -> None:
        locale = inter.locale.name.replace("_", "-")
        title = inter.bot.i18n.get(key="COMMAND_EMOTE_ADD_TITLE")[locale]
        title = title.format(name)

        super().__init__(
            title=title,
            color=disnake.Colour.green(),
        )
        self.set_image(file=image)


class EmoteErrorEnum(Enum):
    WITHOUT_PERMISSION = 1
    LARGE_IMAGE = 2
    NO_EMOTE_ARGS = 3


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

        title = inter.bot.i18n.get(key="COMMAND_EMOTE_ADD_ERR_TITLE")[locale]
        title = title.format(name)

        match err_enum:
            case EmoteErrorEnum.WITHOUT_PERMISSION:
                gif_error = NO_PERM_GIF
                description = inter.bot.i18n.get(key="COMMAND_EMOTE_ADD_ERR_WITHOUT_PERM")[locale]

            case EmoteErrorEnum.LARGE_IMAGE:
                gif_error = LARGE_GIF
                description = inter.bot.i18n.get(key="COMMAND_EMOTE_ADD_ERR_LARGE_IMAGE")[locale].format(
                    "https://discord.com/blog/beginners-guide-to-custom-emojis#heading-4"
                )

            case EmoteErrorEnum.NO_EMOTE_ARGS:
                gif_error = CHOOSE_GIF
                description = "USE UM DOS DOIS ARGUMENTOS OPCIONAIS"

        super().__init__(
            title=title,
            description=description,
            color=disnake.Colour.red(),
        )

        self.set_image(url=gif_error)


class Emote(disnake.Embed):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.slash_command(name=Localized(key="COMMAND_EMOTE"), description=Localized(key="COMMAND_EMOTE_DESC"))
    async def emote(
        self,
        inter: disnake.GuildCommandInteraction,
    ):
        pass

    @emote.sub_command(name=Localized(key="COMMAND_EMOTE_ADD"), description=Localized(key="COMMAND_EMOTE_ADD_DESC"))
    async def emote_add(
        self,
        inter: disnake.GuildCommandInteraction,
        name: str = commands.Param(
            name=Localized(key="COMMAND_EMOTE_ADD_ARG_NAME"),
            description=Localized(key="COMMAND_EMOTE_ADD_ARG_NAME_DESC"),
        ),
        url: str
        | None = commands.Param(
            None,
            name="url",  # Localized(key="COMMAND_EMOTE_ADD_ARG_URL"),
            description="url",  # Localized(key="COMMAND_EMOTE_ADD_ARG_URL_DESC"),
        ),
        image: disnake.Attachment
        | None = commands.Param(
            None,
            name=Localized(key="COMMAND_EMOTE_ADD_ARG_IMAGE"),
            description=Localized(key="COMMAND_EMOTE_ADD_ARG_IMAGE_DESC"),
        ),
    ) -> None:
        image_bin = None
        if not inter.permissions.manage_emojis:
            await inter.send(embed=EmoteError(name=name, err_enum=EmoteErrorEnum.WITHOUT_PERMISSION, inter=inter))
            return

        if url is not None:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    image_bin = await response.read()

                    image_bytes = pil.save_image(pil.open_image(image_bin))
                    image_file = disnake.File(fp=image_bytes, filename="tmp.png")
        elif image is not None:
            image_file = await image.to_file()
        else:
            await inter.send(embed=EmoteError(name=name, err_enum=EmoteErrorEnum.NO_EMOTE_ARGS, inter=inter))
            return

        if image_file.bytes_length >= MAX_IMAGE_BYTES_SIZE:
            await inter.send(embed=EmoteError(name=name, err_enum=EmoteErrorEnum.LARGE_IMAGE, inter=inter))
            return

        emote = None
        try:
            emote = await inter.guild.create_custom_emoji(name=name, image=image_bin)
        except Exception as err:
            await inter.send(err)
        else:
            await inter.send(embed=EmoteEmbed(name=emote.name, image=image_file, inter=inter))


def setup(bot: Bot) -> None:
    bot.add_cog(Emote(bot))
