import pytest
from app.agents.marine_agent import marine_agent

def test_get_pfz_candidates():
    candidates = marine_agent.get_pfz_candidates(16.99, 73.31, "2026-09-09", radius_km=50.0)
    assert len(candidates) > 0
    # Check candidates are sorted ascending by distance_km
    for i in range(len(candidates) - 1):
        assert candidates[i].distance_km <= candidates[i+1].distance_km

def test_get_ocean_conditions():
    conds = marine_agent.get_ocean_conditions(16.99, 73.31, "2026-09-09")
    assert conds.sst_celsius > 0
    assert conds.chlorophyll_mg_m3 > 0

def test_explain_productivity_trend():
    trend = marine_agent.explain_productivity_trend(16.99, 73.31, ["2026-09-01", "2026-09-08"])
    assert trend.sst_delta_celsius != 0
    assert len(trend.likely_factors) > 0
