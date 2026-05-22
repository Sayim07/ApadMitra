# 🌪️ AapdaMitra 2.0 — Complete Step-by-Step Build Prompts

> **How to use this file:** Copy each prompt block and paste it into your AI coding assistant (Trae.ai, Cursor, GitHub Copilot, or Claude). Follow the phases in order. Each prompt builds on the previous one.

---

## 📋 Table of Contents

1. [Phase 1 — Project Scaffold & Setup](#phase-1)
2. [Phase 2 — Firebase & Authentication](#phase-2)
3. [Phase 3 — Backend API (FastAPI)](#phase-3)
4. [Phase 4 — Monitoring Agent](#phase-4)
5. [Phase 5 — Verification Agent](#phase-5)
6. [Phase 6 — Priority Agent](#phase-6)
7. [Phase 7 — Alert Generation Agent (Gemini)](#phase-7)
8. [Phase 8 — Dispatch Agent + Multi-Channel Alerts](#phase-8)
9. [Phase 9 — AI Voice Call Agent (Twilio)](#phase-9)
10. [Phase 10 — React Frontend: Citizen Portal](#phase-10)
11. [Phase 11 — React Frontend: Authority Dashboard](#phase-11)
12. [Phase 12 — Live Disaster Map (Leaflet.js)](#phase-12)
13. [Phase 13 — Analytics Panel](#phase-13)
14. [Phase 14 — Fake News Score UI](#phase-14)
15. [Phase 15 — Testing & Load Testing](#phase-15)
16. [Phase 16 — Deployment (Vercel + Render)](#phase-16)

---

## Tech Stack Reference

| Layer | Technology |
|---|---|
| Frontend | React.js + Tailwind CSS |
| Backend | FastAPI (Python 3.11) |
| AI Orchestration | CrewAI |
| AI Model | Gemini 1.5 Flash API |
| Maps | Leaflet.js + OpenStreetMap |
| Database | Firebase Firestore |
| File Storage | Firebase Storage |
| Auth | Firebase Auth |
| Frontend Host | Vercel |
| Backend Host | Render |
| SMS + Voice | Twilio |
| WhatsApp | Gupshup |
| Email | SendGrid |

---

<a name="phase-1"></a>
## Phase 1 — Project Scaffold & Setup

### Prompt 1.1 — Initialize Full Project Structure

```
Create a monorepo project structure for a disaster intelligence platform called AapdaMitra.

Structure:
aapda-mitra/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   │   └── settings.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── monitoring_agent.py
│   │   ├── verification_agent.py
│   │   ├── priority_agent.py
│   │   ├── alert_generation_agent.py
│   │   └── dispatch_agent.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── incidents.py
│   │   │   ├── alerts.py
│   │   │   ├── users.py
│   │   │   └── dashboard.py
│   │   └── middleware/
│   │       └── auth.py
│   ├── services/
│   │   ├── firebase_service.py
│   │   ├── weather_service.py
│   │   ├── geolocation_service.py
│   │   └── notification_service.py
│   ├── models/
│   │   ├── incident.py
│   │   ├── alert.py
│   │   └── user.py
│   └── utils/
│       ├── logger.py
│       └── helpers.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   └── utils/
│   ├── package.json
│   └── tailwind.config.js
└── README.md

Generate:
1. The complete folder and file structure with placeholder content in each file
2. backend/requirements.txt with: fastapi, uvicorn, crewai, google-generativeai, firebase-admin, python-dotenv, httpx, pydantic, twilio, sendgrid, python-jose, passlib, Pillow
3. frontend/package.json with: react, react-dom, react-router-dom, leaflet, react-leaflet, recharts, firebase, axios, zustand, tailwindcss
4. A root README.md explaining the project
5. backend/.env.example with all required environment variable keys (no values)
```

---

### Prompt 1.2 — Environment Configuration

```
Create the configuration system for AapdaMitra backend.

In backend/config/settings.py, use pydantic-settings to load and validate all environment variables:

Required variables:
- GEMINI_API_KEY (Google AI)
- FIREBASE_PROJECT_ID
- FIREBASE_PRIVATE_KEY
- FIREBASE_CLIENT_EMAIL
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER
- SENDGRID_API_KEY
- GUPSHUP_API_KEY
- GUPSHUP_APP_NAME
- OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"
- GLOFAS_BASE_URL = "https://cds.climate.copernicus.eu"
- USGS_EARTHQUAKE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
- NASA_FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api"
- NASA_FIRMS_API_KEY
- SECRET_KEY (JWT)
- ALGORITHM = "HS256"
- ACCESS_TOKEN_EXPIRE_MINUTES = 30
- SEVERITY_RED_THRESHOLD = 80
- SEVERITY_YELLOW_THRESHOLD = 50
- VERIFICATION_SCORE_VERIFIED = 80
- VERIFICATION_SCORE_SUSPICIOUS = 50
- RAINFALL_THRESHOLD_MM = 50.0
- EARTHQUAKE_MAGNITUDE_THRESHOLD = 4.0
- WIND_SPEED_CYCLONE_THRESHOLD = 88.0
- FIRE_CONFIDENCE_THRESHOLD = 80

Make settings a singleton importable as: from config.settings import settings
```

---

<a name="phase-2"></a>
## Phase 2 — Firebase & Authentication

### Prompt 2.1 — Firebase Service

```
Create backend/services/firebase_service.py for AapdaMitra.

Requirements:
1. Initialize Firebase Admin SDK using credentials from environment variables (settings.py)
2. Create a FirebaseService class with these methods:

   # Incidents
   async def create_incident(incident_data: dict) -> str  # returns incident_id
   async def update_incident(incident_id: str, updates: dict) -> None
   async def get_incident(incident_id: str) -> dict | None
   async def get_incidents(filters: dict = {}, limit: int = 50) -> list[dict]
   async def get_active_incidents() -> list[dict]

   # Alerts
   async def create_alert(alert_data: dict) -> str  # returns alert_id
   async def update_alert_status(alert_id: str, status: str, delivered_at=None) -> None
   async def get_alerts_for_incident(incident_id: str) -> list[dict]

   # Users
   async def get_user(user_id: str) -> dict | None
   async def create_user_profile(user_id: str, profile: dict) -> None
   async def get_authority_contacts(district: str = None) -> list[dict]

   # Real-time
   async def subscribe_to_incidents(callback) -> None

3. Use Firestore collections: "incidents", "alerts", "users"
4. Add proper error handling and logging
5. Export a singleton: firebase_service = FirebaseService()
```

---

### Prompt 2.2 — Pydantic Data Models

```
Create Pydantic v2 models for AapdaMitra in the backend/models/ directory.

backend/models/incident.py:
- DisasterType enum: FLOOD, CYCLONE, EARTHQUAKE, LANDSLIDE, WILDFIRE, OTHER
- SourceType enum: CITIZEN_REPORT, SOCIAL_MEDIA, WEATHER_API, NEWS_FEED
- VerificationStatus enum: PENDING, VERIFIED, SUSPICIOUS, FAKE
- SeverityLevel enum: RED, YELLOW, GREEN, UNASSIGNED
- IncidentCreate model (for new submissions)
- IncidentUpdate model (partial updates)
- IncidentResponse model (full response with all fields)
- Include fields from the PRD schema: incident_id, disaster_type, source_type, raw_text, location_name, latitude, longitude, verification_score (0-100), verification_status, severity, priority_score (0-100), alerts_sent, channels_dispatched, acknowledged_by, media_urls, created_at, updated_at

backend/models/alert.py:
- ChannelType enum: SMS, WHATSAPP, EMAIL, VOICE, DASHBOARD, API
- DeliveryStatus enum: PENDING, SENT, DELIVERED, FAILED
- TargetAudience enum: CITIZEN, AUTHORITY, STATE
- AlertCreate, AlertUpdate, AlertResponse models

backend/models/user.py:
- UserRole enum: CITIZEN, WARD_OFFICER, RESCUE_TEAM, DISTRICT_AUTHORITY, ADMIN
- UserCreate, UserUpdate, UserResponse models
- NotificationPreferences nested model with: preferred_channels (list), preferred_language (str), district (str)

Add model_config with from_attributes=True on all response models.
```

---

### Prompt 2.3 — Authentication Middleware

```
Create JWT-based authentication for AapdaMitra backend.

In backend/api/middleware/auth.py:
1. verify_firebase_token(token: str) -> dict
   - Verifies Firebase ID token using firebase-admin
   - Returns decoded token claims
   - Raises HTTPException 401 if invalid

2. get_current_user(token: str = Depends(oauth2_scheme)) -> dict
   - FastAPI dependency for protected routes
   - Returns user data dict with user_id, role, district

3. require_role(*roles: UserRole) -> Dependency
   - Factory function returning a dependency that checks user role
   - Usage: Depends(require_role(UserRole.AUTHORITY, UserRole.ADMIN))

4. Role hierarchy: ADMIN > DISTRICT_AUTHORITY > RESCUE_TEAM > WARD_OFFICER > CITIZEN

In backend/api/routes/users.py:
- POST /auth/verify — verifies Firebase token, creates/updates user profile in Firestore
- GET /users/me — returns current user profile
- PUT /users/me — updates notification preferences
- GET /users/authority — lists authority users (admin only)
```

---

<a name="phase-3"></a>
## Phase 3 — Backend API (FastAPI)

### Prompt 3.1 — FastAPI Main App + Incident Routes

```
Create the main FastAPI application for AapdaMitra.

backend/main.py:
1. Initialize FastAPI app with title "AapdaMitra API", version "2.0.0"
2. Add CORS middleware allowing all origins (for development)
3. Add rate limiting middleware: max 100 requests/minute per IP using slowapi
4. Include routers: incidents, alerts, users, dashboard
5. Add startup event that initializes Firebase and starts background monitoring agent loop
6. Add /health endpoint returning {"status": "ok", "version": "2.0.0"}

backend/api/routes/incidents.py — implement these endpoints:
- POST /incidents — submit new citizen report (auth optional, accepts multipart form with text + images)
- POST /incidents/sos — SOS report with auto-GPS (faster pipeline, marks as priority)
- GET /incidents — list incidents with filters: severity, status, disaster_type, district (auth required: authority+)
- GET /incidents/{id} — get full incident detail
- PUT /incidents/{id}/acknowledge — authority acknowledges an incident
- GET /incidents/active — get all RED and YELLOW incidents (auth required)
- POST /incidents/{id}/assign — assign rescue team to incident (district_authority+)

Each endpoint should:
- Validate input with Pydantic models
- Write to Firestore via firebase_service
- Return appropriate HTTP status codes
- Include proper error handling
```

---

### Prompt 3.2 — Dashboard + Analytics Routes

```
Create dashboard and analytics API routes for AapdaMitra.

backend/api/routes/dashboard.py:
- GET /dashboard/summary — returns:
  {
    total_active: int,
    by_severity: { red: int, yellow: int, green: int },
    by_type: { flood: int, cyclone: int, earthquake: int, ... },
    avg_response_time_minutes: float,
    verification_stats: { verified: int, suspicious: int, fake: int },
    alerts_sent_today: int,
    acknowledgment_rate: float
  }

- GET /dashboard/heatmap — returns list of {lat, lng, intensity} for map heatmap layer
- GET /dashboard/incidents/stream — SSE endpoint for real-time incident updates using Firebase listener
- GET /dashboard/alerts/recent — last 20 alerts with delivery status

backend/api/routes/alerts.py:
- GET /alerts — list all alerts with filters
- GET /alerts/{id} — alert detail
- PUT /alerts/{id}/status — update delivery status (webhook endpoint for Twilio/SendGrid callbacks)
- POST /alerts/broadcast — manually send alert to a district (admin only)

Add proper pagination (skip, limit) to all list endpoints.
Add query param ?district=kolkata to filter by district on all relevant endpoints.
```

---

<a name="phase-4"></a>
## Phase 4 — Monitoring Agent

### Prompt 4.1 — Monitoring Agent Core

```
Create the Monitoring Agent for AapdaMitra using CrewAI.

backend/agents/monitoring_agent.py:

1. Create a MonitoringAgent class with CrewAI Agent:
   - role: "Disaster Monitoring Specialist"
   - goal: "Continuously scan all data sources for disaster signals and extract structured incident data"
   - backstory: "Expert in detecting early warning signs of natural disasters from multiple data streams"

2. Implement these monitoring tasks as CrewAI Tasks:

   a) monitor_weather_apis() — async method that:
      - Calls Open-Meteo API for rainfall data at key Indian cities (Kolkata, Mumbai, Chennai, Delhi, Bhubaneswar, Guwahati)
      - Endpoint: https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=precipitation,windspeed_10m,precipitation_probability&forecast_days=1
      - Triggers if: precipitation > 50mm/hour OR windspeed > 88km/h
      - Returns list of RawIncidentSignal objects

   b) monitor_earthquake_api() — async method that:
      - Calls USGS API: https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=4.0&orderby=time&limit=10&minlatitude=8&maxlatitude=37&minlongitude=68&maxlongitude=97
      - Filters to India bounding box
      - Returns list of RawIncidentSignal objects

   c) monitor_fire_hotspots() — async method that:
      - Calls NASA FIRMS API for India fire hotspots
      - Filters confidence > 80%
      - Returns list of RawIncidentSignal objects

   d) process_citizen_report(report_data: dict) — called when citizen submits report via API
      - Extracts and structures the report
      - Returns RawIncidentSignal

3. RawIncidentSignal dataclass:
   source_type, raw_text, location_hint, latitude, longitude, disaster_type_hint, confidence, timestamp, metadata dict

4. create_incident_from_signal(signal: RawIncidentSignal) — stores to Firestore and triggers verification pipeline

5. async run_monitoring_loop() — runs all monitors every 5 minutes using asyncio
   - On detection, immediately fires verification pipeline for each new signal
   - Deduplicates: skip if similar incident exists within 5km in last 2 hours

Use httpx for async HTTP calls. Add comprehensive logging.
```

---

<a name="phase-5"></a>
## Phase 5 — Verification Agent

### Prompt 5.1 — Verification Agent Core

```
Create the Verification Agent for AapdaMitra using CrewAI.

backend/agents/verification_agent.py:

1. Create VerificationAgent class with CrewAI Agent:
   - role: "Disaster Report Verification Specialist"  
   - goal: "Verify whether disaster reports are genuine using weather data, geolocation, and source analysis"
   - backstory: "Expert fact-checker trained to identify genuine disasters vs misinformation using API corroboration"

2. Main method: async verify_incident(incident_id: str) -> VerificationResult

3. Implement these verification checks as separate async methods:

   a) check_weather_correlation(lat, lng, disaster_type) -> tuple[float, str]:
      - Flood check: Open-Meteo rainfall > 50mm/hr → +25 points
      - Cyclone check: windspeed > 88km/h → +25 points
      - Score 0 if weather contradicts report (sunny during claimed flood) → -10 points
      
   b) check_geolocation_validity(location_text, lat, lng) -> tuple[float, str]:
      - Use Gemini API to extract location from text
      - Verify extracted location matches provided coordinates using Nominatim (OpenStreetMap geocoding)
      - Match → +20 points, Mismatch → -20 points, Unverifiable → 0 points

   c) check_multi_source_corroboration(lat, lng, disaster_type, time_window_hours=4) -> tuple[float, str]:
      - Query Firestore for other reports within 5km radius in last 4 hours
      - 3+ independent reports → +20 points
      - 1-2 reports → +10 points
      - 0 reports → 0 points

   d) check_source_trust(source_type) -> tuple[float, str]:
      - VERIFIED_NEWS_OUTLET → +15 points
      - CITIZEN_REPORT (with photo) → +10 points
      - ANONYMOUS_SOCIAL_MEDIA → +5 points
      - UNKNOWN → 0 points

   e) check_duplicate_report(lat, lng, disaster_type) -> tuple[float, str]:
      - If this is a duplicate of already-verified incident → -10 points
      - New unique report → +10 points
      - Checks using geospatial 5km radius query

4. VerificationResult dataclass:
   total_score: float (0-100)
   status: VerificationStatus
   breakdown: dict[str, float]  # per-check scores
   reasoning: str  # human-readable explanation

5. Classification logic:
   - score >= 80 → VERIFIED
   - score 50-79 → SUSPICIOUS  
   - score < 50 → FAKE

6. After verification: update Firestore incident with score + status, trigger priority agent if VERIFIED or SUSPICIOUS
```

---

<a name="phase-6"></a>
## Phase 6 — Priority Agent

### Prompt 6.1 — Priority Agent Core

```
Create the Priority Agent for AapdaMitra using CrewAI.

backend/agents/priority_agent.py:

1. Create PriorityAgent class with CrewAI Agent:
   - role: "Emergency Rescue Priority Analyst"
   - goal: "Calculate rescue priority scores and assign severity levels to verified disaster incidents"
   - backstory: "Emergency management expert who optimizes rescue resource allocation using data-driven severity scoring"

2. Main method: async calculate_priority(incident_id: str) -> PriorityResult

3. Implement these scoring factors (total must equal 100 points):

   a) score_disaster_intensity(lat, lng, disaster_type) -> float (max 30 pts):
      - Flood: rainfall intensity from Open-Meteo — scale 0-30 based on mm/hr
        - > 100mm/hr → 30 pts, 75-100 → 24 pts, 50-75 → 18 pts, < 50 → 10 pts
      - Earthquake: USGS magnitude
        - magnitude >= 6.5 → 30 pts, 5.5-6.5 → 22 pts, 4.5-5.5 → 15 pts, < 4.5 → 8 pts
      - Cyclone: wind speed
        - > 150 km/h → 30 pts, 120-150 → 22 pts, 88-120 → 15 pts

   b) score_sos_volume(lat, lng, radius_km=10) -> float (max 25 pts):
      - Count SOS reports in 10km radius in last 2 hours from Firestore
      - > 20 reports → 25 pts, 10-20 → 18 pts, 5-10 → 12 pts, 1-4 → 6 pts, 0 → 0 pts

   c) score_population_impact(lat, lng) -> float (max 20 pts):
      - Use hardcoded Indian city population density data
      - Major metro (Mumbai, Delhi, Kolkata, Chennai) → 20 pts
      - Tier-2 city → 15 pts
      - District town → 10 pts
      - Rural → 5 pts

   d) score_infrastructure_proximity(lat, lng) -> float (max 15 pts):
      - Query OpenStreetMap Nominatim for hospitals, schools, bridges within 2km
      - Call: https://nominatim.openstreetmap.org/search?q=hospital&format=json&limit=5&viewbox={lng-0.05},{lat+0.05},{lng+0.05},{lat-0.05}&bounded=1
      - Critical infrastructure nearby → 15 pts, some → 8 pts, none → 0 pts

   e) score_time_elapsed(created_at: datetime) -> float (max 10 pts):
      - < 15 min ago → 10 pts (very fresh, needs urgent response)
      - 15-60 min → 7 pts
      - 1-3 hours → 4 pts
      - > 3 hours → 1 pt

4. Severity assignment:
   - total_score >= 70 → RED (Critical)
   - total_score 40-69 → YELLOW (Moderate)
   - total_score < 40 → GREEN (Low)

5. PriorityResult dataclass:
   total_score: float, severity: SeverityLevel, score_breakdown: dict, affected_radius_km: float, estimated_population: int

6. After scoring: update incident in Firestore, trigger alert generation agent for RED and YELLOW
```

---

<a name="phase-7"></a>
## Phase 7 — Alert Generation Agent (Gemini)

### Prompt 7.1 — Alert Generation with Gemini API

```
Create the Alert Generation Agent for AapdaMitra using CrewAI and Gemini 1.5 Flash.

backend/agents/alert_generation_agent.py:

1. Create AlertGenerationAgent class with CrewAI Agent:
   - role: "Emergency Communications Specialist"
   - goal: "Generate clear, actionable, multilingual emergency alerts tailored to different audiences"
   - backstory: "Expert in crisis communications trained to write urgent, jargon-free emergency messages in multiple Indian languages"

2. Initialize Gemini: import google.generativeai as genai, configure with GEMINI_API_KEY, use model "gemini-1.5-flash"

3. Main method: async generate_all_alerts(incident_id: str) -> list[GeneratedAlert]

4. Implement these alert generators:

   a) generate_citizen_alert(incident: dict, language: str) -> str
      Prompt template:
      """
      You are an emergency alert system. Generate a SHORT, URGENT citizen alert (max 160 characters for SMS, max 300 for WhatsApp).
      
      Incident: {disaster_type} in {location_name}
      Severity: {severity}
      Verified by: weather data showing {weather_details}
      
      Generate alert in {language} language.
      Include: what happened, where, what to do RIGHT NOW.
      Do NOT include technical jargon. Be direct and life-saving.
      For SMS: max 160 chars. For WhatsApp: max 300 chars.
      """
      Generate for: English, Hindi (hi), Bengali (bn)

   b) generate_authority_brief(incident: dict) -> str
      Prompt template:
      """
      Generate a formal emergency incident brief for district authorities and rescue teams.
      
      Incident Data: {full_incident_json}
      
      Include:
      - Incident summary (2 sentences)
      - Verification method and confidence score
      - Priority score breakdown
      - Recommended immediate actions
      - Resources required
      - Estimated affected population
      
      Format as structured brief. English only. Max 400 words.
      """

   c) generate_district_report(incidents: list, district: str) -> str
      Generates HTML email report for state-level officials
      Includes: incident summary table, map link, priority zones, response recommendations

   d) generate_voice_call_script(incident: dict, language: str) -> str
      Prompt:
      """
      Generate a VOICE CALL SCRIPT for an AI voice call to a District Magistrate.
      Disaster: {disaster_type} in {location_name}. Severity: RED. Population at risk: {population}.
      
      Rules:
      - Opening: "Hello, this is an emergency alert from AapdaMitra."
      - State the disaster, location, severity in 2 sentences
      - Ask for acknowledgment: "Say ACKNOWLEDGED to confirm receipt."
      - Total script: max 30 seconds when spoken (approximately 75 words)
      - Language: {language}
      """

5. GeneratedAlert dataclass:
   incident_id, alert_type, language, channel, content_text, content_html, generated_at

6. Store all generated alerts to Firestore alerts collection
7. After generation: trigger dispatch agent
```

---

<a name="phase-8"></a>
## Phase 8 — Dispatch Agent + Multi-Channel Alerts

### Prompt 8.1 — Dispatch Agent + All Channel Services

```
Create the Dispatch Agent and all notification services for AapdaMitra.

backend/agents/dispatch_agent.py:

1. Create DispatchAgent class with CrewAI Agent:
   - role: "Emergency Alert Dispatch Coordinator"
   - goal: "Deliver verified emergency alerts to the right people through the right channels with guaranteed delivery tracking"

2. Main method: async dispatch_all(incident_id: str) -> DispatchResult

3. Channel routing logic:
   - GREEN incidents → Dashboard push only
   - YELLOW incidents → SMS + WhatsApp + Dashboard + Email
   - RED incidents → ALL channels simultaneously (SMS + WhatsApp + Email + Voice + Dashboard)

4. Implement channel senders:

backend/services/notification_service.py — create these service classes:

   class SMSService:
      def __init__: init Twilio Client with ACCOUNT_SID + AUTH_TOKEN
      async def send_sms(to: str, body: str) -> dict:
         - Use twilio client.messages.create(body=body, from_=TWILIO_PHONE_NUMBER, to=to)
         - Return: {sid, status, to}
      async def send_bulk_sms(contacts: list[str], body: str) -> list[dict]:
         - Send to all contacts concurrently using asyncio.gather

   class WhatsAppService:
      async def send_whatsapp(to: str, body: str) -> dict:
         - Use Gupshup API: POST https://api.gupshup.io/sm/api/v1/msg
         - Headers: apikey: GUPSHUP_API_KEY
         - Body: {"channel": "whatsapp", "source": GUPSHUP_APP_NAME, "destination": to, "message": {"type": "text", "text": body}}
         - Return response dict

   class EmailService:
      def __init__: init SendGrid client
      async def send_email(to: str, subject: str, html_content: str) -> dict:
         - Use sendgrid.send() with proper Message object
         - Include AapdaMitra branding in HTML template
      async def send_district_report(to: str, incident: dict, html_report: str) -> dict:
         - Attach map screenshot URL if available

   class DashboardService:
      async def push_update(incident_id: str, update_data: dict) -> None:
         - Write to Firebase Realtime Database path: /live_updates/{incident_id}
         - Frontend subscribes to this for real-time updates

5. Escalation logic in dispatch_agent.py:
   async def check_and_escalate():
      - Query all RED incidents where acknowledged=False AND created_at < 10 minutes ago
      - For unacknowledged: re-dispatch SMS + Voice to next contact in authority chain
      - After 20 minutes unacknowledged: escalate to state-level contacts
      - Log all escalations with timestamp

6. DispatchResult: channels_attempted, channels_succeeded, channels_failed, dispatch_timestamp, alert_ids
```

---

<a name="phase-9"></a>
## Phase 9 — AI Voice Call Agent (Twilio)

### Prompt 9.1 — Voice Call System

```
Create the AI Voice Call system for AapdaMitra.

backend/services/voice_service.py:

1. VoiceCallService class:

   async def place_emergency_call(to: str, script: str, incident_id: str) -> dict:
      - Use Twilio Client to place a call
      - TwiML URL points to /voice/twiml/{incident_id} endpoint
      - Record the call: record=True
      - Returns: {call_sid, status, to, incident_id}

   async def place_bulk_calls(contacts: list[str], script: str, incident_id: str) -> list[dict]:
      - Place calls to all contacts concurrently
      - Use asyncio.gather with max concurrency of 10

2. In backend/api/routes/voice.py, create TwiML endpoints:

   GET /voice/twiml/{incident_id}:
      - Retrieve incident and its voice script from Firestore
      - Return TwiML XML:
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
          <Say voice="alice" language="en-IN">{script}</Say>
          <Gather input="speech" speechTimeout="3" action="/voice/acknowledgment/{incident_id}" method="POST">
            <Say voice="alice" language="en-IN">Press 1 or say ACKNOWLEDGED to confirm.</Say>
          </Gather>
          <Say>We did not receive your acknowledgment. This incident remains unacknowledged in our system. Goodbye.</Say>
        </Response>

   POST /voice/acknowledgment/{incident_id}:
      - Twilio webhook — receives speech recognition result
      - Check SpeechResult for keywords: "acknowledged", "confirmed", "received", "हाँ", "ठीक है"
      - If keyword found: update Firestore incident acknowledged=True, acknowledged_by=[caller_id]
      - Return TwiML:
        <Response>
          <Say>Thank you. Acknowledgment recorded. Please check AapdaMitra dashboard for full incident details. Stay safe.</Say>
          <Hangup/>
        </Response>

3. Voice call script generator (also in voice_service.py):
   def build_twiml_for_incident(incident: dict, language: str = "en") -> str:
      - Map language codes to Twilio voice: en→alice/en-IN, hi→alice/hi-IN, bn→alice/bn-IN
      - Builds full TwiML XML string from incident data

4. Add voice call status tracking:
   POST /voice/status-callback:
      - Twilio status webhook
      - Update alert delivery_status in Firestore based on CallStatus field
```

---

<a name="phase-10"></a>
## Phase 10 — React Frontend: Citizen Portal

### Prompt 10.1 — React App Setup + Citizen Pages

```
Create the React frontend for AapdaMitra's Citizen Portal.

First, set up frontend/src/App.jsx with React Router v6:
Routes:
- / → LandingPage
- /report → CitizenReportPage
- /sos → SOSPage
- /map → PublicMapPage
- /alerts → PublicAlertsPage
- /dashboard → DashboardPage (protected, authority+)
- /dashboard/incidents → IncidentsPage (protected)
- /dashboard/analytics → AnalyticsPage (protected)
- /auth → AuthPage

Set up frontend/src/store/authStore.js using Zustand:
- user state (null | userObject)
- setUser(user), clearUser()
- role getter
- isAuthority computed

Set up frontend/src/services/api.js:
- axios instance with base URL from env
- Request interceptor to add Firebase ID token to Authorization header
- Response interceptor for 401 handling

---

Create frontend/src/pages/LandingPage.jsx:
- Full-screen hero section: "AapdaMitra 2.0" with tagline "From Tweet to Rescue in 30 Seconds"
- Dark theme (#1a1a2e background, red accent #e74c3c)
- Three feature cards: Detect, Verify, Alert with icons
- Live stats ticker: active incidents count, alerts sent today, response time avg (fetch from /dashboard/summary)
- Two CTAs: "Report Emergency" → /report, "Authority Login" → /auth
- Navbar with: logo, Home, Live Map, Report, Login
- Mobile responsive

---

Create frontend/src/pages/CitizenReportPage.jsx:
Multi-step form (3 steps):

Step 1 — What happened:
- DisasterType dropdown: Flood, Cyclone, Earthquake, Landslide, Wildfire, Other
- Description textarea (required, min 20 chars)
- Severity estimate: "How bad is it?" → Mild / Moderate / Severe

Step 2 — Where:
- Auto-detect location button (uses browser Geolocation API)
- OR manual address input with Nominatim geocoding (https://nominatim.openstreetmap.org/search)
- Show selected location on small Leaflet map preview

Step 3 — Evidence:
- Photo/video upload (max 5 files, 10MB each)
- Contact number (optional, for follow-up)
- Submit button

POST to /incidents with FormData. On success: show tracking token with "Track your report" link.
Add form validation. Add loading states. Add error messages.
```

---

### Prompt 10.2 — SOS Page

```
Create frontend/src/pages/SOSPage.jsx for AapdaMitra.

This is a ONE-TAP emergency page designed for panicked citizens.

Design requirements:
- Full screen, red background (#c0392b)
- Giant red SOS button in center
- Large white text: "EMERGENCY SOS"
- Sub-text: "Tap to send your location and SOS alert"

Behavior on tap:
1. Request browser Geolocation (high accuracy: true)
2. Show spinner: "Getting your location..."
3. POST to /incidents/sos with: { latitude, longitude, disaster_type: "OTHER", raw_text: "SOS - Citizen in distress", source_type: "CITIZEN_REPORT" }
4. Show success screen: "✅ SOS Sent! Help is on the way. Your report ID: {id}"
5. Show nearest emergency contacts (hardcoded): 
   - NDRF: 011-24363260
   - Emergency: 112
   - Flood Control: 1077

If geolocation denied:
- Show manual address input as fallback
- Still allow SOS submission

Add pulsing animation on the SOS button.
Add shake animation on error.
Mobile-first design — works perfectly on 375px screens.
```

---

<a name="phase-11"></a>
## Phase 11 — React Frontend: Authority Dashboard

### Prompt 11.1 — Main Dashboard Layout

```
Create the Authority Dashboard layout for AapdaMitra.

frontend/src/pages/DashboardPage.jsx — main shell:

Layout:
- Fixed top navbar: AapdaMitra logo | "LIVE MONITORING" status badge (pulsing green dot) | active RED count badge | user info | logout
- Fixed left sidebar (240px): navigation links with icons
  - 🗺️ Live Map
  - 🚨 Active Incidents
  - 📊 Analytics
  - 📋 Alert History
  - ⚙️ Settings
- Main content area (flex-1): renders child routes
- Right panel (320px, collapsible): real-time incident feed

If any RED incident is unacknowledged:
- Show sticky full-width red banner at top: "⚠️ CRITICAL ALERT — {location} — [Acknowledge Now]"
- Play audio alert sound (optional, user can dismiss)

Fetch /dashboard/summary every 30 seconds and update stats in top bar.

Dark theme: background #0f0f1a, sidebar #1a1a2e, cards #1e1e3a, accent #e74c3c
Text: white primary, #8892b0 secondary
Borders: #2d2d4e

---

Create frontend/src/components/dashboard/IncidentFeed.jsx (right panel):

- Title: "Live Incidents" with count badge
- Scrollable list of last 20 incidents, real-time updated via Firebase onSnapshot listener
- Each item shows:
  - Colored left border (red/yellow/green by severity)
  - Disaster type icon + type name
  - Location name
  - Time ago (e.g., "3 min ago")
  - Verification score badge
  - Severity badge (RED/YELLOW/GREEN pill)
  - "View" button → navigates to incident detail

- Filter tabs at top: ALL | RED | YELLOW | VERIFIED
- Real-time: use Firebase onSnapshot on "incidents" collection, orderBy created_at desc, limit 20
```

---

### Prompt 11.2 — Incident Detail Page

```
Create frontend/src/pages/IncidentDetailPage.jsx for AapdaMitra.

Route: /dashboard/incidents/:id

Fetch incident from GET /incidents/{id} on mount.

Layout — two column:

LEFT COLUMN (60%):
1. Header: DisasterType icon | Location name | Severity badge | Verification status badge
2. Incident Summary card:
   - Description / raw text
   - Source type
   - Reported at timestamp
   - Coordinates (lat/lng)
   - Small embedded Leaflet map showing exact location with red marker

3. Verification Score card:
   - Large score number (e.g., "92")
   - Score label: VERIFIED / SUSPICIOUS / FAKE
   - Progress bars for each verification factor:
     - Weather API Correlation: [####░] 25/25
     - Multi-source Corroboration: [###░░] 15/20
     - Geolocation Match: [####] 20/20
     - Media Authenticity: [##░░] 10/20
     - Source Trust: [##░] 12/15
   - Reasoning text from verification agent

4. Priority Score card:
   - Circular progress showing score / 100
   - Factor breakdown table

RIGHT COLUMN (40%):
5. Severity Badge: large RED/YELLOW/GREEN indicator
6. Acknowledge button (if not acknowledged): big red button "ACKNOWLEDGE & DISPATCH"
   - On click: POST /incidents/{id}/acknowledge, update UI
   
7. Alert Dispatch Status card:
   - Channel list with delivery icons:
     📱 SMS → ✅ Delivered to 8 contacts
     💬 WhatsApp → ✅ Delivered
     📧 Email → ✅ Sent
     📞 Voice → 🔄 Calling...
     🖥️ Dashboard → ✅ Live
   
8. Generated Alerts card:
   - Tabs: English | Hindi | Bengali
   - Shows generated alert text per language

9. Media Evidence: photo thumbnails if uploaded

Add real-time updates via Firebase onSnapshot for this incident document.
```

---

<a name="phase-12"></a>
## Phase 12 — Live Disaster Map (Leaflet.js)

### Prompt 12.1 — Full Interactive Disaster Map

```
Create the Live Disaster Map for AapdaMitra.

frontend/src/components/map/DisasterMap.jsx:

1. Initialize Leaflet map centered on India (20.5937, 78.9629), zoom 5
   Use OpenStreetMap tiles: https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png

2. Custom marker icons per severity:
   - RED: red circle marker with pulse animation (CSS keyframes)
   - YELLOW: orange circle marker
   - GREEN: green circle marker
   - GREY: grey circle marker (unverified)

3. Incident markers:
   - Fetch from GET /incidents and GET /incidents/active
   - For each incident: place marker at {latitude, longitude}
   - On click: show popup with:
     - Disaster type + location name
     - Severity badge
     - Verification score
     - "View Full Report →" link to /dashboard/incidents/{id}
   - Real-time: subscribe to Firebase for new incidents, add markers dynamically

4. Heatmap layer (separate toggle):
   - Use leaflet.heat plugin
   - Fetch /dashboard/heatmap for {lat, lng, intensity} points
   - Toggle button: "Heatmap ON/OFF"

5. Layer controls (top-right panel):
   - ☑ Verified Incidents
   - ☑ Unverified Reports  
   - ☑ Rescue Priority Zones
   - ☑ Heatmap
   - ☑ Flood Zones (if flood type selected)

6. Map controls:
   - Locate me button (flies to user location)
   - Reset view button (back to India view)
   - Fullscreen toggle

7. District boundary filter dropdown: select district → map flies to that district

8. Live count overlay (bottom-left):
   🔴 3 Critical  🟡 8 Moderate  🟢 12 Safe

Use react-leaflet components. Add CSS for pulsing RED markers animation.
Make map take full available height of content area.
```

---

<a name="phase-13"></a>
## Phase 13 — Analytics Panel

### Prompt 13.1 — Analytics Dashboard with Recharts

```
Create the Analytics Panel for AapdaMitra.

frontend/src/pages/AnalyticsPage.jsx:

Use Recharts for all charts. Fetch data from /dashboard/summary and a new /dashboard/analytics endpoint.

First, add GET /dashboard/analytics to backend returning:
{
  incidents_by_day: [{date, count}] (last 7 days),
  incidents_by_type: [{type, count}],
  verification_breakdown: [{status, count, percentage}],
  severity_distribution: [{severity, count}],
  response_time_trend: [{date, avg_minutes}],
  channel_success_rates: [{channel, sent, delivered, rate}],
  top_affected_districts: [{district, incident_count, severity_score}]
}

Render these charts:

1. Top stats row (4 cards):
   - Total incidents this month
   - Average response time (minutes)
   - Verification accuracy rate
   - Acknowledgment rate (%)

2. "Incidents Over Time" — AreaChart (last 7 days)
   - X: date, Y: incident count
   - Color: gradient red
   - Include reference line for average

3. "Incidents by Disaster Type" — BarChart (horizontal)
   - Each disaster type as a bar
   - Color-coded by frequency

4. "Verification Breakdown" — PieChart
   - Verified: green, Suspicious: yellow, Fake: red
   - Show percentages + counts in legend

5. "Severity Distribution" — PieChart
   - RED: #e74c3c, YELLOW: #f39c12, GREEN: #27ae60

6. "Average Response Time Trend" — LineChart (last 7 days)
   - Target line at 5 minutes (red dotted)
   - Actual line in blue

7. "Alert Channel Success Rates" — BarChart
   - Grouped bars: Sent vs Delivered per channel
   - Show delivery rate % as label on top

8. "Top Affected Districts" — Table with columns:
   District | Active Incidents | Max Severity | Priority Score

Add date range filter (Today / Last 7 days / Last 30 days) that re-fetches data.
Add CSV export button for the districts table.
```

---

<a name="phase-14"></a>
## Phase 14 — Fake News Score UI

### Prompt 14.1 — Fake News Detection Visualization

```
Create the Fake News Score visualization components for AapdaMitra.

frontend/src/components/verification/VerificationScoreCard.jsx:

Props: { incident: IncidentObject }

Render:

1. Score display:
   - Large circular gauge (SVG) showing score 0-100
   - Color: green (80-100), yellow (50-79), red (0-49)
   - Center text: score number + "/ 100"
   - Below gauge: status pill — "✅ VERIFIED" | "⚠️ SUSPICIOUS" | "❌ FAKE"

2. Factor breakdown (accordion or visible list):
   Each factor shows:
   - Factor name
   - Score earned / Max score
   - Horizontal progress bar (colored by percentage)
   - Short explanation text

   Factors:
   - 🌧️ Weather API Correlation (max 25)
   - 🔁 Multi-Source Corroboration (max 20)
   - 📍 Geolocation Match (max 20)
   - 📷 Media Authenticity (max 20)
   - 📰 Source Trust Tier (max 15)

3. Verification reasoning card:
   - AI-generated explanation from verification agent
   - Quote-block style
   - "Verified using Open-Meteo rainfall data: 87mm/hr at coordinates. Multiple independent reports corroborate..."

4. Fake news indicators (if FAKE/SUSPICIOUS):
   - Red warning box: "⚠️ Reasons for low confidence score:"
   - Bullet list of specific issues found

---

frontend/src/components/incidents/IncidentCard.jsx (for incident list views):

Compact card showing:
- Left colored border (red/yellow/green/grey)
- Disaster type icon
- Location + time ago
- Fake news badge: tiny pill "92% VERIFIED" or "FAKE ❌"
- Severity badge
- Quick action: Acknowledge / View buttons

Make it reusable for both dashboard incident feed and incidents list page.
```

---

<a name="phase-15"></a>
## Phase 15 — Testing & Load Testing

### Prompt 15.1 — Backend Tests

```
Create a comprehensive test suite for AapdaMitra backend.

backend/tests/ directory:

1. conftest.py:
   - FastAPI TestClient fixture
   - Mock Firebase service fixture (don't hit real Firestore)
   - Mock Gemini API fixture
   - Mock Twilio fixture
   - Sample incident fixture with all required fields
   - Sample verified incident fixture (score: 92, severity: RED)

2. test_api/test_incidents.py:
   Test each endpoint:
   - test_submit_citizen_report_success
   - test_submit_citizen_report_missing_location (expect 422)
   - test_sos_report_creates_incident
   - test_get_incidents_requires_auth
   - test_acknowledge_incident_updates_firestore
   - test_filter_incidents_by_severity

3. test_agents/test_verification_agent.py:
   - test_flood_verification_with_high_rainfall (score should be > 80)
   - test_flood_verification_no_rainfall (score should be < 50)
   - test_duplicate_report_reduces_score
   - test_verified_news_source_increases_score
   - test_complete_verification_pipeline (mock all API calls)

4. test_agents/test_priority_agent.py:
   - test_high_magnitude_earthquake_scores_red
   - test_low_rainfall_scores_yellow
   - test_metro_city_population_bonus
   - test_priority_score_totals_100_max

5. test_agents/test_alert_generation.py:
   - test_generates_alerts_in_three_languages
   - test_citizen_alert_under_160_chars_sms
   - test_authority_brief_contains_required_sections
   - test_voice_script_under_75_words

6. test_services/test_dispatch.py:
   - test_red_incident_dispatches_all_channels
   - test_yellow_incident_skips_voice_call
   - test_green_incident_dashboard_only
   - test_escalation_triggered_after_10_minutes

Run with: pytest --cov=. --cov-report=html -v
Target: > 80% code coverage on agents and services.
```

---

### Prompt 15.2 — Load Testing with Locust

```
Create a Locust load test for AapdaMitra.

backend/tests/load_test.py:

from locust import HttpUser, task, between, events

class CitizenUser(HttpUser):
    wait_time = between(0.5, 2)
    
    @task(10)
    def submit_citizen_report(self):
        # Submit a realistic flood report
        self.client.post("/incidents", json={
            "disaster_type": "FLOOD",
            "source_type": "CITIZEN_REPORT",
            "raw_text": "There is heavy flooding at my location. Water level rising fast.",
            "location_name": "Behala, Kolkata",
            "latitude": 22.4926,
            "longitude": 88.3248
        })
    
    @task(3)
    def submit_sos(self):
        self.client.post("/incidents/sos", json={
            "latitude": 22.5726 + (random.random() * 0.1),
            "longitude": 88.3639 + (random.random() * 0.1)
        })
    
    @task(1)
    def view_active_incidents(self):
        self.client.get("/incidents/active")

class AuthorityUser(HttpUser):
    wait_time = between(2, 5)
    
    @task(5)
    def view_dashboard_summary(self):
        self.client.get("/dashboard/summary",
            headers={"Authorization": f"Bearer {self.authority_token}"})
    
    @task(3)
    def view_incidents(self):
        self.client.get("/incidents?severity=RED")
    
    @task(1)
    def view_analytics(self):
        self.client.get("/dashboard/analytics")

# Load test targets:
# - 500 concurrent citizen users submitting reports
# - 50 concurrent authority users viewing dashboard
# - Pass criteria: p95 response time < 500ms, 0% error rate
# Run: locust -f load_test.py --headless -u 500 -r 50 --run-time 2m
```

---

<a name="phase-16"></a>
## Phase 16 — Deployment (Vercel + Render)

### Prompt 16.1 — Render Backend Deployment

```
Set up production deployment configuration for AapdaMitra backend on Render.

1. Create backend/render.yaml:
services:
  - type: web
    name: aapda-mitra-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 8000
    healthCheckPath: /health

2. Create backend/Dockerfile for containerized deployment:
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

3. Update backend/main.py CORS:
   - In production: restrict origins to Vercel frontend domain
   - Read allowed origins from ALLOWED_ORIGINS env variable

4. Add keep-alive ping to avoid Render cold starts:
   Create backend/utils/keepalive.py:
   - Async task that pings /health every 14 minutes
   - Start in app startup event

5. Production environment variables checklist (add to Render dashboard):
   GEMINI_API_KEY, FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL,
   TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER,
   SENDGRID_API_KEY, GUPSHUP_API_KEY, NASA_FIRMS_API_KEY,
   SECRET_KEY, ALLOWED_ORIGINS

6. Set up Render cron job for monitoring loop:
   - Type: cron job
   - Schedule: */5 * * * * (every 5 minutes)
   - Command: python -c "from agents.monitoring_agent import MonitoringAgent; import asyncio; asyncio.run(MonitoringAgent().run_all_monitors())"
```

---

### Prompt 16.2 — Vercel Frontend Deployment

```
Set up production deployment for AapdaMitra React frontend on Vercel.

1. Create frontend/vercel.json:
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}

2. Create frontend/.env.production:
VITE_API_BASE_URL=https://aapda-mitra-api.onrender.com
VITE_FIREBASE_API_KEY=<from Firebase console>
VITE_FIREBASE_AUTH_DOMAIN=<project>.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=<project-id>
VITE_FIREBASE_STORAGE_BUCKET=<project>.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=<sender-id>
VITE_FIREBASE_APP_ID=<app-id>
VITE_FIREBASE_DATABASE_URL=https://<project>.firebaseio.com

3. Create frontend/vite.config.js with:
   - React plugin
   - Build optimization: code splitting for leaflet, recharts, firebase
   - Source maps disabled in production

4. Update frontend/src/services/api.js:
   - Base URL from import.meta.env.VITE_API_BASE_URL
   - Add request timeout: 30 seconds
   - Add retry logic: 3 retries on network error

5. Add PWA support via vite-plugin-pwa:
   - App name: AapdaMitra
   - Theme color: #c0392b
   - Background: #0f0f1a
   - Icons in /public/icons/
   - Offline fallback page
   - Cache API responses for offline map viewing

6. Performance checklist before deploy:
   - Run npm run build and check bundle size (target: < 500KB initial)
   - Verify Lighthouse score > 85 (Performance, Accessibility)
   - Test on 3G throttled network in Chrome DevTools
   - Verify all env vars are set in Vercel dashboard
```

---

### Prompt 16.3 — CI/CD Pipeline

```
Create a GitHub Actions CI/CD pipeline for AapdaMitra.

.github/workflows/deploy.yml:

name: AapdaMitra CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - name: Install dependencies
        run: cd backend && pip install -r requirements.txt
      - name: Run tests
        run: cd backend && pytest --cov=. --cov-fail-under=75 -v
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          # ... all other test secrets

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with: { node-version: '18' }
      - name: Install & build
        run: cd frontend && npm ci && npm run build
      - name: Run lint
        run: cd frontend && npm run lint

  deploy-backend:
    needs: test-backend
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Render
        run: curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_URL }}

  deploy-frontend:
    needs: test-frontend
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Vercel
        run: npx vercel --prod --token=${{ secrets.VERCEL_TOKEN }}

Add branch protection rules:
- Require PR review before merging to main
- Require all CI checks to pass
- No direct pushes to main
```

---

## 🧪 End-to-End Demo Test Prompt

### Final Integration Test

```
Create an end-to-end integration test that simulates a complete AapdaMitra disaster response pipeline.

backend/tests/test_e2e/test_full_pipeline.py:

async def test_kolkata_flood_scenario():
    """
    Full pipeline test: citizen report → verification → priority → alert generation → dispatch
    
    Scenario: Flash flood in Behala, Kolkata
    Expected: Complete in under 5 minutes with RED alert dispatched to all channels
    """
    
    Step 1: Mock Open-Meteo to return 87mm/hr rainfall for Kolkata coordinates
    Step 2: Mock USGS to return no earthquakes
    Step 3: Submit citizen report via POST /incidents:
       {
         "disaster_type": "FLOOD",
         "raw_text": "Massive flooding at Behala station. Cars submerged. Water rising fast.",
         "latitude": 22.4926,
         "longitude": 88.3248,
         "location_name": "Behala, Kolkata"
       }
    Step 4: Assert incident created in Firestore with status PENDING
    Step 5: Trigger verification agent manually
    Step 6: Assert verification_score >= 80, status = VERIFIED
    Step 7: Trigger priority agent
    Step 8: Assert severity = RED, priority_score >= 70
    Step 9: Trigger alert generation agent
    Step 10: Assert alerts created in EN, HI, BN languages
    Step 11: Trigger dispatch agent (mock all channels)
    Step 12: Assert all 5 channels were called with correct payloads
    Step 13: Simulate DM voice acknowledgment via POST /voice/acknowledgment/{incident_id}
    Step 14: Assert incident.acknowledged = True
    Step 15: Assert total time < 300 seconds (5 minutes)
    
    Print pipeline timing report at end.
    
Assert this passes in CI before any deployment.
```

---

## 📌 Quick Reference — API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /incidents | Optional | Submit citizen report |
| POST | /incidents/sos | Optional | SOS with GPS |
| GET | /incidents | Authority | List with filters |
| GET | /incidents/{id} | Authority | Full detail |
| PUT | /incidents/{id}/acknowledge | Authority | Acknowledge alert |
| GET | /dashboard/summary | Authority | Stats overview |
| GET | /dashboard/heatmap | Authority | Map heatmap data |
| GET | /dashboard/analytics | Authority | Charts data |
| GET | /dashboard/incidents/stream | Authority | SSE real-time feed |
| GET | /voice/twiml/{id} | Twilio | TwiML for voice call |
| POST | /voice/acknowledgment/{id} | Twilio | Acknowledgment webhook |
| POST | /auth/verify | None | Firebase token verify |
| GET | /users/me | User | Current user profile |
| GET | /health | None | Health check |

---

## 📌 Environment Variables Master List

```bash
# AI
GEMINI_API_KEY=

# Firebase
FIREBASE_PROJECT_ID=
FIREBASE_PRIVATE_KEY=
FIREBASE_CLIENT_EMAIL=
FIREBASE_DATABASE_URL=

# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# SendGrid
SENDGRID_API_KEY=

# Gupshup
GUPSHUP_API_KEY=
GUPSHUP_APP_NAME=

# NASA
NASA_FIRMS_API_KEY=

# App
SECRET_KEY=
ALLOWED_ORIGINS=https://aapda-mitra.vercel.app
```

---

*AapdaMitra 2.0 — Build Prompts v1.0 | Generated from PRD v1.0*
