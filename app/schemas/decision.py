from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import EvidenceItem, MapPayload
from app.schemas.marine import PFZCandidate
from app.schemas.weather import WeatherReading, MarineConditions, HazardAlert
from app.schemas.gis import Route, GeofenceResult
from app.schemas.risk import RiskResult, RiskBandEnum

class CandidateStatusEnum(str, Enum):
    RECOMMENDED = "RECOMMENDED"
    CAUTION = "CAUTION"
    VIABLE = "VIABLE"
    HIGH_RISK = "HIGH_RISK"
    NOT_RECOMMENDED = "NOT_RECOMMENDED"
    REJECTED = "REJECTED"
    NO_SAFE_OPTION = "NO_SAFE_OPTION"

class CandidatePackage(BaseModel):
    zone_id: str
    pfz: Optional[PFZCandidate] = None
    weather: Optional[WeatherReading] = None
    marine_conditions: Optional[MarineConditions] = None
    hazards: List[HazardAlert] = []
    route: Optional[Route] = None
    geofence: Optional[GeofenceResult] = None
    risk: Optional[RiskResult] = None

class RecommendationItem(BaseModel):
    zone_id: str
    status: CandidateStatusEnum
    risk_band: RiskBandEnum
    risk_score: float

class AlternativeItem(BaseModel):
    zone_id: str
    status: CandidateStatusEnum = CandidateStatusEnum.REJECTED
    reason_code: str
    risk_score: Optional[float] = None

class FinalDecisionOutput(BaseModel):
    session_id: str
    language: str = "en"
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    execution_trace: List[Dict[str, Any]] = []
    recommendation: Optional[RecommendationItem] = None
    alternatives_considered: List[AlternativeItem] = []
    evidence: List[EvidenceItem] = []
    explanation_text: str = ""
    map_payload: MapPayload = Field(default_factory=MapPayload)
    disclaimer: str = ""
    generated_at: Optional[str] = None
