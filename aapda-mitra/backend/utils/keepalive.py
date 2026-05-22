import asyncio
import logging
import aiohttp

logger = logging.getLogger("keepalive")


async def keepalive_loop(url: str, interval_seconds: int = 14 * 60):
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, timeout=10) as resp:
                    logger.info("Keepalive ping %s -> %s", url, resp.status)
            except Exception:
                logger.exception("Keepalive ping failed")
            await asyncio.sleep(interval_seconds)
