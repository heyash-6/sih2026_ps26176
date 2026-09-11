from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import LatLon, TimeWindow

class IntentEnum(str, Enum):
    FISHING_TRIP_PLANNING = "fishing_trip_planning"
    PFZ_LOOKUP = "pfz_lookup"
    SAFETY_CHECK = "safety_check"
    CONDITION_LOOKUP = "condition_lookup"
    HAZARD_ALERT_CHECK = "hazard_alert_check"
    CHLOROPHYLL_SST_LOOKUP = "chlorophyll_sst_lookup"
    ROUTE_PLANNING = "route_planning"
    PRODUCTIVITY_EXPLANATION = "productivity_explanation"
    GEOFENCE_CHECK = "geofence_check"
    MULTI_DAY_COMPARISON = "multi_day_comparison"
    FOLLOWUP = "followup"
    OTHER = "other"

class EntityBundle(BaseModel):
    location_text: Optional[str] = None
    location_latlon: Optional[LatLon] = None
    date: Optional[str] = Field(None, description="ISO format date YYYY-MM-DD")
    time_window: Optional[TimeWindow] = None
    duration_hours: Optional[float] = None
    vessel_id: Optional[str] = None

class NLUInput(BaseModel):
    session_id: str
    text: str
    request_timestamp: Optional[str] = None
    prior_context: Optional[Dict[str, Any]] = None

class NLUOutput(BaseModel):
    session_id: str
    language: str = Field("en", description="Language code: en, hi, mr")
    language_confidence: float = 1.0
    intent: IntentEnum = IntentEnum.FISHING_TRIP_PLANNING
    intent_confidence: float = 1.0
    entities: EntityBundle = Field(default_factory=EntityBundle)
    missing_required_fields: List[str] = []
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
