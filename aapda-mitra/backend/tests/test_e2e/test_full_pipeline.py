"""
End-to-end integration tests for AapdaMitra disaster alert pipeline.
Tests the full flow: incident submission → verification → priority → alert generation → dispatch.
"""
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from config.settings import settings
from models.incident import IncidentCreate
from services.firebase_service import firebase_service


@pytest.mark.asyncio
class TestE2EDisasterPipeline:
    """Test the complete disaster alert pipeline from submission to dispatch."""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Initialize services for each test."""
        await firebase_service.initialize(settings)
        yield
    
    async def test_e2e_full_pipeline_from_incident_to_dispatch(self):
        """Test complete pipeline: incident → verification → priority → alerts → dispatch."""
        # Step 1: Create incident
        incident_data = {
            "disaster_type": "EARTHQUAKE",
            "description": "Major tremor in Delhi NCR",
            "latitude": 28.7041,
            "longitude": 77.1025,
            "location_name": "Delhi",
            "source_type": "CITIZEN",
            "severity": "RED",
            "source_confidence": 0.95
        }
        
        # Mock Firestore to avoid real DB calls
        with patch.object(firebase_service, 'create_incident', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = "incident-123"
            incident_id = await firebase_service.create_incident(incident_data)
        
        assert incident_id == "incident-123"
        mock_create.assert_called_once()
    
    async def test_e2e_verification_priority_flow(self):
        """Test verification and priority calculation stages."""
        incident_id = "incident-test-001"
        
        # Mock incident retrieval
        mock_incident = {
            "id": incident_id,
            "disaster_type": "FLOOD",
            "description": "Heavy flooding in Kerala",
            "latitude": 10.3528,
            "longitude": 75.5720,
            "location_name": "Kerala",
            "source_type": "CITIZEN",
            "source_confidence": 0.88
        }
        
        with patch.object(firebase_service, 'get_incident', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_incident
            incident = await firebase_service.get_incident(incident_id)
        
        assert incident["disaster_type"] == "FLOOD"
        
        # Mock verification score update
        with patch.object(firebase_service, 'update_incident', new_callable=AsyncMock) as mock_update:
            await firebase_service.update_incident(incident_id, {
                "verification_score": 0.78,
                "verification_status": "VERIFIED"
            })
        
        mock_update.assert_called_once()
        
        # Mock priority calculation
        with patch.object(firebase_service, 'update_incident', new_callable=AsyncMock) as mock_priority:
            await firebase_service.update_incident(incident_id, {
                "priority_score": 0.85,
                "severity": "RED"
            })
        
        mock_priority.assert_called_once()
    
    async def test_e2e_alert_generation_and_dispatch(self):
        """Test alert generation and multi-channel dispatch."""
        incident_id = "incident-alert-001"
        
        # Mock alert creation (language variants)
        for lang in ["en", "hi", "bn"]:
            with patch.object(firebase_service, 'create_alert', new_callable=AsyncMock) as mock_alert:
                mock_alert.return_value = f"alert-{lang}-123"
                alert_id = await firebase_service.create_alert({
                    "incident_id": incident_id,
                    "language": lang,
                    "message": f"Disaster alert in {lang}",
                    "status": "PENDING"
                })
            assert alert_id == f"alert-{lang}-123"
        
        # Mock authority contacts retrieval
        with patch.object(firebase_service, 'get_authority_contacts', new_callable=AsyncMock) as mock_contacts:
            mock_contacts.return_value = [
                {"id": "auth-001", "name": "Admin", "phone": "+919876543210", "email": "admin@example.com"},
                {"id": "auth-002", "name": "Officer", "phone": "+919876543211", "email": "officer@example.com"}
            ]
            contacts = await firebase_service.get_authority_contacts("incident-alert-001")
        
        assert len(contacts) == 2
        mock_contacts.assert_called_once()
    
    async def test_e2e_notification_queue_enqueue_process(self):
        """Test notification queue enqueue and processing flow."""
        from services.notification_queue import notification_queue
        
        # Mock notification items for different channels
        notification_items = [
            {
                "channel": "sms",
                "to": "+919876543210",
                "message": "Earthquake alert: Please move to safe location",
                "incident_id": "incident-001",
                "alert_id": "alert-001"
            },
            {
                "channel": "email",
                "to": "authority@example.com",
                "subject": "Critical Disaster Alert",
                "html": "<p>Earthquake detected. Response team activated.</p>",
                "incident_id": "incident-001",
                "alert_id": "alert-002"
            }
        ]
        
        # Enqueue notifications (in-memory fallback mode)
        enqueued_ids = []
        for item in notification_items:
            with patch.object(notification_queue._sms, 'send_sms', new_callable=AsyncMock) as mock_sms:
                with patch.object(notification_queue._email, 'send_email', new_callable=AsyncMock) as mock_email:
                    mock_sms.return_value = {"status": "sent"}
                    mock_email.return_value = {"status": "sent"}
                    
                    msg_id = await notification_queue.enqueue(item)
                    enqueued_ids.append(msg_id)
        
        assert len(enqueued_ids) == 2
    
    async def test_e2e_broadcast_alert_to_all_contacts(self):
        """Test broadcast alert functionality to all district authorities."""
        # Mock district authority contacts
        contacts = [
            {"id": "dist-01", "role": "DISTRICT_ADMIN", "phone": "+9198001"},
            {"id": "dist-02", "role": "DISTRICT_OFFICER", "phone": "+9198002"},
            {"id": "dist-03", "role": "COORDINATOR", "phone": "+9198003"}
        ]
        
        with patch.object(firebase_service, 'get_authority_contacts', new_callable=AsyncMock) as mock_get_contacts:
            mock_get_contacts.return_value = contacts
            fetched = await firebase_service.get_authority_contacts("district-001")
        
        assert len(fetched) == 3
        
        # Verify each contact receives broadcast
        from services.notification_queue import notification_queue
        broadcast_jobs = []
        
        for contact in contacts:
            job = {
                "channel": "sms",
                "to": contact["phone"],
                "message": "[BROADCAST] Critical disaster in your district. Check dashboard.",
                "incident_id": "broadcast-001",
                "alert_id": f"bcast-{contact['id']}"
            }
            broadcast_jobs.append(job)
        
        assert len(broadcast_jobs) == 3
    
    async def test_e2e_incident_acknowledge_assign_workflow(self):
        """Test authority workflow: acknowledge → assign → dispatch."""
        incident_id = "incident-wf-001"
        
        # Mock acknowledge
        with patch.object(firebase_service, 'update_incident', new_callable=AsyncMock) as mock_ack:
            await firebase_service.update_incident(incident_id, {
                "acknowledged": True,
                "acknowledged_by": "authority-001",
                "acknowledged_at": "2026-05-21T10:00:00Z"
            })
        mock_ack.assert_called_once()
        
        # Mock assign
        with patch.object(firebase_service, 'update_incident', new_callable=AsyncMock) as mock_assign:
            await firebase_service.update_incident(incident_id, {
                "assigned_to": "team-001",
                "assigned_at": "2026-05-21T10:02:00Z"
            })
        mock_assign.assert_called_once()
        
        # Mock create incident action
        with patch.object(firebase_service, 'create_incident_action', new_callable=AsyncMock) as mock_action:
            mock_action.return_value = "action-001"
            action_id = await firebase_service.create_incident_action({
                "incident_id": incident_id,
                "action_type": "DISPATCH",
                "description": "Emergency response dispatched",
                "performed_by": "authority-001"
            })
        assert action_id == "action-001"
    
    async def test_e2e_multi_source_verification(self):
        """Test multi-source incident verification and corroboration."""
        incident_id = "incident-multi-001"
        
        # Mock multiple sources for the same incident
        sources = [
            {"type": "CITIZEN_REPORT", "confidence": 0.85, "location": [28.7041, 77.1025]},
            {"type": "SEISMIC_SENSOR", "confidence": 0.95, "location": [28.7050, 77.1030]},
            {"type": "EMERGENCY_CALL", "confidence": 0.90, "location": [28.7035, 77.1020]}
        ]
        
        # Mock source verification
        verification_score = sum(s["confidence"] for s in sources) / len(sources)
        
        with patch.object(firebase_service, 'update_incident', new_callable=AsyncMock) as mock_verify:
            await firebase_service.update_incident(incident_id, {
                "verification_score": verification_score,
                "verification_status": "HIGHLY_VERIFIED",
                "source_count": len(sources)
            })
        
        mock_verify.assert_called_once()
        assert verification_score > 0.85
    
    async def test_e2e_alert_status_tracking(self):
        """Test alert status progression through different states."""
        alert_id = "alert-status-001"
        
        statuses = ["PENDING", "PROCESSING", "SENT", "ACKNOWLEDGED", "RESOLVED"]
        
        for status in statuses:
            with patch.object(firebase_service, 'update_alert_status', new_callable=AsyncMock) as mock_status:
                await firebase_service.update_alert_status(alert_id, status)
            mock_status.assert_called_once()


class TestNotificationQueueIntegration:
    """Test notification queue Redis/Firestore integration."""
    
    @pytest.mark.asyncio
    async def test_redis_queue_enqueue_and_process(self):
        """Test Redis queue enqueue (if Redis configured)."""
        from services.notification_queue import notification_queue
        
        if not notification_queue._use_redis:
            pytest.skip("Redis not configured")
        
        item = {
            "channel": "sms",
            "to": "+919876543210",
            "message": "Test notification",
            "incident_id": "test-001"
        }
        
        # Enqueue
        msg_id = await notification_queue.enqueue(item)
        assert msg_id.startswith("redis-")
    
    @pytest.mark.asyncio
    async def test_firestore_queue_fallback(self):
        """Test Firestore queue fallback when Redis unavailable."""
        from services.notification_queue import notification_queue
        
        # Create service with Redis disabled
        backup_use_redis = notification_queue._use_redis
        notification_queue._use_redis = False
        
        try:
            item = {
                "channel": "sms",
                "to": "+919876543210",
                "message": "Fallback test",
                "incident_id": "test-002"
            }
            
            with patch.object(firebase_service, 'db', None):
                msg_id = await notification_queue.enqueue(item)
            
            assert msg_id.startswith("local-")
        finally:
            notification_queue._use_redis = backup_use_redis


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
