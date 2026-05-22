from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
import asyncio
import logging

from services.firebase_service import firebase_service
from services.realtime_activity_logger import realtime_activity_logger
from api.routes import users as users_router
from api.routes import incidents as incidents_router
from api.routes import alerts as alerts_router
from api.routes import dashboard as dashboard_router
from api.routes import voice as voice_router
from api.routes import metrics as metrics_router
from agents.monitoring_agent import MonitoringAgent
from agents.pipeline import pipeline
from services.notification_queue import notification_queue

logger = logging.getLogger("main")

app = FastAPI(title="AapdaMitra API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # initialize Firebase
    try:
        await firebase_service.initialize(settings)
    except Exception:
        logger.exception("Failed to initialize firebase on startup")
    # initialize Realtime Activity Logger
    try:
        await realtime_activity_logger.initialize(settings)
    except Exception:
        logger.exception("Failed to initialize realtime activity logger on startup")
    # start monitoring loop
    try:
        monitor = MonitoringAgent()
        asyncio.create_task(monitor.run_monitoring_loop())
        logger.info("MonitoringAgent started")
    except Exception:
        logger.exception("Failed to start MonitoringAgent")
    # start pipeline orchestrator
    try:
        await pipeline.start()
    except Exception:
        logger.exception("Failed to start pipeline orchestrator")
    # start notification queue processor
    try:
        await notification_queue.start()
        logger.info("Notification queue processor started")
    except Exception:
        logger.exception("Failed to start notification queue processor")


app.include_router(users_router.router)
app.include_router(incidents_router.router)
app.include_router(alerts_router.router)
app.include_router(dashboard_router.router)
app.include_router(voice_router.router)
app.include_router(metrics_router.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
