import disnake
from disnake.ext import commands
from disnake.ext.commands.errors import MissingRequiredArgument
from disnake_plugins import Plugin

from src.bot import Bot
from src.components import buttons
from src.util import asset
from src.util.message import fetch_assets_content

plugin = Plugin[Bot]()


@commands.has_permissions(manage_emojis_and_stickers=True)
@plugin.slash_command(name="sticker")
async def sticker_slash_command(inter: disnake.ApplicationCommandInteraction) -> None:
    """
    Command for managing server stickers.

    Permissions
    ------------
    Requires the 'Manage Emojis and Stickers' permission.
    """


@sticker_slash_command.sub_command(name="add")
async def sticker_add_slash_command(
    inter: disnake.ApplicationCommandInteraction,
    name: str,
    emoji: str,
    attachment: disnake.Attachment,
) -> None:
    """
    Add a sticker to the server.

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
        await plugin.bot.reply(inter, f"`{name}`", file=file)


@sticker_slash_command.sub_command(name="remove")
async def sticker_remove_slash_command(inter: disnake.ApplicationCommandInteraction, name: str) -> None:
    """
    Remove a sticker from the server.

    Parameters
    ----------
    name: The name of the sticker you want to remove.
    """
    await inter.response.defer()
    guild_sticker = [sticker for sticker in inter.guild.stickers if name.casefold() == sticker.name.casefold()][0]
    file = await guild_sticker.to_file()
    view = buttons.DeleteView()
    message = await plugin.bot.reply(inter, file=file, view=view)
    await view.wait()
    if view.value:
        sticker = await guild_sticker.read()
        with asset.to_black_and_white(sticker) as emote_bytes:
            file = disnake.File(emote_bytes, filename=f"{guild_sticker.name}.png")
            await guild_sticker.delete()
            await plugin.bot.reply(inter, file=file)
    await message.edit(view=None)


@sticker_remove_slash_command.autocomplete("name")
async def sticker_remove_autocomplete(self, inter: disnake.ApplicationCommandInteraction, name: str) -> list[str]:
    return [sticker.name for sticker in inter.guild.stickers if name.casefold() in sticker.name.casefold()][:25]


@sticker_slash_command.sub_command(name="rename")
async def sticker_rename_slash_command(
    inter: disnake.ApplicationCommandInteraction, name: str, new_name: str
) -> None:
    """
    Rename a sticker in the server.

    Parameters
    ----------
    name: The name of the sticker you want to rename.
    new_name: The new name you want to assign to the sticker.
    """
    await inter.response.defer()
    guild_sticker = [sticker for sticker in inter.guild.stickers if name.casefold() == sticker.name.casefold()][0]
    await guild_sticker.edit(name=new_name)
    file = await guild_sticker.to_file()
    await plugin.bot.reply(inter, f"`{name}` -> `{new_name}`", file=file)


@sticker_rename_slash_command.autocomplete("name")
async def sticker_rename_autocomplete(self, inter: disnake.ApplicationCommandInteraction, name: str) -> list[str]:
    return [sticker.name for sticker in inter.guild.stickers if name.casefold() in sticker.name.casefold()][:25]


@commands.has_permissions(manage_emojis_and_stickers=True)
@plugin.message_command(name="Add media as sticker")
async def sticker_add_message_command(inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
    await inter.response.defer()
    datas = await fetch_assets_content(message)
    if datas:
        for data in datas:
            with asset.resize_asset(data, width=320, height=320) as sticker_bytes:
                file = disnake.File(sticker_bytes, filename=f"{message.id}.png")
                guild_sticker = await inter.guild.create_sticker(name=str(message.id), emoji="❓", file=file)
                file = await guild_sticker.to_file()
                await plugin.bot.reply(inter, file=file)
    else:
        raise MissingRequiredArgument("No media found in the message.")


setup, teardown = plugin.create_extension_handlers()
