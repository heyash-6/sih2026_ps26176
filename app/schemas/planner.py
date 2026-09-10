from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.nlu import EntityBundle, IntentEnum
from app.schemas.common import ErrorDetail

class ExecutionTraceStep(BaseModel):
    step: int
    tool: str
    status: str = "done"  # done, failed, skipped
    duration_ms: int = 0
    details: Optional[str] = None

class PlanStepItem(BaseModel):
    step: int
    tool: str
    params: Dict[str, Any] = {}

class PlanInput(BaseModel):
    session_id: str
    intent: IntentEnum
    entities: EntityBundle

class PlanOutput(BaseModel):
    session_id: str
    plan: List[PlanStepItem] = []
    execution_trace: List[ExecutionTraceStep] = []
    results: Dict[str, Any] = {}
    errors: List[ErrorDetail] = []
