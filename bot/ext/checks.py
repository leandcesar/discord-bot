import disnake
from disnake.ext import commands


def user_has_role_icon():
    def predicate(inter: disnake.GuildCommandInteraction) -> bool:
        return inter.author.top_role and inter.author.top_role != inter.guild.default_role

    return commands.check(predicate)


def guild_has_role_icons_feature():
    def predicate(inter: disnake.ApplicationCommandInteraction) -> bool:
        return "ROLE_ICONS" in inter.guild.features

    return commands.check(predicate)


def user_is_connected():
    def predicate(inter: disnake.GuildCommandInteraction) -> bool:
        return inter.author.voice

    return commands.check(predicate)


def user_is_disconnected():
    def predicate(inter: disnake.GuildCommandInteraction) -> bool:
        return not inter.author.voice

    return commands.check(predicate)


def bot_is_connected():
    def predicate(inter: disnake.GuildCommandInteraction) -> bool:
        return inter.guild.voice_client

    return commands.check(predicate)


def bot_is_disconnected():
    def predicate(inter: disnake.GuildCommandInteraction) -> bool:
        return not inter.guild.voice_client

    return commands.check(predicate)


def bot_and_user_in_same_channel():
    def predicate(inter: disnake.GuildCommandInteraction) -> bool:
        return inter.guild.voice_client.channel == inter.author.voice.channel

    return commands.check(predicate)
