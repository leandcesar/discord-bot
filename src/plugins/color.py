import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot
from src.components.palette import Palette
from src.types.color import HEX

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


def member_has_color_role(inter: disnake.GuildCommandInteraction) -> bool:
    return inter.author.top_role != inter.guild.default_role


@commands.check(member_has_color_role)
@plugin.slash_command(name="color")
async def color_command(
    inter: disnake.GuildCommandInteraction,
    hex: HEX | None = None,
    attachment: disnake.Attachment = commands.Param(lambda inter: inter.author.display_avatar),
) -> None:
    """
    Change the color of your username on the server.

    Parameters
    ----------
    hex: The HEX code representing the color to change to.
    attachment: An image attachment to extract colors from (default: user's avatar).
    """
    await inter.response.defer(ephemeral=True)
    if hex:
        old_color = inter.author.color
        role = await inter.author.top_role.edit(color=disnake.Color(int(hex)))
        await inter.edit_original_response(f"`{old_color}` -> `{role.color}`")
    else:
        avatar = await attachment.read()
        palette = Palette.from_bytes(avatar)

        class Dropdown(disnake.ui.StringSelect):
            async def callback(self, inter: disnake.MessageInteraction) -> None:
                await inter.response.defer(ephemeral=True)
                old_color = inter.author.color
                hex = self.values[0]
                role = await inter.author.top_role.edit(color=disnake.Color(int(hex)))
                await inter.edit_original_response(f"`{old_color}` -> `{role.color}`")

        view = disnake.ui.View()
        view.add_item(
            Dropdown(
                placeholder="Select a color...",
                options=[
                    disnake.SelectOption(label=f"{i}. #{color.hex}", value=int(color.hex))
                    for i, color in enumerate(palette.colors)
                ],
            )
        )

        with palette.draw() as palette_image:
            file = disnake.File(palette_image, filename="palette.png")
            await inter.edit_original_response(file=file, view=view)


@color_command.autocomplete("hex")
async def color_autocomplete(inter: disnake.GuildCommandInteraction, value: str) -> list[str]:
    value = value.removeprefix("#")
    colors: list[str] = [HEX.random() for _ in range(25)]
    if 0 < len(value) <= 6 and all(c in "0123456789ABCDEFabcdef" for c in value):
        colors = list(set([f"#{value}{color[len(value) + 1:]}" for color in colors]))
    return sorted(colors)


setup, teardown = plugin.create_extension_handlers()
