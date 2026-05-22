from fastapi import APIRouter
try:
    from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
except Exception:  # pragma: no cover - allow environments without prometheus_client
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"

    class Counter:  # minimal stub
        def __init__(self, *args, **kwargs):
            self._v = 0

        def inc(self, n=1):
            self._v += n

    class Gauge:
        def __init__(self, *args, **kwargs):
            self._v = 0

        def set(self, v=0):
            self._v = v

    def generate_latest():
        return b""

from fastapi.responses import Response

router = APIRouter(prefix="/metrics")

# Basic Prometheus metrics
INCIDENTS_CREATED = Counter("aapdamitra_incidents_created", "Number of incidents created")
ALERTS_DISPATCHED = Counter("aapdamitra_alerts_dispatched", "Number of alerts dispatched")
ACTIVE_INCIDENTS = Gauge("aapdamitra_active_incidents", "Current active incidents")


@router.get("/prometheus")
def prometheus_metrics():
    # Return latest metrics
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
