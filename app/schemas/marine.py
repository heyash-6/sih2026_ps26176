from typing import List, Optional
from pydantic import BaseModel, Field

class PFZCandidate(BaseModel):
    zone_id: str
    lat: float
    lon: float
    distance_km: float
    date: str
    sst_celsius: float
    chlorophyll_mg_m3: float
    source: str = "INCOIS PFZ Advisory"
    confidence: str = "advisory"
    confidence_score: Optional[float] = None
    name: Optional[str] = None
    sector: Optional[str] = None
    port_id: Optional[str] = None
    port_name: Optional[str] = None
    bearing_deg: Optional[float] = None
    depth_m: Optional[float] = None

class TideSchedule(BaseModel):
    high: List[str] = []
    low: List[str] = []

class OceanConditions(BaseModel):
    lat: float
    lon: float
    date: str
    sst_celsius: float
    chlorophyll_mg_m3: float
    tide: Optional[TideSchedule] = None
    source: str = "INCOIS Ocean State Advisory"

class ProductivityTrend(BaseModel):
    region: str
    baseline_window: List[str]
    current_window: List[str]
    sst_delta_celsius: float
    chlorophyll_delta_pct: float
    likely_factors: List[str] = []
    source: str = "derived from ocean dataset"
