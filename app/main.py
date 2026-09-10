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

@app.get("/api/ports")
def get_ports():
    """Retrieve catalog of all 20 Indian coastal hubs and their metadata."""
    from app.database.indian_coastal_registry import INDIAN_COASTAL_PORTS
    ports_summary = []
    for p in INDIAN_COASTAL_PORTS:
        ports_summary.append({
            "id": p["id"],
            "name": p["name"],
            "state": p["state"],
            "sector": p["sector"],
            "lat": p["lat"],
            "lon": p["lon"],
            "pfz_count": len(p["pfz_candidates"])
        })
    return {"ports": ports_summary, "count": len(ports_summary)}

@app.get("/api/pfz")
def get_pfz(
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    port: Optional[str] = Query(None, description="Port ID or 'all'"),
    date: str = Query("2026-09-09", description="Date YYYY-MM-DD")
):
    """Direct PFZ lookup tool endpoint supporting port ID, coordinates, or all Indian coast."""
    candidates = marine_agent.get_pfz_candidates(lat=lat, lon=lon, date=date, port_id=port)
    return {
        "port": port,
        "lat": lat,
        "lon": lon,
        "date": date,
        "candidates": [c.model_dump() for c in candidates],
        "count": len(candidates)
    }

@app.post("/api/sync")
def trigger_coastal_sync():
    """Trigger synchronization of real-time marine data across the Indian coastline to Supabase."""
    from app.database.data_pipeline import data_pipeline
    result = data_pipeline.sync_all_indian_coastal_hubs()
    return result

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

@app.get("/api/alerts")
def get_all_alerts():
    """Retrieve all active marine hazard advisories from Supabase database."""
    from app.database.supabase_client import supabase_client
    alerts = supabase_client.get_active_alerts(limit=20)
    return {"alerts": alerts, "count": len(alerts)}

@app.get("/api/analytics")
def get_analytics(period: str = Query("7", description="Time period: '24' for 24h, '7' for 7 days")):
    """Retrieve ocean observations time-series (SST, Chlorophyll, Waves) from Supabase."""
    from app.database.supabase_client import supabase_client
    days = 1 if period == "24" else 7
    data = supabase_client.get_ocean_analytics_timeseries(period_days=days)
    return data

@app.get("/api/history")
def get_history(limit: int = Query(10, description="Max records")):
    """Retrieve recent multi-agent marine analyses from Supabase."""
    from app.database.supabase_client import supabase_client
    analyses = supabase_client.get_recent_analyses(limit=limit)
    return {"analyses": analyses, "count": len(analyses)}

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = ""
    role: Optional[str] = "user"

@app.post("/api/auth/register")
def register_user(req: RegisterRequest):
    """
    Direct user registration bypassing Supabase default SMTP email rate limit.
    Uses Service Role key to create and pre-confirm user in auth.users.
    """
    import httpx
    url = settings.supabase_url.rstrip("/")
    key = settings.supabase_service_role_key or settings.supabase_anon_key

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    # Map role
    role_clean = req.role if req.role in ["user", "researcher", "admin"] else "user"

    payload = {
        "email": req.email.strip(),
        "password": req.password,
        "email_confirm": True,
        "user_metadata": {
            "full_name": req.full_name or req.email.split("@")[0],
            "role": role_clean
        }
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(f"{url}/auth/v1/admin/users", headers=headers, json=payload)
            if res.status_code in [200, 201]:
                return {"success": True, "user": res.json()}
            # If user already registered
            err_data = res.json() if res.headers.get("content-type", "").startswith("application/json") else {"msg": res.text}
            return {"success": False, "error": err_data.get("msg") or err_data.get("message") or "Registration failed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync")
def trigger_sync():
    """Manually trigger data synchronization for coastal hubs to Supabase."""
    from app.agents.weather_hazard_agent import weather_hazard_agent
    now_iso = "2026-09-10T05:00:00+05:30"
    hubs = [("Mumbai", 18.9400, 72.8300), ("Ratnagiri", 16.9902, 73.3120), ("Goa", 15.4989, 73.8278)]
    synced = []
    for name, lat, lon in hubs:
        w = weather_hazard_agent.get_weather(lat, lon, now_iso)
        m = weather_hazard_agent.get_marine_conditions(lat, lon, now_iso)
        synced.append({"hub": name, "temp": w.temperature_c, "waves": m.wave_height_m})
    return {"status": "synced", "hubs": synced}

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

