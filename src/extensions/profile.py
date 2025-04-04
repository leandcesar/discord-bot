import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src.bot import Bot
from src.components.palette import Palette
from src.converters.emote import Emote
from src.converters.hex import HEX

plugin = Plugin[Bot]()


def member_has_color_role(inter: disnake.ApplicationCommandInteraction) -> bool:
    return inter.author.top_role != inter.guild.default_role


def member_has_badge_role(inter: disnake.ApplicationCommandInteraction) -> bool:
    return inter.author.top_role != inter.guild.default_role


def guild_has_role_icons(inter: disnake.ApplicationCommandInteraction) -> bool:
    return "ROLE_ICONS" in inter.guild.features


async def _color_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction,
    hex: HEX | None = None,
    attachment: disnake.Attachment | None = None,
) -> None:
    if hex:
        old_color = inter.author.color
        role = await inter.author.top_role.edit(color=disnake.Color(int(hex)))
        content = f"`{old_color}` -> `{role.color}`"
        await plugin.bot.reply(inter, content)
    else:
        if attachment is None:
            attachment = inter.author.display_avatar
        avatar = await attachment.read()
        palette = Palette.from_bytes(avatar)

        class Dropdown(disnake.ui.StringSelect):
            async def callback(self, inter: disnake.MessageInteraction) -> None:
                await inter.response.defer(ephemeral=True)
                hex = self.values[0]
                old_color = inter.author.color
                role = await inter.author.top_role.edit(color=disnake.Color(int(hex)))
                content = f"`{old_color}` -> `{role.color}`"
                await plugin.bot.reply(inter, content)

        view = disnake.ui.View()
        view.add_item(
            Dropdown(
                placeholder="Select a color...",
                options=[
                    disnake.SelectOption(label=f"{i}. #{color}", value=int(color))
                    for i, color in enumerate(palette.colors)
                ],
            )
        )
        with palette.draw() as palette_image:
            file = disnake.File(palette_image, filename="palette.png")
            await plugin.bot.reply(inter, file=file, view=view)


@commands.check(member_has_color_role)
@plugin.command(name="color", aliases=["cor"])
async def color_prefix_command(
    ctx: commands.Context[Bot],
    hex: HEX | None = None,
) -> None:
    await _color_command(ctx, hex=hex)


@commands.check(member_has_color_role)
@plugin.slash_command(name="color")
async def color_slash_command(
    inter: disnake.ApplicationCommandInteraction,
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
    await _color_command(inter, hex=hex, attachment=attachment)


@color_slash_command.autocomplete("hex")
async def color_autocomplete(inter: disnake.ApplicationCommandInteraction, value: str) -> list[str]:
    value = value.removeprefix("#")
    colors: list[str] = [HEX.random() for _ in range(25)]
    if 0 < len(value) <= 6 and all(c in "0123456789ABCDEFabcdef" for c in value):
        colors = list(set([f"#{value}{color[len(value) + 1:]}" for color in colors]))
    return sorted(colors)


async def _badge_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction,
    *,
    emote: Emote | None = None,
    attachment: disnake.Attachment | None = None,
) -> None:
    if emote and emote.is_unicode_emoji():
        role = await inter.author.top_role.edit(icon=None, emoji=emote.name)
    elif emote and emote.is_custom_emoji():
        icon = await emote.read()
        role = await inter.author.top_role.edit(icon=icon, emoji=None)
    elif attachment:
        icon = await attachment.read()
        role = await inter.author.top_role.edit(icon=icon, emoji=None)
    else:
        role = inter.author.top_role
    if role.emoji:
        await plugin.bot.reply(inter, role.emoji)
    elif role.icon:
        file = await role.icon.to_file()
        await plugin.bot.reply(inter, file=file)


@commands.check(member_has_badge_role)
@commands.check(guild_has_role_icons)
@plugin.command(name="badge")
async def badge_prefix_command(
    ctx: commands.Context[Bot],
    emote: Emote | None = None,
) -> None:
    attachment = ctx.message.attachments[0] if ctx.message.attachments else None
    await _badge_command(ctx, emote=emote, attachment=attachment)


@commands.check(member_has_badge_role)
@commands.check(guild_has_role_icons)
@plugin.slash_command(name="badge")
async def badge_slash_command(
    inter: disnake.ApplicationCommandInteraction,
    emote: Emote | None = None,
    attachment: disnake.Attachment | None = None,
) -> None:
    """
    Change your badge on the server.

    Parameters
    ----------
    emote: The emoji (or emote) to set as your badge.
    attachment: An image file to use as the badge.
    """
    await inter.response.defer(ephemeral=True)
    await _badge_command(inter, emote=emote, attachment=attachment)


setup, teardown = plugin.create_extension_handlers()
