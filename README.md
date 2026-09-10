# ORCA — Marine EcOsystem Reasoning with Collaborative Agents (PS26176)
**Agentic AI-Powered Conversational Decision Platform Backend**

This repository contains the complete AI agent backend for **ORCA** (Problem Statement PS26176 for SIH 2026). It autonomously interprets natural-language queries in English, Hindi, and Marathi, plans tasks, invokes specialized data tools, calculates deterministic safety risks, and generates evidence-backed recommendations and map payloads.

---

## 🏛️ System Architecture

```
User Query (English, Hindi, Marathi)
         │
         ▼
[1] NLU Agent (app/agents/nlu_agent.py) ────────► Intent & Entity Parsing
         │
         ▼
[2] Planner Agent (app/agents/planner_agent.py) ─► Task Decomposition & Tool Dispatch
         │
         ├──► [3] Marine Agent (app/agents/marine_agent.py) ──────► PFZ Candidates, SST, Chlorophyll
         ├──► [4] Weather/Hazard Agent (app/agents/weather_hazard_agent.py) ──► Wind, Waves, Lightning/Cyclone Alerts
         └──► [5] GIS Agent (app/agents/gis_agent.py) ────────────► Geocoding, Haversine Distance, Route, Geofencing
         │
         ▼
[6] Risk Engine (app/agents/risk_engine.py) ────► Deterministic Multi-Factor Risk Score (0-100) & Hard Blocks
         │
         ▼
[7] Decision Agent (app/agents/decision_agent.py) ─► Ranking, Evidence Trail & Multilingual Explanation
         │
         ▼
FastAPI Orchestrator (app/main.py) ──────────────► JSON Output & Map Payload for Frontend
```

---

## 📁 Codebase Directory Structure

```
26176/
├── app/
│   ├── main.py                     # FastAPI server & route definitions
│   ├── config.py                   # Configuration, env settings & risk weights
│   ├── orchestrator.py             # Master pipeline sequencing logic
│   ├── schemas/                    # Pydantic v2 data models
│   │   ├── common.py               # LatLon, TimeWindow, Evidence, MapPayload
│   │   ├── nlu.py                  # NLUInput, NLUOutput, EntityBundle
│   │   ├── planner.py              # PlanInput, PlanOutput, ExecutionTraceStep
│   │   ├── marine.py               # PFZCandidate, OceanConditions, ProductivityTrend
│   │   ├── weather.py              # WeatherReading, MarineConditions, HazardAlert
│   │   ├── gis.py                  # Route, GeofenceResult, GeofenceIntersection
│   │   ├── risk.py                 # RiskInput, RiskResult, ComponentRiskBreakdown
│   │   └── decision.py             # CandidatePackage, FinalDecisionOutput
│   ├── agents/                     # Modular Agent Implementations (separate files)
│   │   ├── llm_client.py           # Gemini / OpenAI / Mock LLM wrapper
│   │   ├── nlu_agent.py            # Stage 1: NLU & Language Agent
│   │   ├── planner_agent.py        # Stage 2: Autonomous Planner Agent
│   │   ├── marine_agent.py         # Stage 3: Marine & PFZ Specialist Agent
│   │   ├── weather_hazard_agent.py # Stage 4: Weather & Hazard Specialist Agent
│   │   ├── gis_agent.py            # Stage 5: GIS & Geospatial Agent
│   │   ├── risk_engine.py          # Stage 6: Deterministic Risk Engine (No LLM)
│   │   └── decision_agent.py       # Stage 7: Decision & Explanation Agent
│   └── datasources/                # Data Sourcing Layer (DEMO vs LIVE)
│       ├── base.py                 # Abstract datasource interfaces
│       ├── demo_datasources.py     # JSON file-backed offline demo implementations
│       └── live_datasources.py     # Open-Meteo & OpenStreetMap Nominatim live connectors
├── data/demo/                      # Curated offline demo datasets
│   ├── gazetteer.json               # Coastal town lat/lon lookup
│   ├── pfz.json                     # Candidate PFZ advisories
│   ├── ocean_conditions.json       # SST, Chlorophyll, tide timings
│   ├── weather.json                # Wind speed, direction, wave height
│   ├── hazards.json                # Lightning and cyclone warnings
│   └── geofences.json              # GeoJSON polygons for MPAs & restricted zones
├── tests/                          # Pytest test suite
│   ├── test_nlu_agent.py           # Intent & language detection unit tests
│   ├── test_marine_agent.py        # PFZ retrieval & sorting tests
│   ├── test_weather_hazard_agent.py# Weather & hazard alert tests
│   ├── test_gis_agent.py           # Geocoding & geofence polygon intersection tests
│   ├── test_risk_engine.py         # Comprehensive risk score tests
│   ├── test_decision_agent.py      # Candidate ranking & hard_block tests
│   └── test_orchestrator_e2e.py    # End-to-End Killer Demo Query tests
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable configuration template
└── README.md                       # Documentation & setup guide
```

---

## ⚡ Quick Start Guide

### 1. Install Dependencies
Make sure Python 3.11+ is installed on your system. Run:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default configuration runs in **DEMO mode** (`ORCA_MODE=demo`) with mock/fallback LLM reasoning, allowing the entire backend to run 100% offline without external API keys.

To enable live LLM reasoning via **Google Gemini**:
```env
ORCA_MODE=demo
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run FastAPI Server
Start the local server with hot reloading:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive Swagger API documentation will be available at: **http://localhost:8000/docs**

---

## 🔌 Public API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/query` | **Master Conversational Entry Point**. Takes `{session_id, text}` and returns recommendation, evidence, explanation prose, execution trace, and map payload. |
| `GET` | `/api/pfz` | Direct PFZ candidate lookup tool (`?lat=16.99&lon=73.31&date=2026-09-09`). |
| `GET` | `/api/weather` | Direct Weather & Sea State lookup tool (`?lat=16.99&lon=73.31`). |
| `GET` | `/api/hazards` | Direct Hazard alerts lookup tool (`?lat=16.99&lon=73.31`). |
| `POST` | `/api/route` | Route distance, coastal waypoints, and Geofence check. |
| `POST` | `/api/risk` | Pure deterministic Risk Engine evaluation endpoint. |
| `GET` | `/api/health` | Service health status and current operational mode (`demo` / `live`). |

---

## 🛠️ How to Add Live External APIs Later

The codebase uses an abstract **`DataSource` interface pattern** (`app/datasources/base.py`). When your team is ready to add real INCOIS, IMD, PostGIS, or custom weather API keys:

1. Open `app/datasources/live_datasources.py`.
2. Implement your live HTTP requests or PostGIS database queries inside the corresponding method:
   - PFZ data: `LivePFZDataSource.get_pfz_candidates()`
   - Weather/Marine: `LiveWeatherDataSource.get_weather()`
   - Geofencing: `LiveGISDataSource.get_geofences()` (or query PostGIS via `ST_Intersects`)
3. Set `ORCA_MODE=live` in your `.env` file!

---

## 🧪 Running Automated Tests

Run the full pytest suite:
```bash
pytest -v
```

Run the End-to-End Killer Demo Query test specifically:
```bash
pytest tests/test_orchestrator_e2e.py -v
```
