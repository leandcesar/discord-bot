# -*- coding: utf-8 -*-
import disnake
from disnake.ext import commands

from bot.services import pil


class GuildCog(commands.Cog):
    @commands.has_permissions(manage_emojis_and_stickers=True)
    @commands.slash_command(name="figurinha", description="adicione uma figurinha")
    async def command_sticker(
        self,
        inter: disnake.ApplicationCommandInteraction,
        image: disnake.Attachment = commands.Param(name="imagem", description="imagem pra adicionar como figurinha"),
        name: str = commands.Param(name="nome", description="nome da figurinha"),
        emoji: str = commands.Param(name="emoji", description="emoji pra representar a figurinha"),
    ) -> None:
        await inter.response.defer()
        image_binary = await image.read()
        image_binary = pil.resize_image(image_binary, size=(320, 320))
        try:
            file = disnake.File(fp=image_binary, filename="figurinha.png")
            sticker = await inter.guild.create_sticker(name=name, emoji=emoji, file=file)
        finally:
            image_binary.close()
        file = await sticker.to_file()
        await inter.edit_original_response(file=file)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(GuildCog(bot))
