import pytest
from app.schemas.gis import LatLon, GeofenceStatusEnum
from app.agents.gis_agent import gis_agent

def test_geocode():
    coords = gis_agent.geocode("Ratnagiri")
    assert coords is not None
    assert abs(coords.lat - 16.9902) < 0.05
    assert abs(coords.lon - 73.3120) < 0.05

def test_distance_km():
    p1 = LatLon(lat=16.99, lon=73.31)
    p2 = LatLon(lat=16.98, lon=73.12)
    dist = gis_agent.distance_km(p1, p2)
    assert dist > 15.0 and dist < 25.0

def test_geofence_intersection():
    p1 = LatLon(lat=16.99, lon=73.31)
    # Point inside Angria Bank Marine Sanctuary Buffer Zone in geofences.json
    p_inside = LatLon(lat=16.85, lon=73.10)
    route = gis_agent.get_route(p1, p_inside)
    gf = gis_agent.check_geofence(route)
    assert gf.status == GeofenceStatusEnum.INTERSECTS
    assert len(gf.intersections) > 0
