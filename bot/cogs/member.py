import disnake
from disnake.ext import commands

from bot import Bot
from bot.ext import HEX, URL, Dropdown, Embed, application_webhook, checks
from bot.services import imagga, pil


class Member(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.check(checks.user_has_role_icon)
    @commands.slash_command()
    async def color(
        self,
        inter: disnake.GuildCommandInteraction,
        hex_code: HEX | None = None,
        image_url: URL | None = None,
        image_file: disnake.Attachment | None = None,
    ) -> None:
        """
        Change your color on the server. {{COLOR}}

        Parameters
        ----------
        hex_code: Hexadecimal code (#ABC123) {{HEX}}
        image_url: Image URL {{IMAGE_URL}}
        image_file: Image attachment {{IMAGE_FILE}}
        """
        checks.one_of_or_none(hex_code, image_file, image_url)

        async def _edit_color(inter: disnake.Interaction, hex_code: HEX | str | int) -> None:
            old_color = inter.author.color
            role = await inter.author.top_role.edit(color=disnake.Color(int(hex_code)))
            embed = Embed.from_interaction(inter, description=f"`{old_color}` -> `{role.color}`")
            await inter.send(embed=embed)

        if hex_code:
            await _edit_color(inter, hex_code)
        else:
            await inter.response.defer()
            image: disnake.Attachment | URL | disnake.Asset = (
                image_file or image_url or inter.author.display_avatar.with_size(512).with_format("png")
            )
            image_binary = await image.read()
            colors = await imagga.get_colors_from_image(image_binary)
            hex_colors = [HEX(hex_code=color["html_code"], name=color["closest_palette_color"]) for color in colors]
            options = [
                disnake.SelectOption(label=hex_color.code, value=str(hex_color.value), description=hex_color.name)
                for hex_color in hex_colors
            ]
            dropdown = Dropdown(callback=_edit_color, placeholder="...", options=options)
            image_bytes = pil.create_image_from_rgb_colors([hex_color.rgb for hex_color in hex_colors])
            file = disnake.File(image_bytes, filename="colors.png")
            image_bytes.close()
            embed = Embed.from_interaction(inter)
            embed.set_image(file=file)
            await inter.edit_original_response(embed=embed, view=dropdown)
            file.close()

    @commands.check(checks.user_has_role_icon)
    @commands.check(checks.guild_has_role_icons_feature)
    @commands.slash_command()
    async def badge(
        self,
        inter: disnake.GuildCommandInteraction,
        emote: disnake.PartialEmoji | None = None,
        image_url: URL | None = None,
        image_file: disnake.Attachment | None = None,
    ) -> None:
        """
        Change your badge on the server. {{BADGE}}

        Parameters
        ----------
        emote: Emote {{EMOTE}}
        image_url: Image URL {{IMAGE_URL}}
        image_file: Image attachment {{IMAGE_FILE}}
        """
        checks.one_of_or_none(emote, image_file, image_url)
        await inter.response.defer()
        if emote and emote.is_unicode_emoji():
            role = await inter.author.top_role.edit(icon=None, emoji=emote)
        elif emote and emote.is_custom_emoji():
            role = await inter.author.top_role.edit(icon=emote, emoji=None)
        elif image_file or image_url:
            image: disnake.Attachment | URL = image_file or image_url
            image_binary = await image.read()
            role = await inter.author.top_role.edit(icon=image_binary, emoji=None)
        else:
            role = inter.author.top_role
        if role.icon:
            file = await role.icon.to_file()
        elif role.emoji:
            file = await role.emoji.to_file()
        else:
            raise Exception()  # TODO: add message
        embed = Embed.from_interaction(inter)
        embed.set_image(file=file)
        await inter.edit_original_response(embed=embed)
        file.close()

    @commands.slash_command()
    async def fake(
        self,
        inter: disnake.GuildCommandInteraction,
        content: str,
        member: disnake.Member = commands.Param(lambda inter: inter.author),
        name: str | None = None,
        image_url: URL | None = None,
        image_file: disnake.Attachment | None = None,
    ) -> None:
        """
        Send a message faking being someone else. {{FAKE}}

        Parameters
        ----------
        content: Message content {{CONTENT}}
        member: Server user {{MEMBER}}
        name: Name {{NAME}}
        image_url: Image URL {{IMAGE_URL}}
        image_file: Image attachment {{IMAGE_FILE}}
        """
        checks.one_of_or_none(image_file, image_url)
        await inter.response.defer(ephemeral=True)
        name = name or member.display_name
        image: disnake.Attachment | URL | disnake.Asset = image_file or image_url or member.display_avatar
        avatar_url = image.url
        webhook = await application_webhook(self.bot, inter.channel)
        message = await webhook.send(content, username=name, avatar_url=avatar_url, wait=True)
        embed = Embed.from_interaction(inter, description=message.jump_url)
        await inter.edit_original_response(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Member(bot))
