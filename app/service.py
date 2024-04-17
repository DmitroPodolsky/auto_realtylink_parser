import asyncio
import json
import math
import re
from concurrent.futures import ProcessPoolExecutor

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger

from app.config import settings
from app.utils import fetch_get_html_from_url
from app.utils import fetch_post_html_from_url


async def parse_apartment_urls() -> list[dict[str, str]]:
    """
    Parse apartment urls

    Returns:
        list of apartment urls with html content
    """

    async with aiohttp.ClientSession() as session:
        urls = []
        logger.info("Fetching Page URLs")
        tasks = [
            fetch_post_html_from_url(session, page_number)
            for page_number in range(math.ceil(10 / 20))
        ]
        logger.info(f"Fetching {settings.RECORDS} URLs")
        for page in await asyncio.gather(*tasks):
            data = json.loads(page)
            soup = BeautifulSoup(data["d"]["Result"]["html"], "html.parser")

            for apartment in soup.find_all("div", itemscope=True):
                if "price" in apartment.get("class", []):
                    continue

                link = apartment.find("a", class_="a-more-detail")
                if len(urls) == settings.RECORDS:
                    break

                urls.append(settings.HOST + link["href"])
        tasks = [fetch_get_html_from_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)


def parse_apartment_sync(
    html: dict[str, str]
) -> dict[str, str | int | list[str] | None]:
    """
    Parses apartment information from HTML content.

    Args:
        html: The HTML content from which to parse apartment information. with url as key and html content as value

    Returns:
        A dictionary containing apartment information.
    """
    url = list(html.keys())[0]
    soup = BeautifulSoup(html[url], "html.parser")
    price = soup.find("span", id="BuyPrice").text
    address_parts = soup.find("h2", itemprop="address").get_text(strip=True).split(", ")
    address = address_parts[0]
    region = ", ".join(address_parts[1:])
    title = soup.find("span", {"data-id": "PageTitle"}).get_text(strip=True)
    image_elements = soup.find_all("img")
    image_urls = [img["src"] for img in image_elements if "src" in img.attrs]

    area = None
    try:
        for container in soup.find_all("div", class_="carac-container"):
            if container.find("div", class_="carac-title").get_text(strip=True) in [
                "Floor Area",
                "Lot Size",
            ]:
                area = container.find("span").get_text(strip=True)
                break
    except AttributeError:
        pass

    try:
        description = soup.find("div", itemprop="description").get_text(strip=True)
    except AttributeError:
        description = None

    try:
        bedroom_counts = re.search(
            r"\d+", soup.find("div", class_="cac").get_text(strip=True)
        )
        bathroom_counts = re.search(
            r"\d+", soup.find("div", class_="sdb").get_text(strip=True)
        )
        rooms_counts = int(bathroom_counts.group(0)) + int(bedroom_counts.group(0))
    except AttributeError:
        rooms_counts = None

    logger.info(f"Successfully parsed {url}")
    return {
        "url": url,
        "price": price,
        "description": description,
        "address": address,
        "region": region,
        "title": title,
        "rooms_counts": rooms_counts,
        "area": area,
        "image_urls": image_urls,
    }


async def parse_apartments_in_parallel(htmls: list[str]) -> None:
    """
    Parses smartphone information from multiple HTMLs in parallel using a process pool.

    Args:
        htmls: A list of HTML strings with url as key which apartment information will be parsed.
    """
    logger.info("Parsing Apartments information in parallel")
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as pool:
        tasks = [
            loop.run_in_executor(pool, parse_apartment_sync, html) for html in htmls
        ]
        return await asyncio.gather(*tasks)
