# Firebase Realtime Database Activity Logging Implementation

## Overview
This implementation adds real-time activity logging to Firebase Realtime Database for the AapdaMitra app. Key events (login, logout, file uploads, incident submissions) are automatically logged and appear in the Firebase console immediately.

## Architecture

### Core Service: `backend/services/realtime_activity_logger.py`
A singleton service that handles all writes to Firebase Realtime Database using a **fire-and-forget** pattern:
- Never blocks login or upload flows
- Errors are logged but don't propagate
- Uses `asyncio.create_task()` for non-blocking execution
- Gracefully handles Firebase initialization state

### Data Paths Structure
```
/activity/
  ├── logins/
  │   └── {uid}/
  │       └── {pushId}/
  │           ├── uid
  │           ├── email
  │           ├── displayName
  │           ├── role
  │           ├── loginAt
  │           ├── lastSeen
  │           └── source
  ├── users/
  │   └── {uid}/
  │       ├── uid
  │       ├── email
  │       ├── displayName
  │       ├── role
  │       ├── lastSeen
  │       ├── isOnline
  │       └── logoutAt (added on logout)
  ├── uploads/
  │   └── {pushId}/
  │       ├── userId
  │       ├── incidentId
  │       ├── fileName
  │       ├── fileUrl
  │       ├── fileType
  │       ├── uploadedAt
  │       └── status
  └── incidents/
      └── {incidentId}/
          ├── incidentId
          ├── status
          ├── severity
          ├── disasterType
          ├── location
          ├── submittedAt
          └── lastUpdated
```

## Integration Points

### 1. **App Startup** (`main.py`)
```python
@app.on_event("startup")
async def startup_event():
    # ... existing Firebase initialization ...
    await realtime_activity_logger.initialize(settings)
```
- Initializes RTDB connection using `FIREBASE_DATABASE_URL` from environment
- Runs during app startup; errors don't crash the app

### 2. **Login Flow** (`api/routes/users.py` - `/auth/verify` endpoint)
After successful token verification:
```python
await realtime_activity_logger.log_login(
    uid=uid,
    email=decoded.get("email", ""),
    display_name=display_name,
    role=user_role,
    source="web"
)
```
- Called after user profile is verified
- Writes to `/activity/logins/{uid}/{pushId}` (new entry each login)
- Updates `/activity/users/{uid}` with online status

### 3. **Incident Upload Flow** (`api/routes/incidents.py` - POST `/incidents`)
After files are uploaded to Cloudinary:
```python
for idx, url in enumerate(media_urls):
    await realtime_activity_logger.log_upload(
        user_id="anonymous",
        incident_id=incident_id,
        file_name=file.filename,
        file_url=url,
        file_type=file.content_type
    )

await realtime_activity_logger.log_incident_submission(
    incident_id=incident_id,
    status=VerificationStatus.PENDING.value,
    severity=SeverityLevel.UNASSIGNED.value,
    disaster_type=data.get("disaster_type"),
    location={...}
)
```
- Each file upload creates an entry in `/activity/uploads/{pushId}`
- Incident metadata updates `/activity/incidents/{incidentId}`

## Key Features

### Non-Blocking Behavior
All activity logging uses `asyncio.create_task()` to execute asynchronously:
- **No blocking on login**: User receives response immediately
- **No blocking on upload**: File upload completes regardless of RTDB status
- **Error handling**: Exceptions caught and logged; never raised

### Error Resilience
```python
try:
    # Write to RTDB
except Exception as e:
    logger.exception(f"Error logging activity: {e}")
    # Continue without raising
```

### Configuration
```env
FIREBASE_DATABASE_URL=https://hackarena-6bde0-default-rtdb.firebaseio.com
```
- URL is set in `.env` and loaded via `settings.FIREBASE_DATABASE_URL`
- Must point to correct Firebase project Realtime Database

## Firebase Console Visibility

### Real-Time Updates
1. Open [Firebase Console](https://console.firebase.google.com) → Select "hackarena-6bde0" project
2. Navigate to **Realtime Database** tab
3. Expand `/activity/` node
4. Login events appear under `/activity/logins/{uid}/`
5. Upload events appear under `/activity/uploads/`
6. User online status updates appear under `/activity/users/{uid}/`

### Live Monitoring
- Changes show in Firebase Console within 1-2 seconds
- Timestamp fields (`loginAt`, `uploadedAt`, `lastUpdated`) track when events occurred in UTC ISO format
- Use Firebase's query/filtering tools to analyze activity patterns

## Testing the Implementation

### Verify Logger Initialization
```bash
cd backend
python verify_realtime_logger.py
```

### Manual Test Flow
1. Start the backend: `python -m uvicorn main:app --reload`
2. Trigger login via frontend or API:
   ```bash
   curl -X POST http://localhost:8000/auth/verify \
     -H "Content-Type: application/json" \
     -d '{"id_token": "YOUR_VALID_TOKEN"}'
   ```
3. Open Firebase Console and check `/activity/logins/` for new entry

### Check Test Suite
```bash
python -m pytest tests/ -q
```
- All existing tests pass with realtime logger integration
- Logger doesn't interfere with existing Firestore operations

## Monitoring & Debugging

### Log Output
The logger uses Python's standard logging module. Check logs for:
```
INFO: Logged login for user {uid}
INFO: Logged upload for incident {incident_id}
INFO: Logged incident submission {incident_id}
ERROR: Error logging login for user {uid}: {error}
```

### Firebase Diagnostics
- Open Firebase Console → Project Settings → Realtime Database Rules
- Check if rules allow writes to `/activity/` paths
- Verify service account has database write permissions

### Network Connectivity
- Confirm `FIREBASE_DATABASE_URL` is reachable from backend environment
- Check firewall/security group allows HTTPS to `*.firebaseio.com`

## Future Enhancements

1. **Logout Flow**: Add automatic logout logging when detected in middleware
2. **Batch Writes**: For high-volume uploads, batch multiple events before writing
3. **Data Retention**: Add TTL (Time-To-Live) rules for activity logs in Realtime Database
4. **Analytics**: Build dashboards querying `/activity/` data for user patterns
5. **Real-time Dashboard**: Frontend can subscribe to `onValue()` listeners on `/activity/users/` for live user status

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Fire-and-forget pattern | Login/upload MUST NOT be blocked by RTDB write |
| Separate from Firestore | Firestore used for persistent data; RTDB for real-time visibility |
| Singleton instance | Single connection reduces Firebase Admin SDK overhead |
| UTC ISO timestamps | Ensures consistency across timezones; Firebase stores natively |
| Push keys for logins | Each login is separate event; push() generates unique ID |
| Non-throwing error handling | App continues even if RTDB temporarily unavailable |

