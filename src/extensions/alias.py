import asyncio
import re

import disnake
from disnake.ext import commands
from disnake.ext.commands.errors import BadArgument, CommandError
from disnake_plugins import Plugin

from src import config
from src.bot import Bot
from src.util.persistent_dict import PersistentDict
from src.util.webhook import application_webhook

plugin = Plugin[Bot]()

DISCORD_MESSAGE_REGEX = re.compile(r"https://discord\.com/channels/([0-9]+)/([0-9]+)/([0-9]+)")


@plugin.load_hook()
async def afk_load_hook() -> None:
    plugin.bot.alias_data = PersistentDict.from_file(config.File.alias)


@plugin.slash_command(name="alias")
async def alias_slash_command(inter: disnake.ApplicationCommandInteraction) -> None:
    """
    Command for managing your aliases.
    """


async def _aliases_command(inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction) -> None:
    if inter.author.id not in plugin.bot.alias_data:
        raise CommandError("You don't have any saved aliases.")
    aliases = plugin.bot.alias_data[inter.author.id].keys()
    await plugin.bot.reply(inter, "```\n" + "\n".join(aliases) + "\n```")


@plugin.command(name="aliases", description="Display a list of your saved aliases.")
async def aliases_prefix_command(ctx: commands.Context[Bot]) -> None:
    await _aliases_command(ctx)


@alias_slash_command.sub_command(name="list")
async def alias_list_slash_command(inter: disnake.ApplicationCommandInteraction) -> None:
    """
    Display a list of your saved aliases.
    """
    await inter.response.defer(ephemeral=True)
    await _aliases_command(inter)


async def _alias_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction, *, alias_name: str, content: str
) -> None:
    if inter.author.id not in plugin.bot.alias_data:
        plugin.bot.alias_data[inter.author.id] = {}
    plugin.bot.alias_data[inter.author.id][alias_name] = content
    await plugin.bot.reply(inter, f'atalho "{alias_name}" criado')


@plugin.command(name="alias", description="Create a custom alias for quick reuse.")
async def alias_prefix_command(ctx: commands.Context[Bot], alias_name: str, *, content: str) -> None:
    await _alias_command(ctx, alias_name=alias_name, content=content)


@alias_slash_command.sub_command(name="add")
async def alias_add_slash_command(
    inter: disnake.ApplicationCommandInteraction, alias_name: str, content: str
) -> None:
    """
    Create a custom alias for quick reuse.

    Parameters
    ----------
    alias_name: The name of the alias.
    content: The message or content to be saved under the alias.
    """
    await inter.response.defer(ephemeral=True)
    await _alias_command(inter, alias_name=alias_name, content=content)


@alias_add_slash_command.autocomplete("alias_name")
async def alias_add_autocomplete(self, inter: disnake.ApplicationCommandInteraction, name: str) -> list[str]:
    if inter.author.id not in plugin.bot.alias_data:
        return []
    aliases = plugin.bot.alias_data[inter.author.id].keys()
    return [alias for alias in aliases if name in alias]


async def _unalias_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction, *, alias_name: str
) -> None:
    if inter.author.id not in plugin.bot.alias_data:
        raise CommandError("You don't have any saved aliases.")
    if alias_name not in plugin.bot.alias_data[inter.author.id]:
        raise BadArgument(f"Alias {alias_name!r} not found.")
    plugin.bot.alias_data[inter.author.id].pop(alias_name)
    await plugin.bot.reply(inter, f'atalho "{alias_name}" removido')


@plugin.command(name="unalias", description="Remove a saved alias.")
async def unalias_prefix_command(ctx: commands.Context[Bot], alias_name: str) -> None:
    await _unalias_command(ctx, alias_name=alias_name)


@alias_slash_command.sub_command(name="remove")
async def alias_remove_slash_command(inter: disnake.ApplicationCommandInteraction, alias_name: str) -> None:
    """
    Remove a saved alias.

    Parameters
    ----------
    alias_name: The name of the alias.
    """
    await inter.response.defer(ephemeral=True)
    await _unalias_command(inter, alias_name=alias_name)


@alias_remove_slash_command.autocomplete("alias_name")
async def alias_remove_autocomplete(self, inter: disnake.ApplicationCommandInteraction, name: str) -> list[str]:
    if inter.author.id not in plugin.bot.alias_data:
        return []
    aliases = plugin.bot.alias_data[inter.author.id].keys()
    return [alias for alias in aliases if name in alias]


@plugin.message_command(name="Add as alias")
async def alias_message_command(inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
    await inter.response.send_modal(
        title="Create alias",
        custom_id="create_alias",
        components=[
            disnake.ui.TextInput(
                label="Alias name",
                custom_id="alias_name",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=30,
            ),
        ],
    )

    try:
        modal_inter: disnake.ModalInteraction = await plugin.bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "create_alias" and i.author.id == inter.author.id,
            timeout=300,
        )
    except asyncio.TimeoutError:
        return None

    alias_name = modal_inter.text_values["alias_name"]
    await modal_inter.response.defer(ephemeral=True)
    await _alias_command(modal_inter, alias_name=alias_name, content=message.jump_url)


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    if str(message.author.id) not in plugin.bot.alias_data:
        return None
    if message.content not in plugin.bot.alias_data[str(message.author.id)]:
        return None
    content = plugin.bot.alias_data[str(message.author.id)][message.content]
    files = []
    discord_message = DISCORD_MESSAGE_REGEX.match(content)
    if discord_message:
        channel_id = discord_message.group(2)
        message_id = discord_message.group(3)
        channel = await plugin.bot.fetch_channel(channel_id)
        original_message = await channel.fetch_message(message_id)
        content = original_message.content
        files = [await attachment.to_file() for attachment in original_message.attachments]
    webhook = await application_webhook(plugin.bot, message.channel)
    await webhook.send(
        content,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url,
        files=files,
    )
    await message.delete()


setup, teardown = plugin.create_extension_handlers()
