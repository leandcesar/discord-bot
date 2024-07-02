import datetime

import disnake
from disnake.ext import commands
from prisma.types import MessageGroupByOutput

from bot import Bot
from bot.ext import Embed, Paginator, application_webhook


class Stalker(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.slash_command()
    async def ranking(
        self,
        inter: disnake.GuildCommandInteraction,
        channel: disnake.TextChannel | None = None,
        member: disnake.Member | None = None,
        interval: int = commands.Param(
            0,
            choices=[
                disnake.OptionChoice(disnake.Localized("day", key="INTERVAL_DAY"), 1),
                disnake.OptionChoice(disnake.Localized("week", key="INTERVAL_WEEK"), 7),
                disnake.OptionChoice(disnake.Localized("month", key="INTERVAL_MONTH"), 30),
                disnake.OptionChoice(disnake.Localized("year", key="INTERVAL_YEAR"), 365),
                disnake.OptionChoice(disnake.Localized("all", key="INTERVAL_ALL"), 0),
            ],
        ),
    ) -> None:
        """
        Get the ranking of message counts from server members. {{RANKING}}

        Parameters
        ----------
        channel: Server channel {{CHANNEL}}
        member: Server user {{MEMBER}}
        interval: Time interval for ranking. Choose between day, week, month, year, or all time. {{INTERVAL}}
        """
        after = inter.created_at - datetime.timedelta(days=interval) if interval else None
        by = ["channel_id"] if member else ["user_id"]
        where = {"channel": {"guild_id": inter.guild.id}}
        if channel:
            where["channel_id"] = channel.id
        if member:
            where["user_id"] = member.id
        if after:
            where["created_at"] = {"gte": after}
        messages = await self.bot.db.message.group_by(by, where=where, count=True)
        sorted_messages = sorted(messages, key=lambda x: x["_count"]["_all"], reverse=True)

        def _get_leaderboard_text(position: int, message: MessageGroupByOutput) -> str:
            text = f"`{position}.`"
            if "channel_id" in by:
                channel_id = message["channel_id"]
                text += f" <#{channel_id}>"
            if "user_id" in by:
                user_id = message["user_id"]
                text += f" <@{user_id}>"
            total = message["_count"]["_all"]
            text += f" {total}"
            return text

        leaderboard = [_get_leaderboard_text(i + 1, message) for i, message in enumerate(sorted_messages)]

        def _create_embed(i: int) -> disnake.Embed:
            description = "\n".join(leaderboard[i : i + 10])
            current_page = (i // 10) + 1
            total_page = (len(sorted_messages) // 10) + 1
            channel_name = f" #{channel.name}" if channel else ""
            member_name = f" @{member.global_name}" if member else ""
            footer = f"{current_page}/{total_page} {channel_name} {member_name}"
            embed = Embed.from_interaction(inter, description=description)
            embed.set_footer(text=footer)
            return embed

        embeds = [_create_embed(i) for i in range(0, len(leaderboard), 10)]
        await inter.send(embed=embeds[0], view=Paginator(embeds))

    @commands.slash_command()
    async def undo_delete(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Undo the last deletion or edit of a message in the channel (up to 5 minutes). {{UNDO_DELETE}}
        """
        await inter.response.defer(ephemeral=True)
        for m in self.bot.deleted_messages[::-1]:
            if m.channel.id == inter.channel.id:
                member = await inter.guild.fetch_member(m.author.id)
                webhook = await application_webhook(self.bot, m.channel)
                files = [await attachment.to_file() for attachment in m.attachments]
                webhook_message = await webhook.send(
                    m.content,
                    username=member.display_name,
                    avatar_url=member.display_avatar.url,
                    files=files,
                    wait=True,
                )
                embed = Embed.from_interaction(inter, description=webhook_message.jump_url)
                await inter.edit_original_response(embed=embed)
                return None
        else:
            raise Exception()  # TODO: add message

    @commands.message_command()
    async def undo_edit(self, inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
        """
        {{UNDO_EDIT}}
        """
        if not message.edited_at:
            raise Exception()  # TODO: add message
        await inter.response.defer(ephemeral=True)
        for m in self.bot.edited_messages[::-1]:
            if m.id == message.id:
                member = await inter.guild.fetch_member(m.author.id)
                webhook = await application_webhook(self.bot, m.channel)
                files = [await attachment.to_file() for attachment in m.attachments]
                webhook_message = await webhook.send(
                    m.content,
                    username=member.display_name,
                    avatar_url=member.display_avatar.url,
                    files=files,
                    wait=True,
                )
                embed = Embed.from_interaction(inter, description=webhook_message.jump_url)
                await inter.edit_original_response(embed=embed)
                return None
        else:
            raise Exception()  # TODO: add message


def setup(bot: Bot) -> None:
    bot.add_cog(Stalker(bot))
