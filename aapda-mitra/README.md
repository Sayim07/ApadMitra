# AapdaMitra 2.0 - Disaster Alert & Response Platform

A real-time disaster alerting and community resilience platform that combines multi-source incident monitoring, AI-powered verification, and coordinated emergency response across multiple communication channels.

## 🎯 Project Overview

**AapdaMitra** (आपदा मित्र - Disaster Friend) is designed to:
- **Detect** disasters in real-time from multiple sources (citizen reports, IoT sensors, seismic data)
- **Verify** incidents using multi-source corroboration and ML-based confidence scoring
- **Prioritize** responses based on severity, impact, and urgency
- **Alert** citizens and authorities through SMS, WhatsApp, Email, and Voice channels
- **Dispatch** emergency response teams with coordination dashboards
- **Track** incident resolution with action history and audit trails

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.11)
- **Database**: Firebase Firestore (NoSQL document store)
- **Media Storage**: Cloudinary (replaced Firebase Storage)
- **Queueing**: Redis (configurable) + Firestore fallback for notifications
- **AI/ML**: Google Generative AI (Gemini) for alert generation
- **Notification Channels**: Twilio (SMS/Voice), SendGrid (Email), Gupshup (WhatsApp)
- **Deployment**: Render (Backend), Vercel (Frontend), GitHub Actions (CI/CD)

### Frontend Stack
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Maps**: Leaflet + React-Leaflet + Leaflet.heat (heatmap visualization)
- **PWA**: Progressive Web App support with offline capabilities
- **Charts**: Recharts for analytics

## 📋 Project Structure

```
aapda-mitra/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── incidents.py           # Incident submission, acknowledge, assign, dispatch
│   │   │   ├── alerts.py              # Alert management, broadcast endpoint
│   │   │   ├── voice.py               # Twilio Voice callbacks
│   │   │   ├── auth.py                # JWT authentication
│   │   │   └── health.py              # Health check endpoint
│   │   └── middleware/
│   │       └── auth.py                # JWT verification middleware
│   ├── agents/
│   │   ├── monitoring_agent.py        # Monitor external APIs (USGS, OpenMeteo, NASA)
│   │   ├── verification_agent.py      # Multi-source incident verification
│   │   ├── priority_agent.py          # Incident prioritization
│   │   ├── alert_generation_agent.py  # Generate alerts in multiple languages
│   │   ├── dispatch_agent.py          # Multi-channel alert dispatch
│   │   └── pipeline.py                # Orchestrate agents sequentially
│   ├── services/
│   │   ├── firebase_service.py        # Firestore CRUD operations
│   │   ├── notification_service.py    # SMS, Email, WhatsApp, Voice wrappers
│   │   ├── notification_queue.py      # Persistent notification queue (Redis/Firestore)
│   │   ├── cloudinary_service.py      # Media upload service
│   │   └── voice_service.py           # Twilio VoiceML
│   ├── models/
│   │   ├── incident.py                # Incident Pydantic models
│   │   ├── alert.py                   # Alert models
│   │   ├── user.py                    # User/Authority models
│   │   └── action.py                  # Incident action audit models
│   ├── config/
│   │   └── settings.py                # Environment configuration (pydantic-settings)
│   ├── utils/
│   │   ├── retry_queue.py             # AsyncRetry and AsyncQueueWorker utilities
│   │   └── keepalive.py               # Scheduled health ping for Render
│   ├── tests/
│   │   ├── test_api/                  # API endpoint tests
│   │   ├── test_services/             # Service layer tests
│   │   ├── test_e2e/                  # End-to-end integration tests
│   │   ├── conftest.py                # Pytest configuration
│   │   └── test_*.py                  # Unit tests
│   ├── main.py                        # FastAPI app initialization
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Container build configuration
│   └── render.yaml                    # Render deployment manifest
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx        # Public landing page
│   │   │   ├── CitizenReportPage.jsx  # Citizen incident form
│   │   │   ├── SOSPage.jsx            # Emergency SOS alert
│   │   │   ├── Dashboard.jsx          # Authority dashboard
│   │   │   ├── IncidentDetail.jsx     # Incident details + actions
│   │   │   └── Login.jsx              # Authentication
│   │   ├── components/
│   │   │   ├── AuthProvider.jsx       # Firebase Auth context
│   │   │   ├── ProtectedRoute.jsx     # Route protection
│   │   │   ├── AuthorityPanel.jsx     # Authority control panel
│   │   │   └── DisasterMap.jsx        # Map with heatmap layer
│   │   ├── App.jsx                    # Root component with routing
│   │   ├── main.jsx                   # Vite entry point
│   │   ├── firebase.js                # Firebase config
│   │   └── styles.css                 # Global styles
│   ├── public/
│   │   ├── manifest.json              # PWA manifest
│   │   └── index.html                 # HTML template
│   ├── package.json                   # Node dependencies
│   └── vite.config.js                 # Vite + PWA plugin config
├── .github/
│   └── workflows/
│       └── deploy.yml                 # GitHub Actions CI/CD pipeline
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- Firebase project with Firestore database
- Cloudinary account
- Twilio, SendGrid, and Gupshup API credentials
- Google Generative AI API key

### Backend Setup

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Create .env file with:
   GEMINI_API_KEY=your_api_key
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_PRIVATE_KEY=your_private_key
   FIREBASE_CLIENT_EMAIL=your_email
   FIREBASE_DATABASE_URL=your_db_url
   
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=+1234567890
   
   SENDGRID_API_KEY=sg.xxx
   GUPSHUP_API_KEY=your_key
   GUPSHUP_APP_NAME=your_app
   NASA_FIRMS_API_KEY=your_key
   
   CLOUDINARY_CLOUD_NAME=your_cloud
   CLOUDINARY_API_KEY=your_key
   CLOUDINARY_API_SECRET=your_secret
   
   SECRET_KEY=your_jwt_secret
   ALLOWED_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
   
   # Optional: Redis queue
   REDIS_URL=redis://localhost:6379
   ```

