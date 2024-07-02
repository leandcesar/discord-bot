import disnake
from disnake.ext.commands import CheckFailure


def user_has_role_icon(inter: disnake.GuildCommandInteraction) -> bool:
    if not inter.author.top_role or inter.author.top_role == inter.guild.default_role:
        raise CheckFailure("User has no top_role for icon")
    return True


def guild_has_role_icons_feature(inter: disnake.GuildCommandInteraction) -> bool:
    if "ROLE_ICONS" not in inter.guild.features:
        raise CheckFailure("Guild has no ROLE_ICONS feature")
    return True


def one_of(*args) -> bool:
    number_of_args = sum(arg is not None for arg in args)
    if number_of_args > 1:
        raise CheckFailure("You can only provide one of the specified arguments.")
    if number_of_args < 1:
        raise CheckFailure("You must provide at least one of the specified arguments.")
    return True


def one_of_or_none(*args) -> bool:
    number_of_args = sum(arg is not None for arg in args)
    if number_of_args > 1:
        raise CheckFailure("You can only provide one of the specified arguments.")
    return True
