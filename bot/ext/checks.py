import disnake
from disnake.ext import commands
from disnake.ext.commands import CheckFailure


def user_has_role(inter: disnake.GuildCommandInteraction) -> bool:
    if inter.author.top_role == inter.guild.default_role:
        raise CheckFailure()
    return True


def guild_has_role_icons_feature(inter: disnake.ApplicationCommandInteraction) -> bool:
    if "ROLE_ICONS" not in inter.guild.features:
        raise CheckFailure()
    return True


def user_is_connected(inter: disnake.GuildCommandInteraction) -> bool:
    if not inter.author.voice:
        raise CheckFailure()
    return True


def user_is_disconnected(inter: disnake.GuildCommandInteraction) -> bool:
    if inter.author.voice:
        raise CheckFailure()
    return True


def bot_is_connected(inter: disnake.GuildCommandInteraction) -> bool:
    if not inter.guild.voice_client:
        raise CheckFailure()
    return True


def bot_is_disconnected(inter: disnake.GuildCommandInteraction) -> bool:
    if inter.guild.voice_client:
        raise CheckFailure()
    return True


def bot_and_user_in_same_channel(inter: disnake.GuildCommandInteraction) -> bool:
    if not inter.guild.voice_client or not inter.author.voice:
        raise CheckFailure()
    if not inter.guild.voice_client.channel == inter.author.voice.channel:
        raise CheckFailure()
    return True


def queue_is_not_empty(inter: disnake.GuildCommandInteraction) -> bool:
    if inter.guild.id not in inter.bot.players:
        raise CheckFailure()
    player = inter.bot.players[inter.guild.id]
    if player.queue.is_empty():
        raise CheckFailure()
    return True
