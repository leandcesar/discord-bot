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
@plugin.slash_command(name="emote")
async def emote_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    Command for managing server emotes.

    Permissions
    ------------
    Requires the 'Manage Emojis and Stickers' permission.
    """


@emote_command.sub_command(name="add")
async def emote_add_command(
    inter: disnake.GuildCommandInteraction,
    name: str,
    attachment: disnake.Attachment,
) -> None:
    """
    Add a new emote to the server.

    Parameters
    ----------
    name: The name to assign to the new emote.
    attachment: The image file that will be used as the emote.
    """
    await inter.response.defer()
    emote = await attachment.read()
    guild_emote = await inter.guild.create_custom_emoji(name=name, image=emote)
    file = await guild_emote.to_file()
    await inter.edit_original_response(file=file)


@emote_command.sub_command(name="remove")
async def emote_remove_command(inter: disnake.GuildCommandInteraction, emote: disnake.Emoji) -> None:
    """
    Remove an emote from the server.

    Parameters
    ----------
    emote: The emote to be removed from the server.
    """
    await inter.response.defer()
    guild_emote = await inter.guild.fetch_emoji(emote.id)
    file = await guild_emote.to_file()

    view = buttons.Delete()
    message = await inter.edit_original_response(file=file, view=view)
    await view.wait()

    if view.value:
        emote = await guild_emote.read()
        with asset.to_black_and_white(emote) as emote_bytes:
            file = disnake.File(emote_bytes, filename=f"{guild_emote.name}.png")
            await guild_emote.delete()
            await inter.send(file=file)

    await message.edit(view=None)


@emote_remove_command.autocomplete("emote")
async def emote_remove_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
    return [emote.name for emote in inter.guild.emojis if name.casefold() in emote.name.casefold()][:25]


setup, teardown = plugin.create_extension_handlers()
