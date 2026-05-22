import sys
import os

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.firebase_service import firebase_service
from config.settings import settings
import asyncio

print('Settings FIREBASE_PROJECT_ID=', settings.FIREBASE_PROJECT_ID)
print('Settings FIREBASE_CLIENT_EMAIL=', settings.FIREBASE_CLIENT_EMAIL)

async def init():
    try:
        await firebase_service.initialize(settings)
        print('Firebase initialized:', firebase_service._initialized)
    except Exception as e:
        print('Firebase init error:', e)

if __name__ == '__main__':
    asyncio.run(init())
