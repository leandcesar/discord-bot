from __future__ import annotations

import re

import disnake

__all__ = ("fetch_assets_content", "fetch_assets_url", "fetch_emojis")


async def fetch_emojis(message: disnake.Message, /) -> list[disnake.Emoji]:
    emojis_ids = re.findall(r"<a?:\w+:(\d{16,19})>", message.content)
    return [await message.guild.fetch_emoji(int(emoji_id)) for emoji_id in set(emojis_ids)]


async def fetch_assets_content(message: disnake.Message, /) -> list[bytes]:
    datas = []
    datas.extend([await x.read() for x in message.attachments])
    datas.extend([await x.read() for x in await fetch_emojis(message)])
    datas.extend([await x.read() for x in message.stickers])
    return datas


async def fetch_assets_url(message: disnake.Message, /) -> list[str]:
    datas = []
    datas.extend([x.url for x in message.attachments])
    datas.extend([x.url for x in await fetch_emojis(message)])
    datas.extend([x.url for x in message.stickers])
    return datas
