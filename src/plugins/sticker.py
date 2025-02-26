import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot
from src.components import buttons
from src.util import asset

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


@commands.has_permissions(manage_emojis_and_stickers=True)
@plugin.slash_command(name="sticker")
async def sticker_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    Command for managing server stickers.

    Permissions
    ------------
    Requires the 'Manage Emojis and Stickers' permission.
    """


@sticker_command.sub_command(name="add")
async def sticker_add_command(
    inter: disnake.GuildCommandInteraction,
    name: str,
    emoji: str,
    attachment: disnake.Attachment,
) -> None:
    """
    Add a new sticker to the server.

    Parameters
    ----------
    name: The name to assign to the new sticker.
    emoji: The emoji associated with the sticker.
    attachment: The image file that will be used as the sticker.
    """
    await inter.response.defer()
    sticker = await attachment.read()
    with asset.resize_asset(sticker, width=320, height=320) as sticker_bytes:
        file = disnake.File(sticker_bytes, filename=f"{name}.png")
        guild_sticker = await inter.guild.create_sticker(name=name, emoji=emoji, file=file)
        file = await guild_sticker.to_file()
        await inter.edit_original_response(file=file)


@sticker_command.sub_command(name="remove")
async def sticker_remove_command(inter: disnake.GuildCommandInteraction, sticker: disnake.GuildSticker) -> None:
    """
    Remove an sticker from the server.

    Parameters
    ----------
    sticker: The sticker to be removed from the server.
    """
    await inter.response.defer()
    guild_sticker = await inter.guild.fetch_sticker(sticker.id)
    file = await guild_sticker.to_file()

    view = buttons.Delete()
    message = await inter.edit_original_response(file=file, view=view)
    await view.wait()

    if view.value:
        sticker = await guild_sticker.read()
        with asset.to_black_and_white(sticker) as emote_bytes:
            file = disnake.File(emote_bytes, filename=f"{guild_sticker.name}.png")
            await guild_sticker.delete()
            await inter.send(file=file)

    await message.edit(view=None)


@sticker_remove_command.autocomplete("sticker")
async def sticker_remove_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
    return [sticker.name for sticker in inter.guild.stickers if name.casefold() in sticker.name.casefold()][:25]


setup, teardown = plugin.create_extension_handlers()