4. **Run backend**
   ```bash
   python main.py
   # Server runs at http://localhost:8000
   ```

5. **Run tests**
   ```bash
   pytest tests/ -q
   # Expected: 22+ passed tests including E2E pipeline
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API endpoint**
   - Update frontend API base URL to point to backend
   - Configure Firebase in config files

3. **Run development server**
   ```bash
   npm run start
   # App runs at http://localhost:3000
   ```

4. **Build for production**
   ```bash
   npm run build
   # Generates optimized bundle in `dist/`
   ```

## 📡 API Endpoints

### Incidents
- `POST /incidents` - Submit new incident (multipart/form-data with media)
- `POST /incidents/sos` - Emergency SOS alert
- `GET /incidents` - List incidents (with filters)
- `GET /incidents/{id}` - Get incident details
- `PUT /incidents/{id}/acknowledge` - Authority acknowledge incident
- `POST /incidents/{id}/assign` - Assign to team and notify authorities
- `POST /incidents/{id}/dispatch` - Dispatch emergency response
- `GET /incidents/{id}/actions` - Get incident action history

### Alerts
- `GET /alerts` - List alerts
- `GET /alerts/{id}` - Get alert details
- `PUT /alerts/{id}/status` - Update alert status
- `POST /alerts/broadcast` - Send broadcast alert to all district contacts

### Voice (Twilio)
- `GET /voice/twiml/{incident_id}` - Generate voice message TwiML
- `POST /voice/acknowledgment/{incident_id}` - Voice acknowledgment webhook
- `POST /voice/status-callback` - Voice delivery status callback

### Health
- `GET /health` - Service health check

## 🧪 Testing

### Run all tests
```bash
cd backend
pytest tests/ -v
```

### Run specific test suites
```bash
# Unit tests
pytest tests/test_api/ -v

# Service tests
pytest tests/test_services/ -v

# End-to-end integration tests
pytest tests/test_e2e/ -v
```

### Test Results
- **22+ tests passing** (includes 9 E2E integration tests)
- Full pipeline coverage: incident → verification → priority → alerts → dispatch
- Notification queue testing (Redis and Firestore fallback)
- Authority workflow testing

## 🔄 Key Workflows

### Incident Submission to Dispatch Pipeline

```
1. Citizen/Sensor submits incident
   ↓
