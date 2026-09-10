import os
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.config import settings
from app.orchestrator import orchestrator
from app.agents.marine_agent import marine_agent
from app.agents.weather_hazard_agent import weather_hazard_agent
from app.agents.gis_agent import gis_agent
from app.agents.risk_engine import risk_engine
from app.schemas.gis import LatLon, Route
from app.schemas.risk import RiskInput, RiskResult

app = FastAPI(
    title="ORCA — Marine EcOsystem Reasoning with Collaborative Agents",
    description="Agentic AI-powered Conversational Marine Intelligence Backend API (PS26176)",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths to compiled frontend
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
FRONTEND_ASSETS = os.path.join(FRONTEND_DIST, "assets")

if os.path.isdir(FRONTEND_ASSETS):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS), name="assets")

class QueryRequest(BaseModel):
    session_id: str = Field(..., example="sess_123")
    text: str = Field(..., example="I am at Ratnagiri. I want to go fishing tomorrow at 5 AM for 6 hours. Which fishing zone should I choose?")
    request_timestamp: Optional[str] = None
    prior_context: Optional[Dict[str, Any]] = None

class RouteRequest(BaseModel):
    origin: LatLon
    destination: LatLon

@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    return {
        "service": "ORCA Marine Intelligence Agent Platform",
        "version": "1.0.0",
        "mode": settings.orca_mode,
        "status": "online"
    }


@app.get("/api/health")
def get_health():
    return {
        "status": "ok",
        "mode": settings.orca_mode,
        "llm_provider": settings.llm_provider,
        "max_candidates": settings.max_candidates
    }

@app.post("/api/query")
def post_query(request: QueryRequest):
    """
    Primary conversational pipeline entry point.
    Runs NLU -> Planner -> Specialist Execution -> Risk Scoring -> Decision Reasoning.
    """
    try:
        result = orchestrator.process_query(
            session_id=request.session_id,
            text=request.text,
            prior_context=request.prior_context
        )
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution error: {str(e)}")

@app.get("/api/pfz")
def get_pfz(
    lat: float = Query(16.99, description="Latitude"),
    lon: float = Query(73.31, description="Longitude"),
    date: str = Query("2026-09-09", description="Date YYYY-MM-DD")
):
    """Direct PFZ lookup tool endpoint."""
    candidates = marine_agent.get_pfz_candidates(lat, lon, date)
    return {"lat": lat, "lon": lon, "date": date, "candidates": [c.model_dump() for c in candidates]}

@app.get("/api/weather")
def get_weather(
    lat: float = Query(16.99, description="Latitude"),
    lon: float = Query(73.31, description="Longitude"),
    datetime: str = Query("2026-09-09T05:00:00+05:30", description="ISO Datetime")
):
    """Direct Weather and Sea State lookup tool endpoint."""
    w = weather_hazard_agent.get_weather(lat, lon, datetime)
    m = weather_hazard_agent.get_marine_conditions(lat, lon, datetime)
    return {
        "weather": w.model_dump(),
        "marine_conditions": m.model_dump()
    }

@app.get("/api/hazards")
def get_hazards(
    lat: float = Query(16.99, description="Latitude"),
    lon: float = Query(73.31, description="Longitude"),
    datetime: str = Query("2026-09-09T05:00:00+05:30", description="ISO Datetime")
):
    """Direct Hazard alerts lookup tool endpoint."""
    hazards = weather_hazard_agent.get_hazards(lat, lon, datetime)
    return {"hazards": [h.model_dump() for h in hazards]}

@app.post("/api/route")
def post_route(request: RouteRequest):
    """Direct Coastal Routing and Geofence check endpoint."""
    route = gis_agent.get_route(request.origin, request.destination)
    geofence = gis_agent.check_geofence(route)
    return {
        "route": route.model_dump(),
        "geofence": geofence.model_dump()
    }

@app.post("/api/risk")
def post_risk(request: RiskInput):
    """Direct Deterministic Risk Engine evaluation endpoint."""
    res = risk_engine.compute_risk(request)
    return res.model_dump()

@app.get("/{full_path:path}")
def catch_all(full_path: str):
    """SPA client-side routing fallback for React Router (/map, /analytics, /assistant, etc.)."""
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

