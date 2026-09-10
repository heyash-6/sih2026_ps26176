from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import LatLon

class GeofenceStatusEnum(str, Enum):
    CLEAR = "clear"
    INTERSECTS = "intersects"
    NEAR_BOUNDARY = "near_boundary"

class Waypoint(BaseModel):
    lat: float
    lon: float

class Route(BaseModel):
    origin: LatLon
    destination: LatLon
    waypoints: List[Waypoint] = []
    distance_km: float
    estimated_travel_time_min: int
    assumed_speed_kmh: float = 15.0
    method: str = "coastal_approximation"

class GeofenceIntersection(BaseModel):
    zone_type: str  # international_boundary, marine_protected_area, restricted_zone, hazard_zone
    zone_name: str
    distance_into_zone_km: Optional[float] = 0.0

class GeofenceResult(BaseModel):
    status: GeofenceStatusEnum = GeofenceStatusEnum.CLEAR
    intersections: List[GeofenceIntersection] = []
    checked_zone_types: List[str] = [
        "international_boundary",
        "marine_protected_area",
        "restricted_zone"
    ]
