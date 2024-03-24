# -*- coding: utf-8 -*-
import disnake
from disnake.ext import commands

from bot.core.webhook import get_or_create_webhook
from bot.services import pil


class RoleplayCog(commands.Cog):
    @commands.slash_command(name="metadinha", description="faça metadinha com alguém")
    async def command_match(
        self,
        inter: disnake.GuildCommandInteraction,
        member: disnake.Member = commands.Param(name="usuário", description="usuário pra fazer metadinha"),
        vertical: bool
        | None = commands.Param(None, name="vertical", description="a metadinha deve ser na vertical?"),
        reverse: bool
        | None = commands.Param(None, name="invertido", description="a sua foto deve vir depois da do usuário?"),
    ) -> None:
        await inter.response.defer()
        image_1_binary = await inter.author.display_avatar.with_size(512).with_format("png").read()
        image_2_binary = await member.display_avatar.with_size(512).with_format("png").read()
        if reverse:
            image_1_binary, image_2_binary = image_2_binary, image_1_binary
        try:
            if vertical:
                image_binary = pil.merge_images_vertical(image_1_binary, image_2_binary)
            else:
                image_binary = pil.merge_images_horizontal(image_1_binary, image_2_binary)
            file = disnake.File(fp=image_binary, filename="metadinha.png")
            await inter.edit_original_response(file=file)
        finally:
            image_binary.close()

    @commands.cooldown(rate=3, per=30)
    @commands.slash_command(name="fake", description="finja ser algo ou alguém")
    async def command_message(
        self,
        inter: disnake.GuildCommandInteraction,
        content: str = commands.Param(name="mensagem", description="mensagem para enviar fingindo ser alguém"),
        member: disnake.Member | None = commands.Param(None, name="usuário", description="usuário para fingir ser"),
        name: str | None = commands.Param(None, name="nome", description="nome de quem quer fingir ser"),
        image: disnake.Attachment
        | None = commands.Param(None, name="imagem", description="imagem de quem quer fingir ser"),
    ) -> None:
        if not (member or (name and image)):
            return await inter.send(
                "defina o **usuário** ou o **nome** e **imagem** de quem quer fingir ser", ephemeral=True
            )
        await inter.response.defer(ephemeral=True)
        if member:
            name = member.display_name
            image = member.display_avatar
        avatar_url = image.url if image else None
        webhook = await get_or_create_webhook(inter)
        message = await webhook.send(content, username=name, avatar_url=avatar_url, wait=True)
        await inter.edit_original_response(message.jump_url)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(RoleplayCog(bot))
