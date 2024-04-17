import asyncio
import json
import time

from loguru import logger

from app.config import settings
from app.service import parse_apartment_urls
from app.service import parse_apartments_in_parallel


async def main():
    """Main function to run the parser."""
    time_start = time.time()

    data = await parse_apartments_in_parallel(await parse_apartment_urls())

    file_path = settings.DATA_DIR / "output.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    logger.success(f"Data has been successfully saved to {file_path}")
    logger.info(f"Time taken: {time.time() - time_start:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
