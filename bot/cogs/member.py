import disnake
from disnake.ext import commands

from bot.core import Bot
from bot.ext import Dropdown, Embed, checks
from bot.services import imagga, pil


class Profile(disnake.Embed):
    def __init__(self, *, member: disnake.Member, user: disnake.User, **kwargs) -> None:
        title = f"`{member.display_name}` aka. "
        if member.display_name != member.global_name:
            title += f"`{member.global_name}`, "
        title += f"`{member.name}`"
        if isinstance(member.activity, disnake.Spotify):
            description = f"[**{member.activity.title}** from {member.activity.artist}]({member.activity.track_url})"
        elif isinstance(member.activity, disnake.Streaming):
            description = f"[**{member.activity.game}** from @{member.activity.twitch_name}]({member.activity.url})"
        elif member.activity:
            description = member.activity.name
        else:
            description = ""
        super().__init__(
            title=title,
            description=description,
            color=member.color,
            url=user.display_avatar.url,
        )
        if user.display_avatar:
            self.set_thumbnail(user.display_avatar.url)
        if user.banner:
            self.set_image(user.banner.url)
        self.add_field("Cor", f"`{member.color}`")
        self.add_field("Criado em", f"<t:{int(member.created_at.timestamp())}:d>")
        self.add_field("Entrou em", f"<t:{int(member.joined_at.timestamp())}:d>")
        self.add_field("Cargos", " ".join([role.mention for role in member.roles[1:][::-1]]), inline=False)


async def update_user_color(inter: disnake.GuildCommandInteraction, int_code: str | int) -> None:
    await inter.response.defer()
    old_color = inter.author.color
    role = await inter.author.top_role.edit(color=disnake.Color(int(int_code)))
    description = f"`{old_color}` -> `{role.color}`"
    embed = Embed(inter, description=description)
    await inter.edit_original_response(embed=embed)


class Member(commands.Cog):
    @commands.slash_command()
    async def profile(self, inter: disnake.GuildCommandInteraction, member: disnake.Member | None) -> None:
        """
        Get profile information of a user. {{PROFILE}}

        Parameters
        ----------
        member: Server user {{MEMBER}}
        """
        await inter.response.defer()
        if not member:
            member = inter.author
        user = await inter.bot.fetch_user(member.id)
        profile = Profile(member=member, user=user)
        await inter.edit_original_response(embed=profile)

    @commands.check(checks.user_has_role_icon())
    @commands.slash_command()
    async def color(
        self,
        inter: disnake.GuildCommandInteraction,
        hex: str | None = None,
        image: disnake.Attachment | None = None,
    ) -> None:
        """
        Change your color on the server. {{COLOR}}

        Parameters
        ----------
        hex: Hexadecimal code (#ABC123) {{HEX}}
        """
        if hex:
            int_code = int(hex.strip("#"), 16)
            await update_user_color(inter, int_code)
        else:
            await inter.response.defer()
            if not image:
                image = inter.author.display_avatar.with_size(512).with_format("png")
            image_binary = await image.read()
            colors = await imagga.Colors().from_image(image_binary)
            options = [
                disnake.SelectOption(label=f"{i}. {c}", value=str(c.int_code)) for i, c in enumerate(colors, start=1)
            ]
            dropdown = Dropdown(callback=update_user_color, placeholder="Select...", options=options)
            image_binary = pil.create_image_from_rgb_colors([c.rgb_code for c in colors])
            file = disnake.File(fp=image_binary, filename="colors.png")
            image_binary.close()
            embed = Embed(inter, image={"file": file})
            await inter.edit_original_response(embed=embed, view=dropdown)
            file.close()

    @commands.check(checks.user_has_role_icon())
    @commands.check(checks.guild_has_role_icons_feature())
    @commands.slash_command()
    async def badge(
        self,
        inter: disnake.GuildCommandInteraction,
        emoji: str | None = None,
        emote: disnake.PartialEmoji | None = None,
        image: disnake.Attachment | None = None,
    ) -> None:
        """
        Change your badge on the server. {{BADGE}}

        Parameters
        ----------
        emoji: Emoji {{EMOJI}}
        emote: Emote {{EMOTE}}
        image: Image attachment {{IMAGE}}
        """
        await inter.response.defer()
        if emoji:
            role = await inter.author.top_role.edit(icon=None, emoji=emoji)
        elif emote or image:
            icon = emote or image
            role = await inter.author.top_role.edit(icon=icon, emoji=None)
        else:
            role = inter.author.top_role
        if role.icon:
            file = await role.icon.to_file()
        else:
            file = await role.emoji.to_file()
        embed = Embed(inter, image={"file": file})
        await inter.edit_original_response(embed=embed)
        file.close()

    @commands.slash_command()
    async def match(
        self,
        inter: disnake.GuildCommandInteraction,
        member_1: disnake.Member,
        member_2: disnake.Member,
        vertical: bool = False,
    ) -> None:
        """
        Match profile pictures of two users. {{MATCH}}

        Parameters
        ----------
        member_1: Server user 1 {{MEMBER1}}
        member_2: Server user 2 {{MEMBER2}}
        vertical: Should the profile pictures be joined vertically? {{VERTICAL}}
        """
        await inter.response.defer()
        image_left_binary = await member_1.display_avatar.with_size(512).with_format("png").read()
        image_right_binary = await member_2.display_avatar.with_size(512).with_format("png").read()
        if vertical:
            image_binary = pil.merge_images_vertical(image_left_binary, image_right_binary)
        else:
            image_binary = pil.merge_images_horizontal(image_left_binary, image_right_binary)
        file = disnake.File(fp=image_binary, filename="match.png")
        image_binary.close()
        embed = Embed(inter, image={"file": file})
        await inter.edit_original_response(embed=embed)
        file.close()


def setup(bot: Bot) -> None:
    bot.add_cog(Member(bot))
