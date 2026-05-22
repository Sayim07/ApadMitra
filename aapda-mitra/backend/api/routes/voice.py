from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from services.voice_service import VoiceCallService
from services.firebase_service import firebase_service

router = APIRouter(prefix="/voice")
voice_service = VoiceCallService()


@router.get("/twiml/{incident_id}")
async def twiml(incident_id: str):
    incident = await firebase_service.get_incident(incident_id)
    if not incident:
        return PlainTextResponse("Incident not found", status_code=404)
    twiml_xml = voice_service.build_twiml_for_incident(incident)
    return Response(content=twiml_xml, media_type="application/xml")


@router.post("/acknowledgment/{incident_id}")
async def acknowledgment(incident_id: str, request: Request):
    form = await request.form()
    speech = form.get('SpeechResult') or form.get('SpeechResult'.lower()) or form.get('Digits')
    caller = form.get('From') or form.get('from')
    if speech:
        text = str(speech).lower()
        keywords = ["acknowledged", "confirmed", "received", "हाँ", "ठीक"]
        if any(k in text for k in keywords):
            await firebase_service.update_incident(incident_id, {"acknowledged": True, "acknowledged_by": caller})
            resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Say>Thank you. Acknowledgment recorded. Please check AapdaMitra dashboard for full incident details. Stay safe.</Say><Hangup/></Response>"
            return Response(content=resp, media_type="application/xml")

    resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Say>We did not receive your acknowledgment. Goodbye.</Say><Hangup/></Response>"
    return Response(content=resp, media_type="application/xml")


@router.post("/status-callback")
async def status_callback(request: Request):
    form = await request.form()
    call_sid = form.get('CallSid') or form.get('CallSid'.lower())
    call_status = form.get('CallStatus')
    # Update alerts in Firestore if possible
    if call_sid:
        # naive: search alerts by sid is not implemented; log for now
        pass
    return {"ok": True}
