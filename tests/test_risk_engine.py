import pytest
from app.schemas.risk import RiskInput, RiskBandEnum
from app.schemas.weather import HazardAlert, HazardTypeEnum, SeverityEnum
from app.schemas.common import TimeWindow
from app.schemas.gis import GeofenceStatusEnum
from app.agents.risk_engine import risk_engine

def test_calm_conditions_low_risk():
    inp = RiskInput(
        zone_id="PFZ-LOW",
        distance_km=10.0,
        wave_height_m=0.4,
        wind_speed_kmh=10.0,
        hazards=[],
        geofence_status=GeofenceStatusEnum.CLEAR,
        trip_duration_hours=4.0
    )
    res = risk_engine.compute_risk(inp)
    assert res.band == RiskBandEnum.LOW
    assert res.total_risk < 25.0
    assert res.hard_block is False

def test_geofence_intersect_hard_block():
    inp = RiskInput(
        zone_id="PFZ-BLOCKED",
        distance_km=15.0,
        wave_height_m=0.8,
        wind_speed_kmh=12.0,
        hazards=[],
        geofence_status=GeofenceStatusEnum.INTERSECTS,
        trip_duration_hours=6.0
    )
    res = risk_engine.compute_risk(inp)
    assert res.hard_block is True
    assert "intersects_restricted_zone" in res.flags

def test_severe_hazard_high_risk():
    hz = HazardAlert(
        hazard_type=HazardTypeEnum.LIGHTNING,
        severity=SeverityEnum.SEVERE,
        active_window=TimeWindow(start="04:00", end="12:00"),
        area_description="Northern sector"
    )
    inp = RiskInput(
        zone_id="PFZ-HAZARD",
        distance_km=25.0,
        wave_height_m=2.5,
        wind_speed_kmh=35.0,
        hazards=[hz],
        geofence_status=GeofenceStatusEnum.CLEAR,
        trip_duration_hours=6.0
    )
    res = risk_engine.compute_risk(inp)
    assert res.band in [RiskBandEnum.HIGH, RiskBandEnum.VERY_HIGH]
    assert res.total_risk > 50.0
