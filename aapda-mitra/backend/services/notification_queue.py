import asyncio
import logging
import time
from typing import Dict, Any, List, Optional

from services.firebase_service import firebase_service
from utils.retry_queue import AsyncRetry
from services.notification_service import SMSService, EmailService
from config.settings import settings
import json

logger = logging.getLogger("notification_queue")


class NotificationQueueService:
    def __init__(self, poll_interval: float = 2.0, concurrency: int = 3):
        self.poll_interval = poll_interval
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._in_memory_queue: List[Dict[str, Any]] = []
        self._sms = SMSService(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER)
        self._email = EmailService(settings.SENDGRID_API_KEY)
        self._redis = None
        self._use_redis = bool(settings.REDIS_URL)
        if self._use_redis:
            try:
                import redis.asyncio as aioredis  # type: ignore
                self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                self._redis = None
                self._use_redis = False

    async def enqueue(self, item: Dict[str, Any]) -> str:
        """Persist the notification to Redis (if configured), Firestore, or process immediately in-memory."""
        # Prefer Redis if configured
        if self._use_redis and self._redis is not None:
            try:
                payload = json.dumps(item)
                await self._redis.lpush("notification_queue", payload)
                return f"redis-{int(time.time()*1000)}"
            except Exception:
                logger.exception("Failed to enqueue to Redis; falling back")

        if getattr(firebase_service, 'db', None) is None:
            # no firestore available (tests/local) — process immediately for determinism
            try:
                await self._process_item(item)
                return f"local-{int(time.time()*1000)}"
            except Exception:
                logger.exception("Failed to process in-memory notification")
                return f"local-failed-{int(time.time()*1000)}"

        def _write():
            col = firebase_service.db.collection("notification_queue")
            doc_ref = col.add({**item, "status": "PENDING", "created_at": firestore.SERVER_TIMESTAMP})[0]
            return doc_ref.id

        try:
            # import firestore symbol lazily
            from firebase_admin import firestore as _fs
            firestore = _fs
        except Exception:
            firestore = None

        try:
            doc_id = await asyncio.to_thread(_write)
            return doc_id
        except Exception:
            logger.exception("Failed to enqueue notification to Firestore, falling back to in-memory processing")
            try:
                await self._process_item(item)
                return f"fallback-{int(time.time()*1000)}"
            except Exception:
                return f"failed-{int(time.time()*1000)}"

    async def _process_item(self, item: Dict[str, Any]):
        """Send a single notification item with retries."""
        retry = AsyncRetry(retries=3, base_delay=0.5, max_delay=8.0)
        channel = item.get("channel")
        to = item.get("to")
        if channel == "sms":
            await retry.run(self._sms.send_sms, to, item.get("message", ""))
        elif channel == "email":
            await retry.run(self._email.send_email, to, item.get("subject", "Alert"), item.get("html", item.get("message", "")))
        else:
            logger.warning("Unknown channel for notification: %s", channel)

    async def _poll_and_process(self):
        # Use Redis if available, otherwise poll Firestore
        while self.running:
            try:
                if self._use_redis and self._redis is not None:
                    try:
                        # BRPOP with timeout
                        res = await self._redis.brpop("notification_queue", timeout=1)
                        if res:
                            _key, payload = res
                            try:
                                data = json.loads(payload)
                            except Exception:
                                data = None
                            if data:
                                try:
                                    await self._process_item(data)
                                    alert_id = data.get("alert_id")
                                    if alert_id:
                                        try:
                                            await firebase_service.update_alert_status(alert_id, "SENT")
                                        except Exception:
                                            pass
                                except Exception:
                                    logger.exception("Failed processing redis notification")
                        continue
                    except Exception:
                        logger.exception("Redis notification processing failed, falling back to Firestore")

                if getattr(firebase_service, 'db', None) is None:
                    await asyncio.sleep(self.poll_interval)
                    continue

                def _fetch():
                    col = firebase_service.db.collection("notification_queue")
                    q = col.where("status", "==", "PENDING").limit(20).stream()
                    return [(d.id, d.to_dict()) for d in q]

                rows = await asyncio.to_thread(_fetch)
                for doc_id, data in rows:
                    # mark as in-progress
                    try:
                        def _mark():
                            doc_ref = firebase_service.db.collection("notification_queue").document(doc_id)
                            doc_ref.update({"status": "IN_PROGRESS", "started_at": firestore.SERVER_TIMESTAMP})

                        from firebase_admin import firestore as _fs
                        firestore = _fs
                        await asyncio.to_thread(_mark)
                    except Exception:
                        # could be processed by another worker
                        continue

                    try:
                        await self._process_item(data)
                        # mark done
                        def _done():
                            firebase_service.db.collection("notification_queue").document(doc_id).update({"status": "DONE", "completed_at": firestore.SERVER_TIMESTAMP})

                        await asyncio.to_thread(_done)
                        # update corresponding alert if present
                        try:
                            alert_id = data.get("alert_id")
                            if alert_id:
                                await firebase_service.update_alert_status(alert_id, "SENT")
                        except Exception:
                            pass
                    except Exception:
                        logger.exception("Failed processing notification %s", doc_id)
                        try:
                            def _fail():
                                firebase_service.db.collection("notification_queue").document(doc_id).update({"status": "FAILED", "completed_at": firestore.SERVER_TIMESTAMP})

                            await asyncio.to_thread(_fail)
                        except Exception:
                            pass

            except Exception:
                logger.exception("Error in notification processor loop")

            await asyncio.sleep(self.poll_interval)

    async def start(self):
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._poll_and_process())

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass


notification_queue = NotificationQueueService()
