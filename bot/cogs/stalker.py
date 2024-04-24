import datetime

import disnake
from disnake.ext import commands

from bot.core import Bot
from bot.ext import application_webhook


def ago(dt: datetime.datetime) -> datetime.timedelta:
    return datetime.datetime.now(tz=datetime.timezone.utc) - dt


def seconds_ago(dt: datetime.datetime) -> int:
    return ago(dt).seconds


class Stalker(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message) -> None:
        self.bot.edited_message_history.append(before)
        self.bot.edited_message_history = [
            m for m in self.bot.edited_message_history if seconds_ago(m.created_at) <= 600
        ]

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message) -> None:
        self.bot.deleted_message_history.append(message)
        self.bot.deleted_message_history = [
            m for m in self.bot.deleted_message_history if seconds_ago(m.created_at) <= 600
        ]

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[disnake.Message]) -> None:
        self.bot.deleted_message_history.extend(messages)
        self.bot.deleted_message_history = [
            m for m in self.bot.deleted_message_history if seconds_ago(m.created_at) <= 600
        ]

    @commands.slash_command()
    async def fake(
        self,
        inter: disnake.GuildCommandInteraction,
        content: str,
        member: disnake.Member | None = None,
        name: str | None = None,
        image: disnake.Attachment | None = None,
        channel: disnake.TextChannel | None = None,
    ) -> None:
        """
        Send a message faking being someone else. {{FAKE}}

        Parameters
        ----------
        content: Message content {{CONTENT}}
        member: Server user {{MEMBER}}
        name: Name {{NAME}}
        image: Image attachment {{IMAGE}}
        channel: Server channel {{CHANNEL}}
        """
        if not member:
            member = inter.author
        if not name:
            name = member.display_name
        if not image:
            image = member.display_avatar
        if not channel:
            channel = inter.channel
        avatar_url = image.url if image else None
        webhook = await application_webhook(inter, channel=channel)
        message = await webhook.send(content, username=name, avatar_url=avatar_url, wait=True)
        await inter.send(message.jump_url, ephemeral=True)

    @commands.slash_command()
    async def undo(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Undo the last deletion or edit of a message in the channel (up to 5 minutes). {{UNDO}}
        """
        for m in self.bot.deleted_message_history[::-1]:
            if m.channel.id == inter.channel.id:
                await inter.response.defer(ephemeral=True)
                member = await inter.guild.fetch_member(m.author.id)
                ttl = 600 - seconds_ago(m.created_at)
                webhook = await application_webhook(inter, channel=m.channel)
                files = [await attachment.to_file() for attachment in m.attachments]
                message = await webhook.send(
                    m.content,
                    username=member.display_name,
                    avatar_url=member.display_avatar,
                    files=files,
                    delete_after=ttl,
                    wait=True,
                )
                await inter.edit_original_response(message.jump_url)
                return None

    @commands.message_command()
    async def undo_edit(self, inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
        """
        {{UNDO_EDIT}}
        """
        if not message.edited_at:
            return None
        for m in self.bot.edited_message_history[::-1]:
            if m.channel.id == message.channel.id:
                member = await inter.guild.fetch_member(m.author.id)
                ttl = 600 - seconds_ago(m.edited_at)
                webhook = await application_webhook(inter, channel=m.channel)
                files = [await attachment.to_file() for attachment in m.attachments]
                message = await webhook.send(
                    m.content,
                    username=member.display_name,
                    avatar_url=member.display_avatar,
                    files=files,
                    delete_after=ttl,
                    wait=True,
                )
                await inter.response.send_message(
                    message.jump_url,
                    delete_after=ttl,
                    ephemeral=True,
                )
                return None


def setup(bot: Bot) -> None:
    bot.add_cog(Stalker(bot))
