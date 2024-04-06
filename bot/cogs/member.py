import disnake
from disnake.ext import commands
from disnake.i18n import Localized

from bot.ext import Dropdown, Profile, checks
from bot.services import imagga, pil


async def update_user_color(inter: disnake.GuildCommandInteraction, int_code: str | int) -> None:
    color = disnake.Color(int(int_code))
    old_color = inter.author.color
    role = await inter.author.top_role.edit(color=color)
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
        await inter.response.defer()
        if not member:
            member = inter.author
        user = await inter.bot.fetch_user(member.id)
        profile = Profile(member=member, user=user)
        await inter.edit_original_response(embed=profile)

    @commands.check(checks.user_has_role)
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
        await inter.response.defer(ephemeral=True)
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
            await inter.edit_original_response(file=file, view=dropdown)

    @commands.check(checks.user_has_role)
    @commands.check(checks.guild_has_role_icons_feature)
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
        await inter.response.defer(ephemeral=True)
        if emoji:
            role = await inter.author.top_role.edit(icon=None, emoji=emoji)
        elif emote or image:
            icon = emote or image
            role = await inter.author.top_role.edit(icon=icon, emoji=None)
        else:
            role = inter.author.top_role
        if role.icon:
            file = await role.icon.to_file()
            await inter.edit_original_response(file=file)
        else:
            await inter.edit_original_response(role.emoji)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Member(bot))
