from collections import defaultdict

import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src.bot import Bot

plugin = Plugin[Bot]()


async def _help_command(inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction) -> None:
    commands: dict[str, list[str]] = defaultdict(list)
    for slash_command in plugin.bot.slash_commands:
        if slash_command.name == "help":
            continue
        for sub_command in slash_command.children.values():
            commands[sub_command.description].append(f"`/{sub_command.qualified_name}`")
        if not slash_command.children:
            commands[slash_command.description].append(f"`/{slash_command.qualified_name}`")

    for command in plugin.bot.commands:
        if command.name == "help":
            continue
        commands[command.description].append(f"`+{command.qualified_name}`")
        for alias in command.aliases:
            commands[command.description].append(f"`+{alias}`")

    commands_help = [
        (
            "{} ({}): {}".format(names[0], ", ".join(names[1:]), description)
            if len(names) > 1
            else f"{names[0]}: {description}"
        )
        for description, names in commands.items()
    ]
    content = "\n".join(sorted(commands_help))
    await plugin.bot.reply(inter, content)


@plugin.command(name="help", description="Show this command.")
async def help_prefix_command(ctx: commands.Context[Bot]) -> None:
    await _help_command(ctx)


@plugin.slash_command(name="help")
async def help_slash_command(inter: disnake.ApplicationCommandInteraction) -> None:
    """
    Show this command.
    """
    await _help_command(inter)


setup, teardown = plugin.create_extension_handlers()
