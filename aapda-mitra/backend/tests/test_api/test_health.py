import sys
import os
import asyncio

# Ensure backend package is importable
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from main import health


def test_health():
    res = asyncio.get_event_loop().run_until_complete(health())
    assert isinstance(res, dict)
    assert res.get("status") == "ok"
