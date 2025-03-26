import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot
from src.components import buttons
from src.util import asset
from src.util.message import fetch_assets_content

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


@commands.has_permissions(manage_emojis_and_stickers=True)
@plugin.slash_command(name="emote")
async def emote_slash_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    Command for managing server custom emotes.

    Permissions
    ------------
    Requires the 'Manage Emojis and Stickers' permission.
    """


@emote_slash_command.sub_command(name="add")
async def emote_add_slash_command(
    inter: disnake.GuildCommandInteraction,
    name: str,
    attachment: disnake.Attachment,
) -> None:
    """
    Add a custom emote to the server.

    Parameters
    ----------
    name: The name to assign to the new custom emote.
    attachment: The image file that will be used as the custom emote.
    """
    await inter.response.defer()
    image = await attachment.read()
    guild_emoji = await inter.guild.create_custom_emoji(name=name, image=image)
    file = await guild_emoji.to_file()
    await inter.edit_original_response(f"`{name}`", file=file)


@emote_slash_command.sub_command(name="remove")
async def emote_remove_slash_command(inter: disnake.GuildCommandInteraction, name: str) -> None:
    """
    Remove a custom emote from the server.

    Parameters
    ----------
    name: The name of the custom emote you want to remove.
    """
    await inter.response.defer()
    guild_emoji = [emoji for emoji in inter.guild.emojis if name.casefold() == emoji.name.casefold()][0]
    file = await guild_emoji.to_file()
    view = buttons.DeleteView()
    message = await inter.edit_original_response(file=file, view=view)
    await view.wait()
    if view.value:
        emote = await guild_emoji.read()
        with asset.to_black_and_white(emote) as emote_bytes:
            file = disnake.File(emote_bytes, filename=f"{guild_emoji.name}.png")
            await guild_emoji.delete()
            await inter.send(file=file)
    await message.edit(view=None)


@emote_remove_slash_command.autocomplete("name")
async def emote_remove_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
    return [emoji for emoji in inter.guild.emojis if name.casefold() == emoji.name.casefold()][:25]


@emote_slash_command.sub_command(name="rename")
async def emote_rename_slash_command(inter: disnake.GuildCommandInteraction, name: str, new_name: str) -> None:
    """
    Rename a custom emote in the server.

    Parameters
    ----------
    name: The name of the custom emote you want to rename.
    new_name: The new name you want to assign to the custom emote.
    """
    await inter.response.defer()
    guild_emoji = [emoji for emoji in inter.guild.emojis if name.casefold() == emoji.name.casefold()][0]
    await guild_emoji.edit(name=new_name)
    file = await guild_emoji.to_file()
    await inter.edit_original_response(f"`{name}` -> `{new_name}`", file=file)


@emote_rename_slash_command.autocomplete("name")
async def emote_rename_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
    return [emoji for emoji in inter.guild.emojis if name.casefold() == emoji.name.casefold()][:25]


@commands.has_permissions(manage_emojis_and_stickers=True)
@plugin.message_command(name="Add media as emote")
async def emote_add_message_command(inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
    await inter.response.defer()
    datas = await fetch_assets_content(message)
    if datas:
        if len(datas) > 1:
            raise Exception(datas)  # TODO: add error message
        guild_emoji = await inter.guild.create_custom_emoji(name=str(message.id), image=datas[0])
        file = await guild_emoji.to_file()
        await inter.edit_original_response(file=file)
    else:
        await inter.edit_original_response("💨")


setup, teardown = plugin.create_extension_handlers()
