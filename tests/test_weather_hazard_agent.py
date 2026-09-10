import pytest
from app.agents.weather_hazard_agent import weather_hazard_agent

def test_get_weather():
    w = weather_hazard_agent.get_weather(16.99, 73.31, "2026-09-09T05:00:00+05:30")
    assert w.wind_speed_kmh >= 0
    assert w.air_temp_celsius > 0

def test_get_marine_conditions():
    m = weather_hazard_agent.get_marine_conditions(16.99, 73.31, "2026-09-09T05:00:00+05:30")
    assert m.wave_height_m >= 0
    assert m.sea_state in ["calm", "slight", "moderate", "rough", "high"]

def test_get_hazards():
    hazards = weather_hazard_agent.get_hazards(16.99, 73.31, "2026-09-09T05:00:00+05:30")
    assert isinstance(hazards, list)
