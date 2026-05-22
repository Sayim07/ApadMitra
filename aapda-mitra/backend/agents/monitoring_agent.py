import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, Any, List
import time
from datetime import datetime
import httpx
import math

from services.firebase_service import firebase_service
from config.settings import settings

logger = logging.getLogger("monitoring_agent")


@dataclass
class RawIncidentSignal:
    source_type: str
    raw_text: str
    location_hint: str
    latitude: float
    longitude: float
    disaster_type_hint: str
    confidence: float
    timestamp: float
    metadata: Dict[str, Any]


class MonitoringAgent:
    def __init__(self):
        self.role = "Disaster Monitoring Specialist"
        self.goal = "Continuously scan data sources for disaster signals"

    async def monitor_weather_apis(self) -> List[RawIncidentSignal]:
        results: List[RawIncidentSignal] = []
        # sentinel locations (lat, lng, name) — can be extended or loaded from config
        sentinels = [
            (28.7041, 77.1025, "Delhi"),
            (19.0760, 72.8777, "Mumbai"),
            (13.0827, 80.2707, "Chennai"),
            (22.5726, 88.3639, "Kolkata"),
            (12.9716, 77.5946, "Bengaluru"),
            (17.3850, 78.4867, "Hyderabad"),
            (18.5204, 73.8567, "Pune"),
        ]

        try:
            for lat, lng, name in sentinels:
                try:
                    url = f"{settings.OPEN_METEO_BASE_URL}/forecast?latitude={lat}&longitude={lng}&hourly=precipitation&forecast_days=1"
                    data = await request_json(url, timeout=10, retries=2)
                    if not data:
                        continue
                    hourly = data.get("hourly", {})
                    prec = hourly.get("precipitation", [])
                    max_prec = max(prec) if prec else 0
                    if max_prec >= settings.RAINFALL_THRESHOLD_MM:
                        signal = RawIncidentSignal(
                            source_type="OPEN_METEO_RAINFALL",
                            raw_text=f"heavy rainfall detected {max_prec} mm in forecast at {name}",
                            location_hint=name,
                            latitude=lat,
                            longitude=lng,
                            disaster_type_hint="FLOOD",
                            confidence=min(100.0, 40.0 + max_prec / 2.0),
                            timestamp=float(datetime.utcnow().timestamp()),
                            metadata={"max_precipitation": max_prec},
                        )
                        results.append(signal)
                except Exception:
                    logger.exception("error checking sentinel %s", name)
        except Exception:
            logger.exception("monitor_weather_apis error")

        return results

    async def monitor_earthquake_api(self) -> List[RawIncidentSignal]:
        results: List[RawIncidentSignal] = []
        try:
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
            data = await request_json(url, timeout=10, retries=2)
            if not data:
                return results
                for feat in data.get("features", []):
                    props = feat.get("properties", {})
                    geom = feat.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])
                    mag = props.get("mag") or 0
                    place = props.get("place") or ""
                    ts = props.get("time") or int(time.time() * 1000)
                    # filter by magnitude threshold
                    if mag and mag >= settings.EARTHQUAKE_MAGNITUDE_THRESHOLD:
                        signal = RawIncidentSignal(
                            source_type="USGS_EARTHQUAKE",
                            raw_text=f"earthquake magnitude {mag} at {place}",
                            location_hint=place,
                            latitude=float(coords[1]),
                            longitude=float(coords[0]),
                            disaster_type_hint="EARTHQUAKE",
                            confidence=min(100.0, 50.0 + (mag * 10)),
                            timestamp=float(ts) / 1000.0,
                            metadata={"mag": mag, "url": props.get("url")},
                        )
                        results.append(signal)
        except Exception:
            logger.exception("monitor_earthquake_api error")
        return results

    async def monitor_fire_hotspots(self) -> List[RawIncidentSignal]:
        results: List[RawIncidentSignal] = []
        # NASA FIRMS provides JSON/CSV feeds for hotspots. Attempt a simple JSON query if key available.
        if not settings.NASA_FIRMS_API_KEY:
            return results
        try:
            # Example FIRMS endpoint (may require account access) — using a generic endpoint for recent MODIS/VIIRS
            url = f"https://firms.modaps.eosdis.nasa.gov/api/alert/csv?key={settings.NASA_FIRMS_API_KEY}&limit=50"
            # request_json returns dict/json; we need raw text for CSV, so use httpx with retry fallback
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(url)
                if r.status_code != 200:
                    return results
                text = r.text
                # parse CSV lines (skip header)
                lines = [ln for ln in text.splitlines() if ln.strip()]
                if len(lines) <= 1:
                    return results
                header = lines[0].split(',')
                for ln in lines[1:50]:
                    parts = ln.split(',')
                    try:
                        # FIRMS CSV typically: latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5
                        lat = float(parts[0])
                        lon = float(parts[1])
                        confidence_raw = parts[9] if len(parts) > 9 else ""
                        try:
                            conf = float(confidence_raw)
                        except Exception:
                            conf = 75.0
                        if conf >= settings.FIRE_CONFIDENCE_THRESHOLD:
                            signal = RawIncidentSignal(
                                source_type="NASA_FIRMS",
                                raw_text="fire hotspot detected",
                                location_hint="",
                                latitude=lat,
                                longitude=lon,
                                disaster_type_hint="FIRE",
                                confidence=conf,
                                timestamp=float(datetime.utcnow().timestamp()),
                                metadata={"source_line": ln},
                            )
                            results.append(signal)
                    except Exception:
                        continue
        except Exception:
            logger.exception("monitor_fire_hotspots error")
        return results

    async def process_citizen_report(self, report_data: Dict[str, Any]) -> RawIncidentSignal:
        # Extract structured fields from report
        return RawIncidentSignal(
            source_type=report_data.get("source_type", "CITIZEN_REPORT"),
            raw_text=report_data.get("raw_text", ""),
            location_hint=report_data.get("location_name", ""),
            latitude=report_data.get("latitude", 0.0),
            longitude=report_data.get("longitude", 0.0),
            disaster_type_hint=report_data.get("disaster_type", "OTHER"),
            confidence=0.0,
            timestamp=report_data.get("created_at"),
            metadata={},
        )

    async def create_incident_from_signal(self, signal: RawIncidentSignal):
        logger.info("Creating incident from signal: %s", signal)
        incident_doc = {
            "source_type": signal.source_type,
            "raw_text": signal.raw_text,
            "location_name": signal.location_hint,
            "latitude": signal.latitude,
            "longitude": signal.longitude,
            "disaster_type": signal.disaster_type_hint,
            "created_at": datetime.utcnow(),
            "verification_status": "PENDING",
            "verification_score": 0,
            "priority_score": 0,
            "severity": "UNASSIGNED",
            "channels_dispatched": [],
            "alerts_sent": [],
            "metadata": signal.metadata,
        }

        try:
            incident_id = await firebase_service.create_incident(incident_doc)
        except Exception:
            logger.exception("Failed to create incident in Firestore")
            return

        # Enqueue incident for pipeline processing
        try:
            from .pipeline import pipeline
            await pipeline.enqueue_incident(incident_id)
        except Exception:
            logger.exception("Failed to enqueue incident to pipeline %s", incident_id)

    async def run_monitoring_loop(self):
        while True:
            try:
                weather_signals = await self.monitor_weather_apis()
                for s in weather_signals:
                    await self.create_incident_from_signal(s)

                quake_signals = await self.monitor_earthquake_api()
                for s in quake_signals:
                    await self.create_incident_from_signal(s)

                fire_signals = await self.monitor_fire_hotspots()
                for s in fire_signals:
                    await self.create_incident_from_signal(s)
            except Exception:
                logger.exception("monitoring loop error")
            await asyncio.sleep(300)  # 5 minutes
