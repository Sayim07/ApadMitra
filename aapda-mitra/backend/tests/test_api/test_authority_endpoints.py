import sys
import os
import pytest
import asyncio

# Ensure backend package is importable (same pattern as other tests)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from api.routes import incidents as incidents_routes


@pytest.fixture(autouse=True)
def patch_firebase_and_dispatch(monkeypatch):
    # stub user lookup to return an authority user
    async def fake_get_user(uid):
        return {"user_id": uid, "name": "Authority", "role": "DISTRICT_AUTHORITY", "preferences": {}}

    async def fake_update_incident(incident_id, updates):
        # record no-op
        return None

    async def fake_get_incident(incident_id):
        return {"id": incident_id, "disaster_type": "FLOOD", "location_name": "Testville", "severity": "RED", "district": "TestDistrict"}

    class DummyResult:
        def __init__(self):
            self.channels_attempted = ["SMS"]
            self.channels_succeeded = ["ok"]
            self.channels_failed = []
            self.alert_ids = ["sid-123"]

    async def fake_dispatch_all(incident_id):
        return DummyResult()

    import services.firebase_service as fs
    monkeypatch.setattr(fs.firebase_service, 'get_user', fake_get_user)
    monkeypatch.setattr(fs.firebase_service, 'update_incident', fake_update_incident)
    monkeypatch.setattr(fs.firebase_service, 'get_incident', fake_get_incident)

    import agents.dispatch_agent as da
    async def _fake_dispatch(self, iid):
        return await fake_dispatch_all(iid)
    monkeypatch.setattr(da.DispatchAgent, 'dispatch_all', _fake_dispatch)

    yield


def test_acknowledge_assign_dispatch_flow():
    # call route handlers directly (async)
    async def run_flow():
        ack = await incidents_routes.acknowledge_incident('incident-1', type('P', (), {'acknowledged_by': 'authority-1'})())
        assert ack.get('ok') is True

        assign = await incidents_routes.assign_incident('incident-1', {'team_id': 'team-42'})
        assert assign.get('ok') is True

        dispatch = await incidents_routes.dispatch_incident('incident-1')
        assert dispatch.get('ok') is True
        assert 'result' in dispatch

    asyncio.get_event_loop().run_until_complete(run_flow())


def test_assign_creates_alert_and_notifies(monkeypatch):
    async def run_test():
        import services.firebase_service as fs
        # spy create_alert and get_team
        called = {}

        async def fake_get_team(team_id):
            return {"team_id": team_id, "name": "Rescue", "contacts": [{"phone": "+10000000001", "email": "team@example.com"}]}

        async def fake_create_alert(data):
            called['alert'] = data
            return 'alert-1'

        fs.firebase_service.get_team = fake_get_team
        fs.firebase_service.create_alert = fake_create_alert

        # monkeypatch SMS and Email services to capture sends
        import services.notification_service as ns

        async def fake_send_sms(self, to, body):
            called.setdefault('sms', []).append((to, body))
            return {"sid": None, "status": "queued", "to": to}

        async def fake_send_email(self, to, subject, html):
            called.setdefault('email', []).append((to, subject))
            return {"status": "queued", "to": to}

        ns.SMSService.send_sms = fake_send_sms
        ns.EmailService.send_email = fake_send_email

        # call assign
        res = await incidents_routes.assign_incident('incident-999', {'team_id': 'team-99', 'notes': 'test'})
        # allow background notification task to run
        await asyncio.sleep(0.01)
        assert res.get('ok') is True
        assert 'alert' in called
        assert 'sms' in called and len(called['sms']) == 1
        assert 'email' in called and len(called['email']) == 1

    asyncio.get_event_loop().run_until_complete(run_test())
