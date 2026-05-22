"""
Quick verification that RealtimeActivityLogger can be imported and initialized correctly.
"""
import asyncio
import sys
from config.settings import settings
from services.realtime_activity_logger import realtime_activity_logger

async def main():
    print(f"Firebase Database URL: {settings.FIREBASE_DATABASE_URL}")
    await realtime_activity_logger.initialize(settings)
    print(f"Realtime Activity Logger Initialized: {realtime_activity_logger._initialized}")
    print(f"Database Reference: {realtime_activity_logger._db_ref}")
    return "SUCCESS"

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        print(f"Verification Result: {result}")
        sys.exit(0)
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
