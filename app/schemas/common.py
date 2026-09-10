from typing import Optional, List, Any
from pydantic import BaseModel, Field

class LatLon(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    resolved_from: Optional[str] = None
    method: Optional[str] = None

class TimeWindow(BaseModel):
    start: str = Field(..., description="Start time ISO string or HH:MM")
    end: str = Field(..., description="End time ISO string or HH:MM")

class EvidenceItem(BaseModel):
    claim: str
    source: str

class MapPayload(BaseModel):
    candidates: List[dict] = []
    routes: List[dict] = []
    geofence_zones_checked: List[str] = []
    hazards: List[dict] = []

class ErrorDetail(BaseModel):
    tool: str
    error_message: str
