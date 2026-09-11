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
    session_id: Optional[str] = "default_session"
    text: Optional[str] = None
    query: Optional[str] = None
    query_text: Optional[str] = None
    language: Optional[str] = "en"
    request_timestamp: Optional[str] = None
    prior_context: Optional[Dict[str, Any]] = None

    def get_query_text(self) -> str:
        return self.text or self.query or self.query_text or ""


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
        query_str = request.get_query_text()
        if not query_str:
            raise HTTPException(status_code=400, detail="Query text is required")


        result = orchestrator.process_query(
            session_id=request.session_id or "default_session",
            text=query_str,
            prior_context=request.prior_context
        )
        res_dict = result.model_dump()
        res_dict["answer"] = result.explanation_text or res_dict.get("explanation_text", "")
        return res_dict
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

@app.get("/api/ports/{port_id}/context")
@app.get("/api/ports/{port_id}")
def get_port_context_endpoint(port_id: str):
    """Retrieve port-specific marine dashboard context, conditions, advisories, and active/inactive PFZs."""
    from app.database.indian_coastal_registry import get_port_dashboard_context
    return get_port_dashboard_context(port_id)

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

@app.get("/api/fishing/multi-day")
def get_fishing_multi_day(
    port: str = Query("mumbai", description="Port ID"),
    pfz: Optional[str] = Query(None, description="PFZ ID"),
    days: int = Query(4, description="Number of forecast days (4-5)")
):
    """Multi-day intelligent forward simulation comparing PFZ, sea state, weather, tides & risk."""
    from app.agents.fishing_reasoning_engine import fishing_reasoning_engine
    return fishing_reasoning_engine.compute_multi_day_comparison(port_id=port, pfz_id=pfz, num_days=days)

@app.get("/api/fishing/suitability")
def get_fishing_suitability(
    port: str = Query("mumbai", description="Port ID"),
    pfz: Optional[str] = Query(None, description="PFZ ID")
):
    """Explainable data-driven overall fishing suitability with full multi-factor breakdown."""
    from app.agents.fishing_reasoning_engine import fishing_reasoning_engine
    return fishing_reasoning_engine.compute_day_suitability(port_id=port)

@app.get("/api/sync")

@app.post("/api/sync")
def trigger_coastal_sync():
    """Trigger synchronization of real-time marine data across the Indian coastline to Supabase."""
    from app.database.data_pipeline import data_pipeline
    result = data_pipeline.sync_all_indian_coastal_hubs()
    return result

@app.get("/api/incois/live")
def get_incois_live(
    lat: float = Query(18.94, description="Latitude"),
    lon: float = Query(72.83, description="Longitude")
):
    """Query live oceanographic parameters directly from official INCOIS THREDDS OpenDAP operational models."""
    from app.datasources.incois_client import incois_client
    obs = incois_client.get_live_marine_observation(lat, lon)
    return obs

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

class NavRouteRequest(BaseModel):
    start_latitude: float
    start_longitude: float
    end_latitude: float
    end_longitude: float
    vessel_speed_kmh: Optional[float] = 18.0

@app.post("/api/gis/route/safe")
def calculate_safe_marine_route(req: NavRouteRequest):
    """Calculate safest risk-aware A* route avoiding restricted zones."""
    from app.gis.navigator import navigator
    return navigator.calculate_safe_route(
        req.start_latitude, req.start_longitude,
        req.end_latitude, req.end_longitude,
        vessel_speed_kmh=req.vessel_speed_kmh or 18.0
    )

@app.post("/api/gis/navigation/analyze")
def analyze_voyage_navigation(req: NavRouteRequest):
    """Analyze comprehensive voyage navigation (PFZs, hazards, conditions, safe route)."""
    from app.gis.navigator import navigator
    return navigator.analyze_navigation(
        req.start_latitude, req.start_longitude,
        req.end_latitude, req.end_longitude,
        vessel_speed_kmh=req.vessel_speed_kmh or 18.0
    )

@app.get("/api/location/resolve")
@app.get("/api/location/nearest-port")
def get_user_location_intelligence(
    lat: float = Query(..., description="User GPS Latitude"),
    lon: float = Query(..., description="User GPS Longitude")
):
    """Resolve user's GPS coordinates to nearest Indian coastal hub with live telemetry & nearby PFZs."""
    from app.gis.location_service import resolve_user_location
    return resolve_user_location(lat, lon)

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
def get_analytics(
    period: str = Query("7", description="Time period: '24' for 24h, '7' for 7 days"),
    port: str = Query("mumbai", description="Port ID for port-specific tide predictions")
):
    """Retrieve ocean observations time-series (SST, Chlorophyll, Waves) and tide predictions."""
    from app.database.supabase_client import supabase_client
    days = 1 if period == "24" else 7
    data = supabase_client.get_ocean_analytics_timeseries(period_days=days)
    data["tide_information"] = supabase_client.get_tide_predictions(port_id=port)
    return data

