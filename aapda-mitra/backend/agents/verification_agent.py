import logging
from dataclasses import dataclass
from typing import Dict, Any, Tuple
import math
from services.http_utils import request_json
from datetime import datetime, timedelta

from models.incident import VerificationStatus
from services.firebase_service import firebase_service
from config.settings import settings

logger = logging.getLogger("verification_agent")


@dataclass
class VerificationResult:
    total_score: float
    status: VerificationStatus
    breakdown: Dict[str, float]
    reasoning: str


def _haversine(lat1, lon1, lat2, lon2):
    # returns distance in km
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class VerificationAgent:
    def __init__(self):
        self.role = "Incident Verification Agent"

    async def check_weather_correlation(self, lat: float, lng: float, disaster_type: str) -> Tuple[float, str]:
        try:
            url = f"{settings.OPEN_METEO_BASE_URL}/forecast?latitude={lat}&longitude={lng}&hourly=precipitation,windspeed_10m&forecast_days=1"
            data = await request_json(url, timeout=10, retries=2)
            if not data:
                return 0.0, "weather API unavailable"
            hourly = data.get("hourly", {})
            prec = hourly.get("precipitation", [])
            wind = hourly.get("windspeed_10m", [])
            max_prec = max(prec) if prec else 0
            max_wind = max(wind) if wind else 0

            if disaster_type.upper() == "FLOOD":
                if max_prec >= settings.RAINFALL_THRESHOLD_MM:
                    return 25.0, f"rainfall {max_prec} mm/hr"
                else:
                    return 0.0, f"rainfall {max_prec} mm/hr"
            if disaster_type.upper() == "CYCLONE":
                if max_wind >= settings.WIND_SPEED_CYCLONE_THRESHOLD:
                    return 25.0, f"windspeed {max_wind} km/h"
                else:
                    return 0.0, f"windspeed {max_wind} km/h"

            return 0.0, "no relevant weather signal"
        except Exception as e:
            logger.exception("check_weather_correlation error: %s", e)
            return 0.0, "weather check failed"

    async def check_geolocation_validity(self, location_text: str, lat: float, lng: float) -> Tuple[float, str]:
        try:
            # Use Nominatim reverse lookup
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=jsonv2"
            data = await request_json(url, timeout=10, headers={"User-Agent": "AapdaMitra/1.0"}, retries=2)
            if not data:
                return 0.0, "geolocation service unavailable"
            display = data.get("display_name", "")
            if location_text and location_text.lower() in display.lower():
                return 20.0, "location matches text"
            else:
                return 0.0, "location does not match text"
        except Exception as e:
            logger.exception("check_geolocation_validity error: %s", e)
            return 0.0, "geolocation check failed"

    async def check_multi_source_corroboration(self, lat: float, lng: float, disaster_type: str, time_window_hours: int = 4) -> Tuple[float, str]:
        try:
            cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)
            all_incidents = await firebase_service.get_incidents({}, limit=200)
            count = 0
            for inc in all_incidents:
                try:
                    lat2 = float(inc.get("latitude") or 0)
                    lng2 = float(inc.get("longitude") or 0)
                    dist = _haversine(lat, lng, lat2, lng2)
                    if dist <= 5 and inc.get("disaster_type") == disaster_type and count < 100:
                        count += 1
                except Exception:
                    continue

            if count >= 3:
                return 20.0, f"{count} corroborating reports"
            if count >= 1:
                return 10.0, f"{count} corroborating reports"
            return 0.0, "no corroboration"
        except Exception as e:
            logger.exception("check_multi_source_corroboration error: %s", e)
            return 0.0, "corroboration check failed"

    async def check_source_trust(self, source_type: str, media_urls: list) -> Tuple[float, str]:
        try:
            if source_type == "NEWS_FEED":
                return 15.0, "news outlet"
            if source_type == "CITIZEN_REPORT" and media_urls:
                return 10.0, "citizen with media"
            if source_type == "SOCIAL_MEDIA":
                return 5.0, "social media"
            return 0.0, "unknown"
        except Exception as e:
            logger.exception("check_source_trust error: %s", e)
            return 0.0, "source trust check failed"

    async def check_duplicate_report(self, lat: float, lng: float, disaster_type: str) -> Tuple[float, str]:
        try:
            all_incidents = await firebase_service.get_incidents({}, limit=200)
            for inc in all_incidents:
                try:
                    lat2 = float(inc.get("latitude") or 0)
                    lng2 = float(inc.get("longitude") or 0)
                    dist = _haversine(lat, lng, lat2, lng2)
                    if dist <= 5 and inc.get("disaster_type") == disaster_type and inc.get("verification_status") == "VERIFIED":
                        return -10.0, "duplicate of verified incident"
                except Exception:
                    continue
            return 10.0, "unique report"
        except Exception as e:
            logger.exception("check_duplicate_report error: %s", e)
            return 0.0, "duplicate check failed"

    async def verify_incident(self, incident_id: str) -> VerificationResult:
        incident = await firebase_service.get_incident(incident_id)
        if not incident:
            return VerificationResult(total_score=0.0, status=VerificationStatus.PENDING, breakdown={}, reasoning="incident not found")

        lat = float(incident.get("latitude") or 0)
        lng = float(incident.get("longitude") or 0)
        disaster_type = incident.get("disaster_type") or "OTHER"
        source_type = incident.get("source_type")
        media = incident.get("media_urls") or []

        breakdown = {}
        score = 0.0

        wscore, wmsg = await self.check_weather_correlation(lat, lng, disaster_type)
        breakdown["weather_correlation"] = wscore
        score += wscore

        gscore, gmsg = await self.check_geolocation_validity(incident.get("location_name", ""), lat, lng)
        breakdown["geolocation_validity"] = gscore
        score += gscore

        mscore, mmsg = await self.check_multi_source_corroboration(lat, lng, disaster_type)
        breakdown["multi_source"] = mscore
        score += mscore

        sscore, smsg = await self.check_source_trust(source_type, media)
        breakdown["source_trust"] = sscore
        score += sscore

        dscore, dmsg = await self.check_duplicate_report(lat, lng, disaster_type)
        breakdown["duplicate_check"] = dscore
        score += dscore

        # clamp score
        total = max(0.0, min(100.0, score))

        if total >= settings.VERIFICATION_SCORE_VERIFIED:
            status = VerificationStatus.VERIFIED
        elif total >= settings.VERIFICATION_SCORE_SUSPICIOUS:
            status = VerificationStatus.SUSPICIOUS
        else:
            status = VerificationStatus.FAKE

        reasoning = "; ".join([f"{k}:{v}" for k, v in breakdown.items()])

        # update Firestore
        await firebase_service.update_incident(incident_id, {"verification_score": int(total), "verification_status": status.value, "updated_at": datetime.utcnow()})

        return VerificationResult(total_score=total, status=status, breakdown=breakdown, reasoning=reasoning)
