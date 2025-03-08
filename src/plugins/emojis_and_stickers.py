import re

import aiohttp
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
@plugin.slash_command(name="emoji")
async def emoji_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    Command for managing server emojis.

    Permissions
    ------------
    Requires the 'Manage Emojis and Stickers' permission.
    """


@emoji_command.sub_command(name="add")
async def emoji_add_command(
    inter: disnake.GuildCommandInteraction,
    name: str,
    attachment: disnake.Attachment,
) -> None:
    """
    Add a new emoji to the server.

    Parameters
    ----------
    name: The name to assign to the new emoji.
    attachment: The image file that will be used as the emoji.
    """
    await inter.response.defer()
    emoji = await attachment.read()
    guild_emoji = await inter.guild.create_custom_emoji(name=name, image=emoji)
    file = await guild_emoji.to_file()
    await inter.edit_original_response(file=file)


@emoji_command.sub_command(name="remove")
async def emoji_remove_command(inter: disnake.GuildCommandInteraction, emoji_name: str) -> None:
    """
    Remove an emoji from the server.

    Parameters
    ----------
    emoji: The emoji (or emote) to be removed from the server.
    """
    await inter.response.defer()
    guild_emoji = [emoji for emoji in inter.guild.emojis if emoji_name.casefold() == emoji.name.casefold()][0]
    file = await guild_emoji.to_file()
    view = buttons.Delete()
    message = await inter.edit_original_response(file=file, view=view)
    await view.wait()
    if view.value:
        emoji = await guild_emoji.read()
        with asset.to_black_and_white(emoji) as emoji_bytes:
            file = disnake.File(emoji_bytes, filename=f"{guild_emoji.name}.png")
            await guild_emoji.delete()
            await inter.send(file=file)
    await message.edit(view=None)


@emoji_remove_command.autocomplete("emoji_name")
async def emoji_remove_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
    return [emoji.name for emoji in inter.guild.emojis if name.casefold() in emoji.name.casefold()][:25]


@emoji_command.sub_command(name="rename")
async def emoji_rename_command(inter: disnake.GuildCommandInteraction, emoji_name: str, name: str) -> None:
    """
    Rename an emoji from the server.

    Parameters
    ----------
    emoji: The emoji (or emote) to be renamed from the server.
    name: The new emoji (or emote) name.
    """
    await inter.response.defer()
    guild_emoji = [emoji for emoji in inter.guild.emojis if emoji_name.casefold() == emoji.name.casefold()][0]
    await guild_emoji.edit(name=name)
    file = await guild_emoji.to_file()
    await inter.edit_original_response(file=file)


@emoji_rename_command.autocomplete("emoji_name")
async def emoji_rename_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
    return [emoji.name for emoji in inter.guild.emojis if name.casefold() in emoji.name.casefold()][:25]


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
async def sticker_remove_command(inter: disnake.GuildCommandInteraction, sticker_name: str) -> None:
    """
    Remove a sticker from the server.

    Parameters
    ----------
    sticker: The sticker to be removed from the server.
    """
    await inter.response.defer()
    guild_sticker = [
        sticker for sticker in inter.guild.stickers if sticker_name.casefold() == sticker.name.casefold()
    ][0]
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


@sticker_remove_command.autocomplete("sticker_name")
async def sticker_remove_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
    return [sticker.name for sticker in inter.guild.stickers if name.casefold() in sticker.name.casefold()][:25]


@sticker_command.sub_command(name="rename")
async def sticker_rename_command(inter: disnake.GuildCommandInteraction, sticker_name: str, name: str) -> None:
    """
    Rename a sticker from the server.

    Parameters
    ----------
    sticker: The sticker to be renamed from the server.
    name: The new sticker name.
    """
    await inter.response.defer()
    guild_sticker = [
        sticker for sticker in inter.guild.stickers if sticker_name.casefold() == sticker.name.casefold()
    ][0]
    await guild_sticker.edit(name=name)
    file = await guild_sticker.to_file()
    await inter.edit_original_response(file=file)


@sticker_rename_command.autocomplete("sticker_name")
async def sticker_rename_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
    return [sticker.name for sticker in inter.guild.stickers if name.casefold() in sticker.name.casefold()][:25]


async def data_from_url(url: str, /) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.read()
            return data


async def datas_from_message_attachments(message: disnake.Message, /) -> list[bytes]:
    datas = []
    for attachment in message.attachments:
        data = await attachment.read()
        datas.append(data)
    return datas


async def datas_from_message_embeds(message: disnake.Message, /) -> list[bytes]:
    datas = []
    for embed in message.embeds:
        media = embed.video or embed.thumbnail or embed.image
        if media:
            data = await data_from_url(media.url)
            datas.append(data)
    return datas


async def datas_from_message_emojis(message: disnake.Message, /) -> list[bytes]:
    datas = []
    for emoji_name, emoji_id in re.findall(r"<a?:(\w+):(\d{16,19})>", message.content):
        emoji = plugin.bot.get_emoji(int(emoji_id))
        data = await emoji.read()
        datas.append(data)
    return datas


async def datas_from_message_stickers(message: disnake.Message, /) -> list[bytes]:
    datas = []
    for sticker in message.stickers:
        data = await sticker.read()
        datas.append(data)
    return datas


async def datas_from_message(message: disnake.Message, /) -> list[bytes]:
    datas = []
    datas.extend(await datas_from_message_attachments(message))
    datas.extend(await datas_from_message_embeds(message))
    datas.extend(await datas_from_message_emojis(message))
    datas.extend(await datas_from_message_stickers(message))
    return datas


@commands.has_permissions(manage_emojis_and_stickers=True)
@plugin.message_command(name="Add media as emoji")
async def emoji_add_message_command(inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
    await inter.response.defer()
    datas = await datas_from_message(message)
    if datas:
        if len(datas) > 1:
            raise Exception(datas)  # TODO: add error message
        guild_emoji = await inter.guild.create_custom_emoji(name=str(message.id), image=datas[0])
        file = await guild_emoji.to_file()
        await inter.edit_original_response(file=file)
    else:
        await inter.edit_original_response("💨")


@commands.has_permissions(manage_emojis_and_stickers=True)
@plugin.message_command(name="Add media as sticker")
async def sticker_add_message_command(inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
    await inter.response.defer()
    datas = await datas_from_message(message)
    if datas:
        if len(datas) > 1:
            raise Exception(datas)  # TODO: add error message
        with asset.resize_asset(datas[0], width=320, height=320) as sticker_bytes:
            file = disnake.File(sticker_bytes, filename=f"{message.id}.png")
            guild_sticker = await inter.guild.create_sticker(name=str(message.id), emoji="❓", file=file)
            file = await guild_sticker.to_file()
            await inter.edit_original_response(file=file)
    else:
        await inter.edit_original_response("💨")


setup, teardown = plugin.create_extension_handlers()
