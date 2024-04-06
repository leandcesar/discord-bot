import disnake
from disnake.ext import commands
from disnake.i18n import Localized

from bot.services import pil


class Guild(commands.Cog):
    @commands.has_permissions(manage_emojis_and_stickers=True)
    @commands.slash_command(
        name=Localized(key="COMMAND_STICKER"),
        description=Localized("", key="COMMAND_STICKER_DESC"),
    )
    async def sticker(
        self,
        inter: disnake.GuildCommandInteraction,
        image: disnake.Attachment = commands.Param(
            name=Localized(key="ARG_IMAGE"),
            description=Localized("", key="ARG_IMAGE_DESC"),
        ),
        name: str = commands.Param(name=Localized(key="ARG_NAME"), description=Localized("", key="ARG_NAME_DESC")),
        emoji: str = commands.Param(
            name=Localized(key="ARG_EMOJI"),
            description=Localized("", key="ARG_EMOJI_DESC"),
        ),
    ) -> None:
        await inter.response.defer()
        image_binary = await image.read()
        image_binary = pil.resize_image(image_binary, size=(320, 320))
        file = disnake.File(fp=image_binary, filename="sticker.png")
        guild_sticker = await inter.guild.create_sticker(name=name, emoji=emoji, file=file)
        image_binary.close()
        file = await guild_sticker.to_file()
        await inter.edit_original_response(file=file)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Guild(bot))
