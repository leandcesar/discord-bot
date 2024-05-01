import datetime
from typing import TypedDict

import disnake


class Image(TypedDict):
    url: str | None
    file: disnake.File | None


class Thumbnail(TypedDict):
    url: str | None
    file: disnake.File | None


class Author(TypedDict):
    name: str
    url: str | None
    icon_url: str | None


class Footer(TypedDict):
    text: str
    icon_url: str | None


class Field(TypedDict):
    name: str
    value: str
    inline: bool


class Embed(disnake.Embed):
    def __init__(
        self,
        inter: disnake.GuildCommandInteraction | None = None,
        *,
        title: str | None = None,
        description: str | None = None,
        image: Image | None = None,
        thumbnail: Thumbnail | None = None,
        author: Author | disnake.Member | disnake.Guild = None,
        footer: Footer | disnake.Member | disnake.Guild = None,
        fields: list[Field] | None = None,
        timestamp: datetime.datetime | None = None,
        color: disnake.Colour = disnake.Colour.light_gray(),
        **kwargs,
    ) -> None:
        if not title and inter:
            title = inter.bot.localized(f"{inter.application_command.name.upper()}_NAME", locale=inter.locale)
        if not author and inter:
            author = inter.guild
        if not footer and inter:
            footer = inter.author
        super().__init__(
            title=title,
            description=description,
            color=color,
            timestamp=timestamp,
        )
        if image:
            self.set_image(**image)
        if thumbnail:
            self.set_thumbnail(**thumbnail)
        if author:
            self._set_author(author)
        if footer:
            self._set_footer(footer)
        if fields:
            self._add_fields(fields)

    def _set_author(self, author: Author | disnake.Member | disnake.Guild) -> None:
        if isinstance(author, disnake.Member):
            self.set_author(
                name=author.display_name,
                icon_url=author.display_avatar.url,
            )
        elif isinstance(author, disnake.Guild):
            self.set_author(
                name=author.name,
                icon_url=author.icon.url,
            )
        else:
            self.set_author(**author)

    def _set_footer(self, footer: Footer | disnake.Member | disnake.Guild) -> None:
        if isinstance(footer, disnake.Member):
            self.set_footer(
                text=footer.display_name,
                icon_url=footer.display_avatar.url,
            )
        elif isinstance(footer, disnake.Guild):
            self.set_footer(
                text=footer.name,
                icon_url=footer.icon.url,
            )
        else:
            self.set_footer(**footer)

    def _add_fields(self, fields: list[Field]) -> None:
        for field in fields:
            self.add_field(**field)
