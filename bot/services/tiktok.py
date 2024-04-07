import re
from io import BytesIO

import aiohttp
import browser_cookie3

HEADERS = {
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/56.0.2924.87 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "referer": "https://www.tiktok.com/",
}


def save_video(video_bytes: bytes) -> BytesIO:
    video_binary = BytesIO(video_bytes)
    video_binary.seek(0)
    return video_binary


def get_cookies(browser: str = "chrome") -> dict[str, str]:
    cookies = getattr(browser_cookie3, browser)(domain_name="www.tiktok.com")
    return {cookie.name: cookie.value for cookie in cookies}


def get_download_video_url(html: str) -> str | None:
    match = re.search(r"\"downloadAddr\":\"(https:[^\"]+)", html)
    if match:
        return match.group(1).replace(r"\u002F", "/")
    return None


async def download_video(video_url: str, *, browser: str = "chrome") -> BytesIO | None:
    cookies = get_cookies(browser)
    async with aiohttp.ClientSession() as session:
        async with session.get(video_url, headers=HEADERS, cookies=cookies) as response:
            response.raise_for_status()
            html = await response.text()
            download_video_url = get_download_video_url(html)
        if not download_video_url:
            raise ValueError(f"Unable to find the video download URL for {video_url!r}")
        async with session.get(
            download_video_url, headers=HEADERS, cookies=cookies, allow_redirects=True
        ) as response:
            response.raise_for_status()
            video_data = await response.read()
        return save_video(video_data)
    return None
