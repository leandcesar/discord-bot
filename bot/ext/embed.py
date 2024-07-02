import disnake


class Embed(disnake.Embed):
    @classmethod
    def from_interaction(
        cls,
        inter: disnake.GuildCommandInteraction | disnake.MessageInteraction,
        /,
        **kwargs,
    ):
        if "title" not in kwargs:
            command_name_key = f"{inter.application_command.name.upper()}_NAME"
            command_name_value = inter.bot.localized(command_name_key, locale=inter.locale)
            kwargs["title"] = command_name_value
        if "color" not in kwargs:
            kwargs["color"] = disnake.Colour.default()
        instance = cls(**kwargs)
        instance.set_author(
            name=inter.guild.name,
            icon_url=inter.guild.icon.url,
        )
        instance.set_footer(
            text=inter.author.display_name,
            icon_url=inter.author.display_avatar.url,
        )
        return instance
