from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import TimeWindow

class HazardTypeEnum(str, Enum):
    LIGHTNING = "lightning"
    CYCLONE = "cyclone"
    HIGH_WAVE = "high_wave"
    STORM_SURGE = "storm_surge"
    STRONG_WIND = "strong_wind"
    OTHER = "other"

class SeverityEnum(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"

class WeatherReading(BaseModel):
    lat: float
    lon: float
    datetime: str
    wind_speed_kmh: float
    wind_direction_deg: float
    rain_probability_pct: float
    air_temp_celsius: float
    source: str = "Open-Meteo / IMD"

class MarineConditions(BaseModel):
    lat: float
    lon: float
    datetime: str
    wave_height_m: float
    swell_period_s: float
    sea_state: str = "slight"  # calm, smooth, slight, moderate, rough, high
    source: str = "INCOIS forecast"

class HazardAlert(BaseModel):
    hazard_type: HazardTypeEnum
    severity: SeverityEnum
    active_window: TimeWindow
    area_description: str
    source: str = "IMD / INCOIS bulletin"
    advisory_text_raw: Optional[str] = None