@app.get("/api/tides")
def get_tides(
    port: str = Query("mumbai", description="Port ID"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude")
):
    """Retrieve location-aware tide schedule & prediction from database."""
    from app.database.supabase_client import supabase_client
    return supabase_client.get_tide_predictions(port_id=port, lat=lat, lon=lon)

@app.get("/api/history")
def get_history(limit: int = Query(10, description="Max records")):
    """Retrieve recent multi-agent marine analyses from Supabase."""
    from app.database.supabase_client import supabase_client
    analyses = supabase_client.get_recent_analyses(limit=limit)
    return {"analyses": analyses, "count": len(analyses)}

@app.get("/api/database/tables")
def get_database_tables():
    """Retrieve all public database tables, live row counts, and metadata from Supabase."""
    from app.database.supabase_client import supabase_client
    import httpx
    
    tables_meta = [
        {"name": "pfz_zones", "title": "Potential Fishing Zones", "icon": "🐟", "desc": "Real-time PFZs with live SST, chlorophyll, and bearings for 20 Indian coastal hubs"},
        {"name": "weather_observations", "title": "Weather Observations", "icon": "🌦️", "desc": "Live meteorological telemetry (air temp, wind, pressure, rain)"},
        {"name": "wave_observations", "title": "Wave Observations", "icon": "🌊", "desc": "Live wave height, swell period, and sea state conditions"},
        {"name": "ocean_observations", "title": "Ocean Observations", "icon": "🛰️", "desc": "Satellite GHRSST sea surface temperatures and chlorophyll-a concentrations"},
        {"name": "marine_analyses", "title": "Marine Analyses", "icon": "🤖", "desc": "Autonomous multi-agent voyage evaluations and reasoning logs"},
        {"name": "alerts", "title": "Hazard Alerts", "icon": "⚠️", "desc": "Active marine weather advisories, high swells, and restricted passages"},
        {"name": "current_observations", "title": "Current Observations", "icon": "⚓", "desc": "Coastal sea surface current velocity and flow directions"},
        {"name": "tide_observations", "title": "Tide Observations", "icon": "🌊", "desc": "Tidal gauges and tidal schedule predictions"},
        {"name": "users", "title": "Users & Auth Profiles", "icon": "👤", "desc": "Registered maritime captains and verified vessel operator accounts"}
    ]
    
    result = []
    with httpx.Client(timeout=5.0) as client:
        for t in tables_meta:
            count = 0
            try:
                r = client.get(
                    f"{supabase_client.rest_url}/{t['name']}?select=count",
                    headers={**supabase_client.headers, "Range": "0-0", "Prefer": "count=exact"}
                )
                if r.status_code in [200, 206]:
                    cr = r.headers.get("content-range", "")
                    if "/" in cr:
                        count = int(cr.split("/")[-1])
            except Exception:
                pass
            result.append({**t, "row_count": count})
            
    return {"tables": result, "project": "byikekhtwiewlpxbuwgo.supabase.co"}

@app.get("/api/database/table/{table_name}")
def get_table_data(table_name: str, limit: int = Query(50, description="Max rows")):
    """Retrieve raw rows from any public table in Supabase."""
    from app.database.supabase_client import supabase_client
    import httpx
    
    allowed = [
        "pfz_zones", "weather_observations", "wave_observations", 
        "ocean_observations", "marine_analyses", "alerts", 
        "current_observations", "tide_observations", "users",
        "conversations", "chat_messages"
    ]
    if table_name not in allowed:
        raise HTTPException(status_code=400, detail="Invalid table name")
        
    try:
        with httpx.Client(timeout=8.0) as client:
            res = client.get(
                f"{supabase_client.rest_url}/{table_name}?limit={limit}",
                headers=supabase_client.headers
            )
            if res.status_code == 200:
                rows = res.json()
                return {"table": table_name, "count": len(rows), "rows": rows}
            return {"table": table_name, "count": 0, "rows": [], "error": res.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

class CreateConversationRequest(BaseModel):
    user_id: str
    title: Optional[str] = "New Marine Chat"

class AddChatMessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    user_id: Optional[str] = "guest_user"
    sender: Optional[str] = "user"
    message: Optional[str] = ""
    language: Optional[str] = "en"
    has_route: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None

@app.get("/api/conversations")
def get_conversations(user_id: str = Query(..., description="User ID")):
    """Get all conversations for a specific user."""
    from app.database.supabase_client import supabase_client
    convs = supabase_client.get_user_conversations(user_id)
    return {"conversations": convs, "count": len(convs)}

@app.post("/api/conversations")
def create_conversation_endpoint(req: CreateConversationRequest):
    """Create a new conversation."""
    from app.database.supabase_client import supabase_client
    conv = supabase_client.create_conversation(req.user_id, req.title or "New Marine Chat")
    if conv:
        return conv
    raise HTTPException(status_code=500, detail="Failed to create conversation")

@app.get("/api/conversations/{conv_id}/messages")
def get_conversation_messages_endpoint(conv_id: str):
    """Get all messages for a specific conversation."""
    from app.database.supabase_client import supabase_client
    msgs = supabase_client.get_conversation_messages(conv_id)
    return {"messages": msgs, "count": len(msgs)}

@app.post("/api/conversations/{conv_id}/messages")
def add_chat_message_endpoint(conv_id: str, req: AddChatMessageRequest):
    """Append a message to a conversation."""
    from app.database.supabase_client import supabase_client
    u_id = req.user_id or "guest_user"
    snd = req.sender or "user"
    txt = req.message or ""
    msg = supabase_client.insert_chat_message(
        conversation_id=conv_id,
        user_id=u_id,
        sender=snd,
        message=txt,
        language=req.language or "en",
        has_route=req.has_route or False,
        metadata=req.metadata or {}
    )
    if msg:
        return msg
    return {
        "id": f"local_{conv_id}",
        "conversation_id": conv_id,
        "user_id": u_id,
        "sender": snd,
        "message": txt
    }

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