2. VerificationAgent:
   - Check geolocation validity
   - Corroborate with multiple sources
   - Compute trust score
   ↓
3. PriorityAgent:
   - Calculate severity (RED/YELLOW/GREEN)
   - Estimate impact radius
   ↓
4. AlertGenerationAgent:
   - Generate citizen SMS/WhatsApp in multiple languages
   - Generate authority briefing
   ↓
5. DispatchAgent:
   - Gather authority contacts
   - Select channels based on severity
   - Enqueue notifications to persistent queue
   ↓
6. NotificationQueue:
   - Process from Redis (if configured) or Firestore
   - Retry with exponential backoff
   - Update alert status
```

### Notification Queue Processing

```
Enqueue notification (SMS/Email/WhatsApp/Voice)
   ↓
If Redis configured:
  - LPUSH to "notification_queue" list
  - BRPOP with retry on error
Else:
  - Write to Firestore "notification_queue" collection
  - Poll for PENDING docs
   ↓
Process with AsyncRetry (max 3 attempts)
   ↓
Send via appropriate service (Twilio/SendGrid/Gupshup)
   ↓
Update status: DONE/FAILED
```

## 🌍 Deployment

### Deploy Backend to Render

1. Connect GitHub repository to Render
2. Create Web Service with build and start commands
3. Configure all environment variables
4. Keepalive runs every 14 minutes to prevent free tier shutdown

### Deploy Frontend to Vercel

1. Connect GitHub repository to Vercel
2. Configure build: `npm run build` from `frontend/` directory
3. Set environment variables for API URL and Firebase config

### CI/CD Pipeline (GitHub Actions)

`.github/workflows/deploy.yml` runs:
1. Backend tests (`pytest tests/`)
2. Frontend build validation
3. Triggers deployment on success

## 🔐 Security Features

- **Authentication**: JWT tokens (PyJWT)
- **Password Hashing**: Bcrypt via passlib
- **CORS**: Configurable allowed origins
- **Environment Variables**: All secrets in .env (not committed)
- **Rate Limiting**: SlowAPI for endpoint protection
- **Input Validation**: Pydantic strict schema validation

## 📈 Performance Features

- **Async Processing**: AsyncIO for concurrent operations
- **Connection Pooling**: Firestore client reuse
- **Notification Queue**: Asynchronous dispatch with retry logic
- **Lazy Imports**: Optional dependencies imported only when needed
- **Frontend**: Vite code splitting, tree-shaking, PWA caching
- **Heatmap Visualization**: Leaflet.heat for incident density mapping

## 📝 Implementation Status

### ✅ Completed
- Backend API with FastAPI
- Firebase Firestore integration
- Cloudinary media storage (replaced Firebase Storage)
- All notification channels (SMS, Email, WhatsApp, Voice)
- Agent pipeline orchestration
- Async notification queue with Redis and Firestore support
- Frontend React + Vite with authority UI
- Incident map with heatmap visualization
- PWA support with offline capabilities
- GitHub Actions CI/CD pipeline
- 22+ integration and unit tests
- Comprehensive E2E testing

### 🔧 Configuration Needed
- Firebase project credentials
- Twilio account SID and token
- SendGrid API key
- Gupshup credentials
- Cloudinary account
- Google Generative AI API key
- Redis instance (optional, Firestore fallback available)
- Render and Vercel deployment hooks

## 🆘 Troubleshooting

### Backend Tests Failing
```bash
# Set all required environment variables
export GEMINI_API_KEY=... 
export FIREBASE_PROJECT_ID=...
# Run tests
pytest tests/ -v
```

### Frontend Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Notification Queue Not Processing
- Check if Redis is running (if configured)
- Verify Firestore database is accessible
- Check notification service credentials (Twilio, SendGrid, Gupshup)

---

**Version**: 2.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: May 21, 2026  
**Test Coverage**: 22+ tests passing
