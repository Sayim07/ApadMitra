import asyncio
import logging
from typing import Callable

from utils.retry_queue import AsyncQueueWorker, AsyncRetry
from services.firebase_service import firebase_service

logger = logging.getLogger("pipeline")


class PipelineOrchestrator:
    def __init__(self, concurrency: int = 2):
        self.started = False
        self.worker = AsyncQueueWorker(self._process_incident, concurrency=concurrency)
        self.retry = AsyncRetry(retries=3, base_delay=0.5, max_delay=8.0)

    async def start(self):
        if not self.started:
            await self.worker.start()
            self.started = True
            logger.info("PipelineOrchestrator started with concurrency=%s", self.worker.concurrency)

    async def stop(self):
        await self.worker.stop()
        self.started = False

    async def enqueue_incident(self, incident_id: str):
        await self.worker.enqueue(incident_id)

    async def _process_incident(self, incident_id: str):
        try:
            # Import agents lazily to avoid circular imports at module load
            from .verification_agent import VerificationAgent
            from .priority_agent import PriorityAgent
            from .alert_generation_agent import AlertGenerationAgent
            from .dispatch_agent import DispatchAgent

            verifier = VerificationAgent()
            prio = PriorityAgent()
            ag = AlertGenerationAgent()
            disp = DispatchAgent()

            # Run agents sequentially with retries for robustness
            await self.retry.run(verifier.verify_incident, incident_id)
            await self.retry.run(prio.calculate_priority, incident_id)
            await self.retry.run(ag.generate_all_alerts, incident_id)
            await self.retry.run(disp.dispatch_all, incident_id)

            logger.info("Pipeline completed for incident %s", incident_id)
        except Exception:
            logger.exception("Pipeline failed for incident %s", incident_id)
            # mark incident as pipeline_failed
            try:
                await firebase_service.update_incident(incident_id, {"pipeline_status": "FAILED"})
            except Exception:
                logger.exception("Failed to mark incident pipeline failure in Firestore")


pipeline = PipelineOrchestrator()
