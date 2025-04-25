import disnake
from disnake.ext import commands
from disnake.ext.commands.errors import MissingRequiredArgument
from disnake_plugins import Plugin

from src import config
from src.api.groq import Groq
from src.bot import Bot as _Bot
from src.util.message import stringfy


class Bot(_Bot):
    groq: Groq


plugin = Plugin[Bot]()


@plugin.load_hook()
async def ai_load_hook() -> None:
    plugin.bot.groq = Groq(config.Groq.api_key)


@plugin.unload_hook()
async def ai_unload_hook() -> None:
    await plugin.bot.groq.close()


async def _summarize_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction,
) -> None:
    messages = await inter.channel.history(limit=100).flatten()
    messages = messages[1:][::-1]
    messages_as_text = "\n".join([await stringfy(message) for message in messages if not message.author.bot])
    content = await plugin.bot.groq.chat_completions(
        prompt=(
            "Resuma as mensagens da conversa de um grupo de amigos do Discord."
            " Em tópicos, trazendo os principais assuntos."
            " Em Português-BR, linguagem informal de internet."
            " Mantenha o tom, o humor e a ironia."
            " Elabore o resumo de cada tópico incluindo os principais participantes, quando possível."
            " Não adicione introdução nem conclusão."
            " Não adicione tópicos vagos, genéricos ou irrelevantes."
        ),
        message=messages_as_text,
        model=config.Groq.chat_completations_model,
        temperature=config.Groq.temperature,
        max_completion_tokens=config.Groq.max_completion_tokens,
    )
    await plugin.bot.reply(inter, content)


@commands.cooldown(2, 600, commands.BucketType.channel)
@plugin.command(name="summarize", aliases=["resumo"], description="Summarize the recent conversation in the chat.")
async def summarize_prefix_command(ctx: commands.Context[Bot]) -> None:
    await _summarize_command(ctx)


@commands.cooldown(2, 600, commands.BucketType.channel)
@plugin.slash_command(name="summarize")
async def summarize_slash_command(inter: disnake.ApplicationCommandInteraction) -> None:
    """
    Summarize the recent conversation in the chat.
    """
    await inter.response.defer()
    await _summarize_command(inter)


async def transcribe(message: disnake.Message) -> disnake.Message | None:
    for attachment in message.attachments:
        if attachment.filename.split("?")[0].endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a")):
            await message.add_reaction(config.Emoji.loading)
            audio_data = await attachment.read()
            content = await plugin.bot.groq.audio_transcriptions(
                audio_data=audio_data,
                audio_filename=attachment.filename,
                model=config.Groq.transcriptions_model,
                language="pt",
            )
            await message.remove_reaction(config.Emoji.loading, member=plugin.bot.user)
            return await plugin.bot.reply(message, f"✍\n> {content}", mention_author=False)
    return None


@commands.cooldown(2, 600, commands.BucketType.user)
@plugin.message_command(name="Transcribe")
async def transcribe_message_command(inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
    await inter.response.defer()
    if await transcribe(message) is None:
        raise MissingRequiredArgument("No audio file found in the message.")


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    await transcribe(message)


setup, teardown = plugin.create_extension_handlers()
