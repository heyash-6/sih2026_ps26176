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
    source: str = "INCOIS PFZ Advisory (demo snapshot)"
    confidence: str = "advisory"

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
