import disnake
from disnake.ext import commands
from disnake.i18n import Localized

from bot.core import Bot
from bot.ext import Dropdown, checks
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
    old_color = inter.author.color
    role = await inter.author.top_role.edit(color=disnake.Color(int(int_code)))
    await inter.send(f"🎨 `{old_color}` -> `{role.color}`", ephemeral=True)


class Member(commands.Cog):
    @commands.slash_command(
        name=Localized(key="COMMAND_PROFILE"),
        description=Localized("", key="COMMAND_PROFILE_DESC"),
    )
    async def profile(
        self,
        inter: disnake.GuildCommandInteraction,
        member: disnake.Member
        | None = commands.Param(
            None,
            name=Localized(key="ARG_MEMBER"),
            description=Localized("", key="ARG_MEMBER_DESC"),
        ),
    ) -> None:
        if not member:
            member = inter.author
        user = await inter.bot.fetch_user(member.id)
        profile = Profile(member=member, user=user)
        await inter.send(embed=profile)

    @commands.check(checks.user_has_role_icon())
    @commands.slash_command(
        name=Localized(key="COMMAND_COLOR"),
        description=Localized("", key="COMMAND_COLOR_DESC"),
    )
    async def color(
        self,
        inter: disnake.GuildCommandInteraction,
        hex: str
        | None = commands.Param(
            None,
            name=Localized(key="ARG_HEX"),
            description=Localized("", key="ARG_HEX_DESC"),
        ),
        image: disnake.Attachment
        | None = commands.Param(
            None,
            name=Localized(key="ARG_IMAGE"),
            description=Localized("", key="ARG_IMAGE_DESC"),
        ),
    ) -> None:
        if hex:
            int_code = int(hex.strip("#"), 16)
            await update_user_color(inter, int_code)
        else:
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
            await inter.send(file=file, view=dropdown)

    @commands.check(checks.user_has_role_icon())
    @commands.check(checks.guild_has_role_icons_feature())
    @commands.slash_command(
        name=Localized(key="COMMAND_BADGE"),
        description=Localized("", key="COMMAND_BADGE_DESC"),
    )
    async def badge(
        self,
        inter: disnake.GuildCommandInteraction,
        emoji: str
        | None = commands.Param(
            None,
            name=Localized(key="ARG_EMOJI"),
            description=Localized("", key="ARG_EMOJI_DESC"),
        ),
        emote: disnake.PartialEmoji
        | None = commands.Param(
            None,
            name=Localized(key="ARG_EMOTE"),
            description=Localized("", key="ARG_EMOTE_DESC"),
        ),
        image: disnake.Attachment
        | None = commands.Param(
            None,
            name=Localized(key="ARG_IMAGE"),
            description=Localized("", key="ARG_IMAGE_DESC"),
        ),
    ) -> None:
        if emoji:
            role = await inter.author.top_role.edit(icon=None, emoji=emoji)
        elif emote or image:
            icon = emote or image
            role = await inter.author.top_role.edit(icon=icon, emoji=None)
        else:
            role = inter.author.top_role
        if role.icon:
            file = await role.icon.to_file()
            await inter.send(file=file, ephemeral=True)
        else:
            await inter.send(role.emoji, ephemeral=True)

    @commands.slash_command(
        name=Localized(key="COMMAND_MATCH"),
        description=Localized("", key="COMMAND_MATCH_DESC"),
    )
    async def match(
        self,
        inter: disnake.GuildCommandInteraction,
        member_1: disnake.Member = commands.Param(
            name=Localized(key="ARG_MEMBER_1"), description=Localized("", key="ARG_MEMBER_1_DESC")
        ),
        member_2: disnake.Member = commands.Param(
            name=Localized(key="ARG_MEMBER_2"), description=Localized("", key="ARG_MEMBER_2_DESC")
        ),
        vertical: bool = commands.Param(
            False, name=Localized(key="ARG_VERTICAL"), description=Localized("", key="ARG_VERTICAL_DESC")
        ),
    ) -> None:
        image_left_binary = await member_1.display_avatar.with_size(512).with_format("png").read()
        image_right_binary = await member_2.display_avatar.with_size(512).with_format("png").read()
        if vertical:
            image_binary = pil.merge_images_vertical(image_left_binary, image_right_binary)
        else:
            image_binary = pil.merge_images_horizontal(image_left_binary, image_right_binary)
        file = disnake.File(fp=image_binary, filename="match.png")
        await inter.send(file=file)
        image_binary.close()


def setup(bot: Bot) -> None:
    bot.add_cog(Member(bot))
