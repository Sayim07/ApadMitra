import logging
import asyncio
from typing import Optional, List, Callable, Dict

logger = logging.getLogger("firebase_service")

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except Exception:  # pragma: no cover - firebase may not be installed in test env
    firebase_admin = None


class FirebaseService:
    def __init__(self):
        self._initialized = False
        self.app = None
        self.db = None
        self._listener_regs = []

    async def initialize(self, settings=None) -> None:
        if self._initialized:
            return
        if firebase_admin is None:
            logger.warning("firebase_admin not installed; FirebaseService will remain uninitialized")
            self._initialized = False
            return

        def _init():
            try:
                creds = None
                if settings is not None:
                    service_account_file = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_FILE", None)
                    if service_account_file:
                        creds = credentials.Certificate(service_account_file)
                    else:
                        creds_dict = settings.firebase_credentials()
                        creds = credentials.Certificate(creds_dict)
                else:
                    creds = credentials.ApplicationDefault()

                self.app = firebase_admin.initialize_app(creds)
                self.db = firestore.client()
                logger.info("Firebase initialized")
                self._initialized = True
            except Exception as e:
                logger.exception("Failed to initialize Firebase: %s", e)
                raise

        await asyncio.to_thread(_init)

    # Incidents
    async def create_incident(self, incident_data: Dict) -> str:
        try:
            def _create():
                col = self.db.collection("incidents")
                doc_ref = col.add(incident_data)[0]
                return doc_ref.id

            doc_id = await asyncio.to_thread(_create)
            return doc_id
        except Exception as e:
            logger.exception("create_incident error: %s", e)
            raise

    async def update_incident(self, incident_id: str, updates: Dict) -> None:
        try:
            def _update():
                doc_ref = self.db.collection("incidents").document(incident_id)
                doc_ref.update(updates)

            await asyncio.to_thread(_update)
        except Exception as e:
            logger.exception("update_incident error: %s", e)
            raise

    async def get_incident(self, incident_id: str) -> Optional[Dict]:
        try:
            def _get():
                doc = self.db.collection("incidents").document(incident_id).get()
                return doc.to_dict() if doc.exists else None

            return await asyncio.to_thread(_get)
        except Exception as e:
            logger.exception("get_incident error: %s", e)
            raise

    async def get_incidents(self, filters: Dict = {}, limit: int = 50) -> List[Dict]:
        try:
            def _query():
                col = self.db.collection("incidents")
                q = col
                # simple filters: severity, verification_status, disaster_type, district
                if "severity" in filters:
                    q = q.where("severity", "==", filters["severity"])
                if "verification_status" in filters:
                    q = q.where("verification_status", "==", filters["verification_status"])
                if "disaster_type" in filters:
                    q = q.where("disaster_type", "==", filters["disaster_type"])
                if "district" in filters:
                    q = q.where("district", "==", filters["district"])
                docs = q.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream()
                return [d.to_dict() for d in docs]

            return await asyncio.to_thread(_query)
        except Exception as e:
            logger.exception("get_incidents error: %s", e)
            raise

    async def get_active_incidents(self) -> List[Dict]:
        try:
            def _query():
                col = self.db.collection("incidents")
                docs = col.where("severity", "in", ["RED", "YELLOW"]).order_by("created_at", direction=firestore.Query.DESCENDING).stream()
                return [d.to_dict() for d in docs]

            return await asyncio.to_thread(_query)
        except Exception as e:
            logger.exception("get_active_incidents error: %s", e)
            raise

    # Alerts
    async def create_alert(self, alert_data: Dict) -> str:
        try:
            def _create():
                col = self.db.collection("alerts")
                doc_ref = col.add(alert_data)[0]
                return doc_ref.id

            return await asyncio.to_thread(_create)
        except Exception as e:
            logger.exception("create_alert error: %s", e)
            raise

    async def update_alert_status(self, alert_id: str, status: str, delivered_at=None) -> None:
        try:
            def _update():
                doc_ref = self.db.collection("alerts").document(alert_id)
                updates = {"delivery_status": status}
                if delivered_at is not None:
                    updates["delivered_at"] = delivered_at
                doc_ref.update(updates)

            await asyncio.to_thread(_update)
        except Exception as e:
            logger.exception("update_alert_status error: %s", e)
            raise

    async def get_alerts_for_incident(self, incident_id: str) -> List[Dict]:
        try:
            def _query():
                col = self.db.collection("alerts")
                docs = col.where("incident_id", "==", incident_id).order_by("created_at", direction=firestore.Query.DESCENDING).stream()
                return [d.to_dict() for d in docs]

            return await asyncio.to_thread(_query)
        except Exception as e:
            logger.exception("get_alerts_for_incident error: %s", e)
            raise

    async def get_alert(self, alert_id: str) -> Optional[Dict]:
        try:
            def _get():
                doc = self.db.collection("alerts").document(alert_id).get()
                return doc.to_dict() if doc.exists else None

            return await asyncio.to_thread(_get)
        except Exception as e:
            logger.exception("get_alert error: %s", e)
            raise

    async def get_alert_by_provider_sid(self, provider: str, sid: str) -> Optional[Dict]:
        try:
            def _query():
                col = self.db.collection("alerts")
                docs = col.where("provider", "==", provider).where("provider_sid", "==", sid).limit(1).stream()
                for d in docs:
                    data = d.to_dict()
                    data["_id"] = d.id
                    return data
                return None

            return await asyncio.to_thread(_query)
        except Exception as e:
            logger.exception("get_alert_by_provider_sid error: %s", e)
            raise

    # Users
    async def get_user(self, user_id: str) -> Optional[Dict]:
        try:
            def _get():
                doc = self.db.collection("users").document(user_id).get()
                return doc.to_dict() if doc.exists else None

            return await asyncio.to_thread(_get)
        except Exception as e:
            logger.exception("get_user error: %s", e)
            raise

    async def create_user_profile(self, user_id: str, profile: Dict) -> None:
        try:
            def _set():
                self.db.collection("users").document(user_id).set(profile, merge=True)

            await asyncio.to_thread(_set)
        except Exception as e:
            logger.exception("create_user_profile error: %s", e)
            raise

    async def get_authority_contacts(self, district: str = None) -> List[Dict]:
        try:
            def _query():
                col = self.db.collection("users")
                q = col.where("role", "in", ["DISTRICT_AUTHORITY", "ADMIN", "RESCUE_TEAM"])
                if district:
                    q = q.where("preferences.district", "==", district)
                docs = q.stream()
                return [d.to_dict() for d in docs]

            return await asyncio.to_thread(_query)
        except Exception as e:
            logger.exception("get_authority_contacts error: %s", e)
            raise

    async def get_teams(self, district: str = None) -> List[Dict]:
        try:
            def _query():
                col = self.db.collection("teams")
                q = col
                if district:
                    try:
                        q = q.where("district", "==", district)
                    except Exception:
                        pass
                docs = q.stream()
                return [d.to_dict() for d in docs]

            return await asyncio.to_thread(_query)
        except Exception as e:
            logger.exception("get_teams error: %s", e)
            raise

    async def get_team(self, team_id: str) -> Optional[Dict]:
        try:
            def _get():
                doc = self.db.collection("teams").document(team_id).get()
                return doc.to_dict() if doc.exists else None

            return await asyncio.to_thread(_get)
        except Exception as e:
            logger.exception("get_team error: %s", e)
            raise

    async def create_incident_action(self, incident_id: str, action: Dict) -> str:
        try:
            def _create():
                col = self.db.collection("incident_actions")
                # attach incident_id for querying
                action_copy = dict(action)
                action_copy["incident_id"] = incident_id
                doc_ref = col.add(action_copy)[0]
                return doc_ref.id

            return await asyncio.to_thread(_create)
        except Exception as e:
            logger.exception("create_incident_action error: %s", e)
            raise

    async def get_incident_actions(self, incident_id: str, limit: int = 100) -> List[Dict]:
        try:
            def _query():
                col = self.db.collection("incident_actions")
                docs = col.where("incident_id", "==", incident_id).order_by("ts", direction=firestore.Query.DESCENDING).limit(limit).stream()
                return [d.to_dict() for d in docs]

            return await asyncio.to_thread(_query)
        except Exception as e:
            logger.exception("get_incident_actions error: %s", e)
            raise

    # Real-time
    async def subscribe_to_incidents(self, callback: Callable) -> None:
        # Attaches a Firestore on_snapshot listener and calls callback with list of docs
        if self.db is None:
            raise RuntimeError("Firebase not initialized")

        def _on_snapshot(col_snapshot, changes, read_time):
            try:
                docs = [doc.to_dict() for doc in col_snapshot]
                asyncio.get_event_loop().call_soon_threadsafe(callback, docs)
            except Exception:
                logger.exception("Error in on_snapshot callback")

        col_ref = self.db.collection("incidents")

        # run the listener registration in a thread
        def _reg():
            reg = col_ref.on_snapshot(_on_snapshot)
            self._listener_regs.append(reg)
            return reg

        await asyncio.to_thread(_reg)



firebase_service = FirebaseService()
