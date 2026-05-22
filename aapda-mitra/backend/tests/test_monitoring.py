import asyncio
from agents.monitoring_agent import MonitoringAgent


def test_monitor_earthquake_api_returns_list():
    m = MonitoringAgent()
    res = asyncio.get_event_loop().run_until_complete(m.monitor_earthquake_api())
    assert isinstance(res, list)


def test_monitor_weather_apis_returns_list():
    m = MonitoringAgent()
    res = asyncio.get_event_loop().run_until_complete(m.monitor_weather_apis())
    assert isinstance(res, list)
