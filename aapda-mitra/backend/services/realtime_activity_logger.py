import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("realtime_activity_logger")

try:
    import firebase_admin
    from firebase_admin import db
except Exception:  # pragma: no cover
    firebase_admin = None
    db = None


class RealtimeActivityLogger:
    """
    Logs activity events to Firebase Realtime Database without blocking the main flow.
    Uses fire-and-forget pattern with error logging.
    """

    def __init__(self):
        self._initialized = False
        self._db_ref = None

    async def initialize(self, settings=None) -> None:
        """Initialize Realtime Database connection."""
        if self._initialized:
            return
        if firebase_admin is None or db is None:
            logger.warning("firebase_admin not installed; RealtimeActivityLogger will remain uninitialized")
            self._initialized = False
            return

        try:
            # Get the database reference using FIREBASE_DATABASE_URL
            if settings and hasattr(settings, 'FIREBASE_DATABASE_URL') and settings.FIREBASE_DATABASE_URL:
                self._db_ref = db.reference(url=settings.FIREBASE_DATABASE_URL)
                self._initialized = True
                logger.info(f"Realtime Activity Logger initialized with URL: {settings.FIREBASE_DATABASE_URL}")
            else:
                logger.warning("FIREBASE_DATABASE_URL not configured; RealtimeActivityLogger will remain uninitialized")
                self._initialized = False
        except Exception as e:
            logger.exception(f"Failed to initialize Realtime Activity Logger: {e}")
            self._initialized = False

    async def log_login(
        self,
        uid: str,
        email: str,
        display_name: Optional[str] = None,
        role: str = "citizen",
        source: str = "web"
    ) -> None:
        """
        Log a login event to /activity/logins/{uid}/{pushId} and update /activity/users/{uid}.
        Non-blocking; errors are logged but do not raise.
        """
        if not self._initialized or self._db_ref is None:
            return

        async def _log():
            try:
                now = datetime.utcnow().isoformat()

                # Write to /activity/logins/{uid}/{pushId}
                logins_ref = self._db_ref.child("activity").child("logins").child(uid)
                login_event = {
                    "uid": uid,
                    "email": email,
                    "displayName": display_name or email,
                    "role": role,
                    "source": source,
                    "loginAt": now,
                    "lastSeen": now,
                }
                logins_ref.push(login_event)

                # Update /activity/users/{uid}
                users_ref = self._db_ref.child("activity").child("users").child(uid)
                users_ref.update({
                    "uid": uid,
                    "email": email,
                    "displayName": display_name or email,
                    "role": role,
                    "lastSeen": now,
                    "isOnline": True,
                })

                logger.info(f"Logged login for user {uid}")
            except Exception as e:
                logger.exception(f"Error logging login for user {uid}: {e}")

        # Fire and forget
        asyncio.create_task(_log())

    async def log_logout(self, uid: str) -> None:
        """
        Log a logout event by updating /activity/users/{uid}.
        Non-blocking; errors are logged but do not raise.
        """
        if not self._initialized or self._db_ref is None:
            return

        async def _log():
            try:
                now = datetime.utcnow().isoformat()

                # Update /activity/users/{uid}
                users_ref = self._db_ref.child("activity").child("users").child(uid)
                users_ref.update({
                    "isOnline": False,
                    "logoutAt": now,
                })

                logger.info(f"Logged logout for user {uid}")
            except Exception as e:
                logger.exception(f"Error logging logout for user {uid}: {e}")

        # Fire and forget
        asyncio.create_task(_log())

    async def log_upload(
        self,
        user_id: str,
        incident_id: str,
        file_name: str,
        file_url: str,
        file_type: str
    ) -> None:
        """
        Log an upload event to /activity/uploads/{pushId}.
        Non-blocking; errors are logged but do not raise.
        """
        if not self._initialized or self._db_ref is None:
            return

        async def _log():
            try:
                now = datetime.utcnow().isoformat()

                # Write to /activity/uploads/{pushId}
                uploads_ref = self._db_ref.child("activity").child("uploads")
                upload_event = {
                    "userId": user_id,
                    "incidentId": incident_id,
                    "fileName": file_name,
                    "fileUrl": file_url,
                    "fileType": file_type,
                    "uploadedAt": now,
                    "status": "completed",
                }
                uploads_ref.push(upload_event)

                logger.info(f"Logged upload for incident {incident_id} by user {user_id}")
            except Exception as e:
                logger.exception(f"Error logging upload for incident {incident_id}: {e}")

        # Fire and forget
        asyncio.create_task(_log())

    async def log_incident_submission(
        self,
        incident_id: str,
        status: str,
        severity: str,
        disaster_type: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an incident submission by updating /activity/incidents/{incidentId}.
        Non-blocking; errors are logged but do not raise.
        """
        if not self._initialized or self._db_ref is None:
            return

        async def _log():
            try:
                now = datetime.utcnow().isoformat()

                # Update /activity/incidents/{incidentId}
                incident_ref = self._db_ref.child("activity").child("incidents").child(incident_id)
                incident_data = {
                    "incidentId": incident_id,
                    "status": status,
                    "severity": severity,
                    "submittedAt": now,
                    "lastUpdated": now,
                }
                if disaster_type:
                    incident_data["disasterType"] = disaster_type
                if location:
                    incident_data["location"] = location

                incident_ref.update(incident_data)

                logger.info(f"Logged incident submission {incident_id} with status {status}")
            except Exception as e:
                logger.exception(f"Error logging incident submission {incident_id}: {e}")

        # Fire and forget
        asyncio.create_task(_log())


# Global singleton instance
realtime_activity_logger = RealtimeActivityLogger()
