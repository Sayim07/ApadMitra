import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger("retry_queue")


class AsyncRetry:
    def __init__(self, retries: int = 3, base_delay: float = 0.5, max_delay: float = 10.0):
        self.retries = retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def run(self, func: Callable[..., Any], *args, **kwargs):
        attempt = 0
        while True:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt > self.retries:
                    logger.exception("Operation failed after retries: %s", e)
                    raise
                delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                logger.warning("Operation failed (attempt %s). Retrying in %s seconds...", attempt, delay)
                await asyncio.sleep(delay)


class AsyncQueueWorker:
    def __init__(self, worker_fn: Callable[[Any], Any], concurrency: int = 3):
        self.queue = asyncio.Queue()
        self.worker_fn = worker_fn
        self.concurrency = concurrency
        self._workers = []

    async def start(self):
        for _ in range(self.concurrency):
            self._workers.append(asyncio.create_task(self._run()))

    async def _run(self):
        while True:
            item = await self.queue.get()
            try:
                await self.worker_fn(item)
            except Exception:
                logger.exception("Error processing queue item")
            finally:
                self.queue.task_done()

    async def stop(self):
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)

    async def enqueue(self, item: Any):
        await self.queue.put(item)
