import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from api.routes import incidents as incidents_routes


def test_get_incident_actions():
    async def run_test():
        # monkeypatch firebase_service.get_incident_actions by replacing attribute
        import services.firebase_service as fs

        async def fake_get_actions(incident_id, limit=100):
            return [{"action": "assign", "by": "authority-1", "details": {"team_id": "team-1"}, "ts": 1620000000000}]

        fs.firebase_service.get_incident_actions = fake_get_actions

        res = await incidents_routes.get_incident_actions('incident-123')
        assert isinstance(res, dict)
        assert 'results' in res
        assert len(res['results']) == 1

    asyncio.get_event_loop().run_until_complete(run_test())
