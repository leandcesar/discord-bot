import disnake
from disnake.ext import commands
from disnake.i18n import Localized

from bot.ext import get_application_webhook
from bot.services import pil


class RoleplayCog(commands.Cog):
    @commands.slash_command(
        name=Localized(key="COMMAND_MATCH"),
        description=Localized("", key="COMMAND_MATCH_DESC"),
    )
    async def match(
        self,
        inter: disnake.GuildCommandInteraction,
        member_left: disnake.Member = commands.Param(
            name=Localized(key="ARG_MEMBER_LEFT"), description=Localized("", key="ARG_MEMBER_LEFT_DESC")
        ),
        member_right: disnake.Member = commands.Param(
            name=Localized(key="ARG_MEMBER_RIGHT"), description=Localized("", key="ARG_MEMBER_RIGHT_DESC")
        ),
        vertical: bool = commands.Param(
            False, name=Localized(key="ARG_VERTICAL"), description=Localized("", key="ARG_VERTICAL_DESC")
        ),
    ) -> None:
        await inter.response.defer()
        image_left_binary = await member_left.display_avatar.with_size(512).with_format("png").read()
        image_right_binary = await member_right.display_avatar.with_size(512).with_format("png").read()
        if vertical:
            image_binary = pil.merge_images_vertical(image_left_binary, image_right_binary)
        else:
            image_binary = pil.merge_images_horizontal(image_left_binary, image_right_binary)
        file = disnake.File(fp=image_binary, filename="match.png")
        await inter.edit_original_response(file=file)
        image_binary.close()

    @commands.slash_command(
        name=Localized(key="COMMAND_FAKE"),
        description=Localized("", key="COMMAND_FAKE_DESC"),
    )
    async def fake(
        self,
        inter: disnake.GuildCommandInteraction,
        content: str = commands.Param(
            name=Localized(key="ARG_CONTENT"), description=Localized("", key="ARG_CONTENT_DESC")
        ),
        member: disnake.Member
        | None = commands.Param(
            None, name=Localized(key="ARG_MEMBER"), description=Localized("", key="ARG_MEMBER_DESC")
        ),
        name: str
        | None = commands.Param(
            None, name=Localized(key="ARG_NAME"), description=Localized("", key="ARG_NAME_DESC")
        ),
        image: disnake.Attachment
        | None = commands.Param(
            None, name=Localized(key="ARG_IMAGE"), description=Localized("", key="ARG_IMAGE_DESC")
        ),
        channel: disnake.TextChannel
        | None = commands.Param(
            None, name=Localized(key="ARG_CHANNEL"), description=Localized("", key="ARG_CHANNEL_DESC")
        ),
    ) -> None:
        await inter.response.defer(ephemeral=True)
        if not member:
            member = inter.author
        if not name:
            name = member.display_name
        if not image:
            image = member.display_avatar
        if not channel:
            channel = inter.channel
        avatar_url = image.url if image else None
        webhook = await get_application_webhook(inter, channel=channel)
        message = await webhook.send(content, username=name, avatar_url=avatar_url, wait=True)
        await inter.edit_original_response(message.jump_url)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(RoleplayCog(bot))
