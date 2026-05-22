import asyncio
import time
from typing import Optional, Dict, Any
import httpx
import logging

logger = logging.getLogger("http_utils")


async def request_json(url: str, method: str = "GET", params: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: int = 10, retries: int = 3, backoff_factor: float = 0.5) -> Optional[Dict[str, Any]]:
    attempt = 0
    while attempt <= retries:
        try:
            async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
                resp = await client.request(method, url, params=params)
                if resp.status_code == 200:
                    try:
                        return resp.json()
                    except Exception:
                        return {"text": resp.text}
                else:
                    logger.warning("HTTP non-200 %s for %s", resp.status_code, url)
        except Exception as e:
            logger.exception("http request error %s %s", url, e)

        attempt += 1
        await asyncio.sleep(backoff_factor * (2 ** (attempt - 1)))

    return None
