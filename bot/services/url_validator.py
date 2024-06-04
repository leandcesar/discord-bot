import re

REGEX_DISCORD_CDN_URL = re.compile(r"https?://cdn.discordapp.com/\S+(\.jpg|\.png|\.jpeg)\S*")


def is_valid_discord_url(url: str) -> bool:
    find_list: list[str] = REGEX_DISCORD_CDN_URL.findall(url)
    return len(find_list) > 0
