from collections import defaultdict

import disnake
from disnake.ext import commands

from bot import Bot
from bot.ext import application_webhook
from bot.services import G4F

DEFAULT_PROMPT = "Você está em um servidor do Discord. Responda de forma curta e objetiva."


class Chatbot(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.g4fs: dict = defaultdict(lambda: dict)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot:
            return None
        if self.bot.user in message.mentions:
            nick = None
        elif message.content.startswith("@"):
            nick = message.content.removeprefix("@").lower().split()[0]
        else:
            return None
        chatbot = await self.bot.db.chatbot.find_first(
            where={"guild_id": message.guild.id, "nick": nick},
        )
        if not chatbot:
            return None
        if chatbot.nick not in self.g4fs[message.channel.id]:
            self.g4fs[message.channel.id][chatbot.nick] = G4F(history_size=30)
        g4f = self.g4fs[message.channel.id][chatbot.nick]
        g4f.prompt = f"{chatbot.prompt} {DEFAULT_PROMPT}"
        text = f"[{message.created_at}] {message.author.global_name}): {message.content}"
        content = await g4f.chat_completions(text)
        webhook = await application_webhook(self.bot, message.channel)
        await webhook.send(
            content,
            username=chatbot.name or message.guild.name,
            avatar_url=chatbot.avatar_url or message.guild.icon.url,
        )


def setup(bot: Bot) -> None:
    bot.add_cog(Chatbot(bot))
