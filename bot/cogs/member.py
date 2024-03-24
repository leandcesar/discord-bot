# -*- coding: utf-8 -*-
import disnake
from disnake.ext import commands

from bot.services import imagga, pil


class Dropdown(disnake.ui.StringSelect):
    def __init__(self, *, callback, **kwargs) -> None:
        self._callback = callback
        super().__init__(**kwargs)

    async def callback(self, inter: disnake.MessageInteraction) -> None:
        hex_code = self.values[0].split(" ", maxsplit=2)[1]
        return await self._callback(inter, hex_code)


async def author_has_role(inter: disnake.ApplicationCommandInteraction) -> bool:
    return inter.author.top_role != inter.guild.default_role


async def update_author_color(inter: disnake.ApplicationCommandInteraction, hex_code: str) -> None:
    int_code = int(hex_code.strip("#"), 16)
    color = disnake.Color(int_code)
    old_color = inter.author.color
    role = await inter.author.top_role.edit(color=color)
    return await inter.send(f"`{old_color}` -> `{role.color}`")


@commands.check(author_has_role)
class MemberCog(commands.Cog):
    @commands.slash_command(name="cor", description="edite sua cor")
    async def command_color(
        self,
        inter: disnake.ApplicationCommandInteraction,
        hex_code: str | None = commands.Param(None, name="hex", description="código HEX da cor desejada"),
        image: disnake.Attachment
        | None = commands.Param(None, name="imagem", description="imagem pra extrair a paleta de cores"),
    ) -> None:
        if hex_code:
            return await update_author_color(inter, hex_code)
        await inter.response.defer()
        if not image:
            image = inter.author.display_avatar.with_size(512).with_format("png")
        image_binary = await image.read()
        colors = await imagga.get_colors_from_image(image_binary)
        view = disnake.ui.View()
        dropdown = Dropdown(
            callback=update_author_color,
            placeholder="escolha sua cor...",
            options=[
                disnake.SelectOption(label="{0}. {1} ({2})".format(i, color["hex"], color["name"]))
                for i, color in enumerate(colors, start=1)
            ],
        )
        view.add_item(dropdown)
        try:
            image_binary = pil.create_image_from_rgb_colors([color["rgb"] for color in colors])
            file = disnake.File(fp=image_binary, filename="cores.png")
            await inter.edit_original_response(f"cor atual: `{inter.author.color}`", file=file, view=view)
        finally:
            image_binary.close()

    @commands.slash_command(name="emblema", description="edite seu emblema")
    async def command_badge(
        self,
        inter: disnake.ApplicationCommandInteraction,
        emote: disnake.PartialEmoji
        | None = commands.Param(None, name="emote", description="emote pra adicionar como emblema"),
        image: disnake.Attachment
        | None = commands.Param(None, name="imagem", description="imagem pra adicionar como emblema"),
    ) -> None:
        if not emote and not image:
            return await inter.send("envie um **emote** ou uma **imagem**", ephemeral=True)
        await inter.response.defer()
        icon = emote or image
        role = await inter.author.top_role.edit(icon=icon)
        file = await role.icon.to_file()
        await inter.edit_original_response(file=file)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(MemberCog(bot))
