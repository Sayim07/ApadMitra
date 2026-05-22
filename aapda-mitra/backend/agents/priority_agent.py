import logging
from dataclasses import dataclass
from typing import Dict, Any
from services.http_utils import request_json
from datetime import datetime, timedelta
import math

from models.incident import SeverityLevel
from services.firebase_service import firebase_service
from config.settings import settings

logger = logging.getLogger("priority_agent")


@dataclass
class PriorityResult:
    total_score: float
    severity: SeverityLevel
    score_breakdown: Dict[str, float]
    affected_radius_km: float
    estimated_population: int


class PriorityAgent:
    def __init__(self):
        self.role = "Emergency Rescue Priority Analyst"

    async def calculate_priority(self, incident_id: str) -> PriorityResult:
        # load incident
        incident = await firebase_service.get_incident(incident_id)
        if not incident:
            return PriorityResult(total_score=0.0, severity=SeverityLevel.UNASSIGNED, score_breakdown={}, affected_radius_km=0.0, estimated_population=0)

        lat = float(incident.get("latitude") or 0)
        lng = float(incident.get("longitude") or 0)
        disaster_type = incident.get("disaster_type")
        created = incident.get("created_at")

        breakdown = {}
        total = 0.0

        # disaster intensity (max 30)
        intensity = 0.0
        try:
            url = f"{settings.OPEN_METEO_BASE_URL}/forecast?latitude={lat}&longitude={lng}&hourly=precipitation,windspeed_10m&forecast_days=1"
            data = await request_json(url, timeout=10, retries=2)
            if data:
                prec = data.get("hourly", {}).get("precipitation", [])
                wind = data.get("hourly", {}).get("windspeed_10m", [])
                max_prec = max(prec) if prec else 0
                max_wind = max(wind) if wind else 0
                if disaster_type == "FLOOD":
                    if max_prec > 100:
                        intensity = 30
                    elif max_prec > 75:
                        intensity = 24
                    elif max_prec > 50:
                        intensity = 18
                    else:
                        intensity = 10
                elif disaster_type == "EARTHQUAKE":
                    intensity = 8
                elif disaster_type == "CYCLONE":
                    if max_wind > 150:
                        intensity = 30
                    elif max_wind > 120:
                        intensity = 22
                    elif max_wind > 88:
                        intensity = 15
                    else:
                        intensity = 8
        except Exception:
            intensity = 10

        breakdown["disaster_intensity"] = intensity
        total += intensity

        # sos volume (max 25)
        sos_score = 0.0
        try:
            all_incidents = await firebase_service.get_incidents({}, limit=500)
            count = 0
            for inc in all_incidents:
                try:
                    lat2 = float(inc.get("latitude") or 0)
                    lng2 = float(inc.get("longitude") or 0)
                    dist = math.hypot(lat - lat2, lng - lng2) * 111  # rough km approx
                    created_at = inc.get("created_at")
                    if dist <= 10:
                        count += 1
                except Exception:
                    continue
            if count > 20:
                sos_score = 25
            elif count > 10:
                sos_score = 18
            elif count > 5:
                sos_score = 12
            elif count > 0:
                sos_score = 6
        except Exception:
            sos_score = 0

        breakdown["sos_volume"] = sos_score
        total += sos_score

        # population impact (max 20) - simple name-based heuristic
        pop_score = 5
        name = (incident.get("location_name") or "").lower()
        if any(x in name for x in ["mumbai", "delhi", "kolkata", "chennai"]):
            pop_score = 20
        elif any(x in name for x in ["pune", "lucknow", "hyderabad", "bangalore", "bengaluru"]):
            pop_score = 15
        elif name:
            pop_score = 10

        breakdown["population_impact"] = pop_score
        total += pop_score

        # infrastructure proximity (max 15) - simple placeholder
        infra = 0
        try:
            # query Nominatim for hospitals nearby
            url = f"https://nominatim.openstreetmap.org/search?format=json&q=hospital&limit=5&viewbox={lng-0.02},{lat+0.02},{lng+0.02},{lat-0.02}&bounded=1"
            items = await request_json(url, timeout=8, headers={"User-Agent": "AapdaMitra/1.0"}, retries=2)
            if items and isinstance(items, list):
                if len(items) >= 3:
                    infra = 15
                elif len(items) > 0:
                    infra = 8
        except Exception:
            infra = 0

        breakdown["infrastructure_proximity"] = infra
        total += infra

        # time elapsed (max 10)
        time_score = 0
        try:
            if isinstance(created, dict):
                time_score = 1
            else:
                # best-effort parse
                time_score = 10
        except Exception:
            time_score = 1

        breakdown["time_elapsed"] = time_score
        total += time_score

        total = max(0, min(100, total))

        if total >= 70:
            severity = SeverityLevel.RED
        elif total >= 40:
            severity = SeverityLevel.YELLOW
        else:
            severity = SeverityLevel.GREEN

        await firebase_service.update_incident(incident_id, {"priority_score": int(total), "severity": severity.value, "updated_at": datetime.utcnow()})

        return PriorityResult(total_score=total, severity=severity, score_breakdown=breakdown, affected_radius_km=2.0, estimated_population=1000)
