from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.weather import HazardAlert, SeverityEnum
from app.schemas.gis import GeofenceStatusEnum

class RiskBandEnum(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

class RiskInput(BaseModel):
    zone_id: str
    distance_km: float
    wave_height_m: float
    wind_speed_kmh: float
    hazards: List[HazardAlert] = []
    geofence_status: GeofenceStatusEnum = GeofenceStatusEnum.CLEAR
    trip_duration_hours: float = 6.0

class ComponentRiskBreakdown(BaseModel):
    wave_risk: float
    wind_risk: float
    hazard_risk: float
    distance_duration_risk: float
    geofence_risk: float

class RiskResult(BaseModel):
    zone_id: str
    total_risk: float
    band: RiskBandEnum
    components: ComponentRiskBreakdown
    weights_used: Dict[str, float]
    hard_block: bool = False
    flags: List[str] = []
    disclaimer: str
