import random

from aiohttp import ClientSession

from app.config import HEADERS_API_URL
from app.config import settings
from app.config import USER_AGENTS


async def fetch_get_html_from_url(session: ClientSession, url: str) -> dict[str, str]:
    """
    Fetches HTML content from the specified URL asynchronously.

    Args:
        session: The aiohttp ClientSession object.
        url: The URL from which to fetch HTML content.

    Returns:
        HTML content fetched from the URL.
    """
    HEADERS_API_URL["User-Agent"] = USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)]

    async with session.get(url, headers=HEADERS_API_URL) as response:
        return {url: await response.text()}


async def fetch_post_html_from_url(session: ClientSession, page: int) -> str:
    """
    Fetches HTML content from the specified URL asynchronously.

    Args:
        session: The aiohttp ClientSession object.
        page: The page number to fetch HTML content from.

    Returns:
        HTML content fetched from the URL.
    """
    payload = {"startPosition": page}
    HEADERS_API_URL["User-Agent"] = USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)]

    async with session.post(
        settings.API_URL, headers=HEADERS_API_URL, json=payload
    ) as response:
        return await response.text()
