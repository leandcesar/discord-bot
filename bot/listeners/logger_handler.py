import disnake
from disnake.ext import commands

from bot import Bot
from bot.ext import Embed


class LoggerHandler(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def sync_messages(self) -> None:
        for guild in self.bot.guilds:
            for text_channel in guild.text_channels:
                channel = await self.bot.db.channel.find_first(where={"id": text_channel.id})
                after = channel.synced_at if channel else None
                async for m in text_channel.history(limit=None, after=after, oldest_first=True):
                    await self.on_message(m)
                await self.bot.db.channel.update(
                    where={"id": text_channel.id}, data={"synced_at": self.bot.started_at}
                )

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message) -> None:
        if after.author.bot:
            return None
        self.bot.edited_messages.append(before)
        await self.bot.db.message.upsert(
            where={"id": after.id},
            data={
                "create": {
                    "id": after.id,
                    "edited_at": after.edited_at,
                    "channel": {"connect": {"id": after.channel.id}},
                    "user": {"connect": {"id": after.author.id}},
                },
                "update": {"edited_at": after.edited_at},
            },
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message) -> None:
        if message.author.bot:
            return None
        self.bot.deleted_messages.append(message)
        await self.bot.db.message.upsert(
            where={"id": message.id},
            data={
                "create": {
                    "id": message.id,
                    "deleted_at": message.edited_at,
                    "channel": {"connect": {"id": message.channel.id}},
                    "user": {"connect": {"id": message.author.id}},
                },
                "update": {"deleted_at": message.edited_at},
            },
        )

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[disnake.Message]) -> None:
        for message in messages:
            await self.on_message_delete(message)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot:
            return None
        self.bot.logger.debug(
            f"{message.guild} ({message.guild.id}) "
            f"#{message.channel} ({message.channel.id}) "
            f"@{message.author} ({message.author.id}): "
            f"{message.content!r} ({message.id})"
        )
        await self.bot.db.guild.upsert(
            where={"id": message.guild.id},
            data={
                "create": {"id": message.guild.id},
                "update": {},
            },
        )
        await self.bot.db.channel.upsert(
            where={"id": message.channel.id},
            data={
                "create": {"id": message.channel.id, "guild": {"connect": {"id": message.guild.id}}},
                "update": {},
            },
        )
        await self.bot.db.user.upsert(
            where={"id": message.author.id},
            data={
                "create": {"id": message.author.id, "guild": {"connect": {"id": message.guild.id}}},
                "update": {},
            },
        )
        await self.bot.db.message.upsert(
            where={"id": message.id},
            data={
                "create": {
                    "id": message.id,
                    "created_at": message.created_at,
                    "updated_at": message.created_at,
                    "channel": {"connect": {"id": message.channel.id}},
                    "user": {"connect": {"id": message.author.id}},
                },
                "update": {},
            },
        )

    @commands.Cog.listener()
    async def on_slash_command(self, inter: disnake.CommandInteraction) -> None:
        self.bot.logger.info(
            f"{inter.guild} ({inter.guild.id}) "
            f"#{inter.channel} ({inter.channel.id}) "
            f"@{inter.author} ({inter.author.id}): "
            f"/{inter.application_command.qualified_name} {inter.options}"
        )

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction) -> None:
        self.bot.logger.info(
            f"{inter.guild} ({inter.guild.id}) "
            f"#{inter.channel} ({inter.channel.id}) "
            f"@{inter.author} ({inter.author.id}): "
            f"{inter.data}"
        )

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.CommandInteraction, e: commands.CommandError) -> None:
        self.bot.logger.error(
            f"{inter.guild} ({inter.guild.id}) "
            f"#{inter.channel} ({inter.channel.id}) "
            f"@{inter.author} ({inter.author.id}): "
            f"/{inter.application_command.qualified_name} {inter.options} "
            f"{e}",
            exc_info=e,
        )
        embed = Embed.from_interaction(inter, description=str(e), color=disnake.Color.red())
        await inter.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(LoggerHandler(bot))
