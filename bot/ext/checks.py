import disnake
from disnake.ext import commands
from disnake.ext.commands import CheckFailure


@commands.check
def user_has_role(inter: disnake.GuildCommandInteraction) -> bool:
    return inter.author.top_role != inter.guild.default_role


@commands.check
def guild_has_role_icons_feature(inter: disnake.ApplicationCommandInteraction) -> bool:
    return "ROLE_ICONS" in inter.guild.features


@commands.check
def user_is_connected(inter: disnake.GuildCommandInteraction) -> bool:
    if not inter.author.voice:
        raise CheckFailure("You must be on a voice channel to use this command.")
    return True


@commands.check
def bot_is_connected(inter: disnake.GuildCommandInteraction) -> bool:
    if not inter.guild.voice_client:
        raise CheckFailure("You must be on a voice channel to use this command.")
    return True


@commands.check
def bot_and_user_in_same_channel(inter: disnake.GuildCommandInteraction) -> bool:
    if not inter.guild.voice_client or not inter.author.voice:
        raise CheckFailure("You or the bot is not connected to a voice channel.")
    if not inter.guild.voice_client.channel == inter.author.voice.channel:
        raise CheckFailure("You're not connected to the same voice channel as the bot.")
    return True


@commands.check
def queue_is_not_empty(inter: disnake.GuildCommandInteraction) -> bool:
    if inter.guild.id not in inter.bot.players:
        raise CheckFailure("You or the bot is not connected to a voice channel.")
    player = inter.bot.players[inter.guild.id]
    if player.queue.is_empty():
        raise CheckFailure("The queue is empty.")
    return True
