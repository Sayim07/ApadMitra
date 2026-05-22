import asyncio
import os

from services.notification_service import SMSService, WhatsAppService, EmailService
from services.voice_service import VoiceCallService


def test_sms_placeholder():
    svc = SMSService()
    res = asyncio.get_event_loop().run_until_complete(svc.send_sms('+10000000000', 'test'))
    assert isinstance(res, dict)
    assert 'status' in res


def test_whatsapp_placeholder():
    svc = WhatsAppService()
    res = asyncio.get_event_loop().run_until_complete(svc.send_whatsapp('+10000000000', 'hello'))
    assert isinstance(res, dict)


def test_email_placeholder():
    svc = EmailService()
    res = asyncio.get_event_loop().run_until_complete(svc.send_email('test@example.com', 'hi', '<p>hi</p>'))
    assert isinstance(res, dict)


def test_voice_placeholder():
    svc = VoiceCallService()
    res = asyncio.get_event_loop().run_until_complete(svc.place_emergency_call('+10000000000', 'this is a test', 'incident-test'))
    assert isinstance(res, dict)
