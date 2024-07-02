import asyncio

import disnake
from disnake.ext import commands

from bot import Bot
from bot.ext import URL, Embed, checks
from bot.services import pil

DEFAULT_NICK = "@einstein"
DEFAULT_NAME = "Albert Einstein"
DEFAULT_AVATAR_URL = "https://cdn.discordapp.com/embed/avatars/0.png"
DEFAULT_PROMPT = "Você é Albert Einstein, o icônico físico teórico"


class Guild(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.has_permissions(manage_emojis_and_stickers=True)
    @commands.slash_command()
    async def sticker(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Manage server stickers. {{STICKER}}
        """

    @sticker.sub_command()
    async def sticker_add(
        self,
        inter: disnake.GuildCommandInteraction,
        name: str,
        emoji: str,
        image_url: URL | None = None,
        image_file: disnake.Attachment | None = None,
    ) -> None:
        """
        Add a sticker to the server. {{STICKER_ADD}}

        Parameters
        ----------
        name: Name {{NAME}}
        emoji: Emoji {{EMOJI}}
        image_url: Image URL {{IMAGE_URL}}
        image_file: Image attachment {{IMAGE_FILE}}
        """
        checks.one_of(image_file, image_url)
        await inter.response.defer()
        image: disnake.Attachment | URL = image_file or image_url
        image_binary = await image.read()
        image_bytes = pil.resize_image(image_binary, width=320, height=320)
        file = disnake.File(image_bytes, filename="sticker.png")
        guild_sticker = await inter.guild.create_sticker(name=name, emoji=emoji, file=file)
        file = await guild_sticker.to_file()
        embed = Embed.from_interaction(inter, color=disnake.Color.green())
        embed.set_image(file=file)
        await inter.edit_original_response(embed=embed)
        file.close()

    @sticker.sub_command()
    async def sticker_remove(self, inter: disnake.GuildCommandInteraction, sticker: disnake.GuildSticker) -> None:
        """
        Remove a sticker from the server. {{STICKER_REMOVE}}

        Parameters
        ----------
        sitcker: Sticker {{STICKER}}
        """
        guild_sticker = await inter.guild.fetch_sticker(sticker.id)
        file = await guild_sticker.to_file()
        embed = Embed.from_interaction(inter, color=disnake.Color.red())
        embed.set_image(file=file)
        await guild_sticker.delete()
        await inter.send(embed=embed)
        file.close()

    @sticker_remove.autocomplete("sticker")
    async def sticker_name_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
        return [sticker.name for sticker in inter.guild.stickers if name.lower() in sticker.name.lower()][:25]

    @commands.has_permissions(manage_emojis=True)
    @commands.slash_command()
    async def emote(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Manage server emotes. {{EMOTE}}
        """

    @emote.sub_command()
    async def emote_add(
        self,
        inter: disnake.GuildCommandInteraction,
        name: str,
        image_url: URL | None = None,
        image_file: disnake.Attachment | None = None,
    ) -> None:
        """
        Add an emote to the server. {{EMOTE_ADD}}

        Parameters
        ----------
        name: Name {{NAME}}
        image_url: Image URL {{IMAGE_URL}}
        image_file: Image attachment {{IMAGE_FILE}}
        """
        checks.one_of(image_file, image_url)
        await inter.response.defer()
        image: disnake.Attachment | URL = image_file or image_url
        image_binary = await image.read()
        image_bytes = pil.resize_image(image_binary, width=128, height=128)
        image_binary = image_bytes.read()
        guild_emote = await inter.guild.create_custom_emoji(name=name, image=image_binary)
        file = await guild_emote.to_file()
        embed = Embed.from_interaction(inter, color=disnake.Color.green())
        embed.set_image(file=file)
        await inter.edit_original_response(embed=embed)
        file.close()

    @emote.sub_command()
    async def emote_remove(self, inter: disnake.GuildCommandInteraction, emote: disnake.PartialEmoji) -> None:
        """
        Remove an emote from the server. {{EMOTE_REMOVE}}

        Parameters
        ----------
        emote: Emote {{EMOTE}}
        """
        guild_emote = await inter.guild.fetch_emoji(emote.id)
        file = await guild_emote.to_file()
        embed = Embed.from_interaction(inter, color=disnake.Color.red())
        embed.set_image(file=file)
        await guild_emote.delete()
        await inter.send(embed=embed)
        file.close()

    @emote_remove.autocomplete("emote")
    async def emote_name_autocomplete(self, inter: disnake.GuildCommandInteraction, name: str) -> list[str]:
        return [emoji.name for emoji in inter.guild.emojis if name.lower() in emoji.name.lower()][:25]

    @commands.slash_command()
    async def chatbot(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Manage your server chatbots. {{CHATBOT}}
        """

    @chatbot.sub_command(name="add")
    async def chatbot_add(self, inter: disnake.GuildCommandInteraction) -> None:
        """
        Add a chatbot to the server. {{CHATBOT_ADD}}
        """
        is_admin = bool(inter.author.guild_permissions.administrator)

        await inter.response.send_modal(
            title="Chatbot",
            custom_id="create_chatbot",
            components=[
                disnake.ui.TextInput(
                    label="Nick",
                    placeholder=DEFAULT_NICK,
                    custom_id="nick",
                    style=disnake.TextInputStyle.single_line,
                    min_length=3,
                    max_length=20,
                    required=(not is_admin),  # If nick is None, then it will work by mentioning bot
                ),
                disnake.ui.TextInput(
                    label="Name",
                    placeholder=DEFAULT_NAME,
                    custom_id="name",
                    style=disnake.TextInputStyle.single_line,
                    min_length=3,
                    max_length=20,
                    required=False,
                ),
                disnake.ui.TextInput(
                    label="Icon (URL)",
                    placeholder=DEFAULT_AVATAR_URL,
                    custom_id="avatar_url",
                    style=disnake.TextInputStyle.single_line,
                    min_length=10,
                    max_length=200,
                    required=False,
                ),
                disnake.ui.TextInput(
                    label="Prompt",
                    placeholder=DEFAULT_PROMPT,
                    custom_id="prompt",
                    style=disnake.TextInputStyle.multi_line,
                    min_length=16,
                    max_length=2048,
                ),
            ],
        )

        try:
            modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "create_chatbot" and i.author.id == inter.author.id,
                timeout=600,
            )
        except asyncio.TimeoutError:
            return None

        nick = modal_inter.text_values["nick"].removeprefix("@").lower().split()[0]
        name = modal_inter.text_values["name"]
        avatar_url = modal_inter.text_values["avatar_url"]
        prompt = modal_inter.text_values["prompt"]
        chatbot = await self.bot.db.chatbot.create(
            data={
                "name": name,
                "nick": nick,
                "prompt": prompt,
                "avatar_url": avatar_url,
                "guild_id": inter.guild.id,
                "user_id": inter.author.id,
            },
        )
        embed = Embed.from_interaction(
            inter,
            title=f"{name} (`@{nick}`)",
            description=chatbot.prompt,
            color=disnake.Color.green(),
        )
        await modal_inter.response.send_message(embed=embed, ephemeral=True)

    @chatbot.sub_command(name="remove")
    async def chatbot_remove(self, inter: disnake.GuildCommandInteraction, nick: str) -> None:
        """
        Remove a chatbot from the server. {{CHATBOT_REMOVE}}

        Parameters
        ----------
        nick: Chatbot nick {{CHATBOT_NICK}}
        """
        is_admin = bool(inter.author.guild_permissions.administrator)

        await self.bot.db.chatbot.delete_many(
            where={
                "guild_id": inter.guild.id,
                "user_id": inter.author.id if not is_admin else None,
                "nick": nick,
            },
        )
        embed = Embed.from_interaction(inter, description=nick, color=disnake.Color.red())
        await inter.send(embed=embed, ephemeral=True)

    @chatbot_remove.autocomplete("nick")
    async def chatbot_remove_nick_autocomplete(self, inter: disnake.GuildCommandInteraction, nick: str) -> list[str]:
        is_admin = bool(inter.author.guild_permissions.administrator)

        chatbots = await self.bot.db.chatbot.find_many(
            where={
                "guild_id": inter.guild.id,
                "user_id": inter.author.id if not is_admin else None,
            },
        )
        return [chatbot.nick for chatbot in chatbots if nick.lower() in chatbot.nick.lower()][:25]


def setup(bot: Bot) -> None:
    bot.add_cog(Guild(bot))
