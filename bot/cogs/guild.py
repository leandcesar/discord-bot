import disnake
from disnake.ext import commands

from bot.core import Bot
from bot.ext import Embed
from bot.services import pil


class Guild(commands.Cog):
    @commands.has_permissions(manage_emojis_and_stickers=True)
    @commands.slash_command()
    async def sticker(
        self, inter: disnake.GuildCommandInteraction, image: disnake.Attachment, name: str, emoji: str
    ) -> None:
        """
        Add a sticker to the server. {{STICKER}}

        Parameters
        ----------
        image: Image attachment {{IMAGE}}
        name: Name {{NAME}}
        emoji: Emoji {{EMOJI}}
        """
        await inter.response.defer()
        image_binary = await image.read()
        image_binary = pil.resize_image(image_binary, size=(320, 320))
        file = disnake.File(fp=image_binary, filename="sticker.png")
        guild_sticker = await inter.guild.create_sticker(name=name, emoji=emoji, file=file)
        image_binary.close()
        file = await guild_sticker.to_file()
        embed = Embed(inter, image={"file": file})
        await inter.edit_original_response(embed=embed)
        file.close()


def setup(bot: Bot) -> None:
    bot.add_cog(Guild(bot))
