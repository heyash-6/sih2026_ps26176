# 🌊 ORCA — Marine EcOsystem Reasoning with Collaborative Agents
### **Smart India Hackathon 2026 — Problem Statement PS26176**
**Agentic AI-Powered Conversational Marine Decision Support & Navigation Platform**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Leaflet](https://img.shields.io/badge/Leaflet-19.4-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database%20%26%20Auth-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![INCOIS](https://img.shields.io/badge/INCOIS-Ocean%20Data-0077BE?style=for-the-badge)](https://incois.gov.in/)
[![Multilingual](https://img.shields.io/badge/Languages-English%20%7C%20%E0%A4%B9%E0%A4%BF%E0%A4%A8%E0%A5%8D%E0%A4%A6%E0%A5%80%20%7C%20%E0%A4%AE%E0%A4%B0%E0%A4%BE%E0%A4%A0%E0%A5%80-orange?style=for-the-badge)](#-tri-lingual-support)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/heyash-6/sih2026_ps26176)

---

## 📌 Executive Summary

**ORCA** (*Marine EcOsystem Reasoning with Collaborative Agents*) is an end-to-end, multi-agent AI decision platform engineered to transform Indian marine fisheries and coastal navigation. Addressing **SIH 2026 Problem Statement PS26176**, ORCA bridges complex oceanographic models (INCOIS, IMD, Copernicus, Open-Meteo) with coastal fishermen, vessel operators, and maritime agencies.

Fishermen can interact using **natural language in English, Hindi (हिन्दी), or Marathi (मराठी)** via voice or text. ORCA autonomously plans tasks, fetches live oceanographic satellite data (SST, Chlorophyll-a), models real-time marine weather (wave height, wind gust, swell), generates safety-checked **A\* obstacle-free marine routes**, calculates deterministic multi-factor risk scores (0–100), and delivers evidence-backed fishing recommendations alongside an interactive GIS workstation.

---

## 🏛️ System Architecture

ORCA enforces a strict separation of concerns: **Autonomous LLM Agents decide *what* to query and *how* to explain, while deterministic engines compute all numeric facts, distances, routes, and risk scores.**

```
                               ┌──────────────────────────────────────────────┐
                               │   Fisherman / Operator Natural Query         │
                               │   (English, हिन्दी, मराठी — Text / Voice)    │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                                       ┌──────────────────────────────┐
                                       │    [Stage 1] NLU Agent       │
                                       │  Language & Intent Detection │
                                       │  Coastal Gazetteer Entity Ext│
                                       └──────────────┬───────────────┘
                                                      │
                                                      ▼
                                       ┌──────────────────────────────┐
                                       │  [Stage 2] Planner Agent     │
                                       │ Dynamic Task Decomposition   │
                                       │   Autonomous Tool Dispatch   │
                                       └──────────────┬───────────────┘
                                                      │
                        ┌─────────────────────────────┼─────────────────────────────┐
                        ▼                             ▼                             ▼
       ┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌──────────────────────────────┐
       │   [Stage 3] Marine Agent     │ │ [Stage 4] Weather & Hazard   │ │     [Stage 5] GIS Agent      │
       │ • INCOIS THREDDS OpenDAP     │ │ • Wind Speed, Gust, Direction│ │ • Safe A* Marine Routing     │
       │ • Satellite SST (°C)         │ │ • Significant Wave Height (m)│ │ • MPA / Coastal Geofencing   │
       │ • Chlorophyll-a (mg/m³)      │ │ • Cyclone & Lightning Alerts │ │ • Haversine Distance & ETAs  │
       │ • Potential Fishing Zones    │ │ • Tide Timings & Swell       │ │ • Waypoint Route Generation  │
       └──────────────┬───────────────┘ └──────────────┬───────────────┘ └──────────────┬───────────────┘
                        │                             │                             │
                        └─────────────────────────────┼─────────────────────────────┘
                                                      │
                                                      ▼
                                       ┌──────────────────────────────┐
                                       │   [Stage 6] Risk Engine      │
                                       │ Deterministic Scoring (0-100)│
                                       │ Hard Safety Blocks & Flags   │
                                       └──────────────┬───────────────┘
                                                      │
                                                      ▼
                                       ┌──────────────────────────────┐
                                       │  [Stage 7] Decision Agent    │
                                       │ Multi-Criteria Candidate Rank│
                                       │ Multilingual Explainability  │
                                       │ Evidence Trail Compilation   │
                                       └──────────────┬───────────────┘
                                                      │
                                                      ▼
                                       ┌──────────────────────────────┐
                                       │ FastAPI Master Orchestrator  │
                                       │ JSON Response + Map Payload  │
                                       └──────────────┬───────────────┘
                                                      │
                        ┌─────────────────────────────┴─────────────────────────────┐
                        ▼                                                           ▼
       ┌──────────────────────────────┐                            ┌──────────────────────────────┐
       │   React 19 GIS Workstation   │                            │  Supabase Real-Time Engine   │
       │ • Interactive Leaflet Maps   │                            │ • PostgreSQL + PostGIS       │
       │ • Route Waypoint Assessment  │                            │ • Secure User Authentication │
       │ • Ocean Timeseries Analytics │                            │ • Port Hub Contexts & RLS    │
       │ • Conversational AI Copilot  │                            │ • Chat Session Persistence   │
       └──────────────────────────────┘                            └──────────────────────────────┘
```

---

## 🤖 The 7 Autonomous AI Agents & Engines

| # | Agent / Module | Implementation | Core Responsibilities & Deterministic Safeguards |
|---|---|---|---|
| **1** | **NLU & Language Agent** | [`app/agents/nlu_agent.py`](file:///app/agents/nlu_agent.py) | Detects query language (`en`, `hi`, `mr`), classifies user intent (`pfz_search`, `weather_check`, `route_plan`, `hazard_inquiry`), extracts coastal ports, vessel specs, and temporal bounds. Handles colloquialisms and gibberish detection. |
| **2** | **Autonomous Planner Agent** | [`app/agents/planner_agent.py`](file:///app/agents/planner_agent.py) | Dynamically synthesizes execution graphs based on missing entities, determines which domain tools to call, and handles fallback routing if external services are unreachable. |
| **3** | **Marine & PFZ Agent** | [`app/agents/marine_agent.py`](file:///app/agents/marine_agent.py) | Queries live INCOIS satellite advisories and ocean color monitors. Computes ocean productivity indices from Sea Surface Temperature (SST) gradients and Chlorophyll-a concentrations. |
| **4** | **Weather & Hazard Agent** | [`app/agents/weather_hazard_agent.py`](file:///app/agents/weather_hazard_agent.py) | Slices multi-layer marine atmospheric data. Tracks wind gust thresholds, wave period, swell, convective lightning, and IMD cyclone trajectory advisories. |
| **5** | **GIS & Navigation Agent** | [`app/agents/gis_agent.py`](file:///app/agents/gis_agent.py)<br>[`app/gis/navigator.py`](file:///app/gis/navigator.py) | Runs **A\* safe sea-lane pathfinding** avoiding landmasses, shallow bathymetry, and Marine Protected Areas (MPAs). Computes coastal waypoints with 1-to-1 data parity for navigation logs. |
| **6** | **Deterministic Risk Engine** | [`app/agents/risk_engine.py`](file:///app/agents/risk_engine.py) | **Zero-hallucination mathematical engine (No LLM).** Computes weighted composite risk score ($0-100$) across 5 dimensions: wave risk, wind risk, lightning risk, distance risk, and cyclone risk. Enforces hard safety blocks (`is_safe = False`) if waves exceed $3.5\text{ m}$, winds exceed $45\text{ km/h}$, or an MPA zone is violated. |
| **7** | **Decision & Explanation Agent** | [`app/agents/decision_agent.py`](file:///app/agents/decision_agent.py) | Ranks PFZ candidates via multi-attribute utility theory, constructs transparent evidence citation trails, and crafts personalized vernacular advisory messages in English, Hindi, or Marathi. |

---

## ✨ Key Platform Features

### 1. 🧭 Safe A* Marine Navigation & Route Assessment
- **Landmass & Obstacle Avoidance:** Prevents routes from clipping shorelines or islands using high-resolution coastal boundary polygons.
- **Marine Protected Area (MPA) Geofencing:** Auto-reroutes around restricted marine sanctuaries and ecological conservation corridors.
- **Waypoint Navigation Log:** Live 1-to-1 data parity between Route Assessment Points on the Leaflet map and the tabular navigation log (distance, coordinates, weather, ETA, risk score).

### 2. 🌊 Live Ocean Analytics & Timeseries
- Real historical and forecast timeseries for **SST (°C)**, **Chlorophyll-a (mg/m³)**, **Significant Wave Height (m)**, and **Productivity Index**.
- Toggle between **24-Hour** and **7-Day** views across 20 coastal port hubs along the Indian coastline.
- Real astronomical tide schedules (High Tide / Low Tide timings and heights).

### 3. 🗓️ Multi-Day Trip Planner
- Calculates expedition feasibility, optimal departure time windows, estimated fuel burn, and voyage duration.
- Identifies the highest-yield fishing zones within safe nautical operating ranges.

### 4. 🗣️ Tri-Lingual Conversational Copilot
- 100% full localization across UI, tooltips, warnings, recommendations, and chatbot responses in:
  - **English**
  - **हिन्दी (Hindi)**
  - **मराठी (Marathi)**
- Persistent multi-turn conversation memory with Supabase session storage.
- Interactive map recentering and visual sync when the user inquires about specific ports or zones.

### 5. 🔐 Enterprise Authentication & Audit Trail
- Supabase Auth integration with pre-configured email verification.
- Complete relational PostgreSQL schema with Row-Level Security (RLS) policies and audit logging.

---

## 📁 Repository Directory Structure

```
.
├── app/                                 # FastAPI Backend & Multi-Agent AI Core
│   ├── main.py                          # Master FastAPI server & API router
│   ├── orchestrator.py                  # End-to-end 7-agent execution pipeline
│   ├── config.py                        # App configuration, weights, and environment
│   ├── agents/                          # Modular AI Agent Implementations
│   │   ├── nlu_agent.py                 # [Stage 1] Language & Intent Parser
│   │   ├── planner_agent.py             # [Stage 2] Dynamic Task Planner
│   │   ├── marine_agent.py              # [Stage 3] Marine & PFZ Specialist
│   │   ├── weather_hazard_agent.py      # [Stage 4] Weather & Marine Hazard Specialist
│   │   ├── gis_agent.py                 # [Stage 5] Geospatial & Geocoding Agent
│   │   ├── risk_engine.py               # [Stage 6] Deterministic Mathematical Risk Engine
│   │   ├── decision_agent.py            # [Stage 7] Ranking & Multilingual Explainer
│   │   └── llm_client.py                # Google Gemini / OpenAI / Fallback LLM client
│   ├── gis/                             # Geospatial & Pathfinding Engine
│   │   └── navigator.py                 # A* sea-route pathfinding & coastal grid
│   ├── database/                        # Database connectivity & data pipeline
│   │   └── data_pipeline.py             # Realtime ingestion from INCOIS & Open-Meteo
│   ├── datasources/                     # Data Sourcing Layer (Demo vs Live)
│   │   ├── base.py                      # Abstract data source interfaces
│   │   ├── demo_datasources.py          # High-fidelity offline demo datasets
│   │   └── live_datasources.py          # INCOIS, Open-Meteo & Nominatim live APIs
│   └── schemas/                         # Pydantic v2 Strong Data Contracts
│       ├── common.py                    # Coordinates, LatLon, Evidence, MapPayload
│       ├── nlu.py                       # Intent and Entity bundles
│       ├── planner.py                   # Dynamic Plan and Trace schemas
│       ├── marine.py                    # PFZ Candidate and Oceanographic schemas
│       ├── weather.py                   # Marine Weather and Hazard schemas
│       ├── gis.py                       # Route, Waypoint, and Geofence schemas
│       ├── risk.py                      # Risk breakdown and score models
│       └── decision.py                  # Final decision package schema
├── frontend/                            # React 19 + Vite Full-Stack Marine Workstation
│   ├── src/
│   │   ├── App.jsx                      # Main UI Controller, Tabs, Leaflet GIS & Copilot
│   │   ├── App.css                      # Modern dark/light glassmorphic styling
│   │   ├── index.css                    # Typography & Tailwind-inspired tokens
│   │   ├── main.jsx                     # React DOM entrypoint
│   │   ├── data.js                      # Port hubs, geofences, and fallback dataset
│   │   ├── components/                  # UI Modular Widgets
│   │   └── services/                    # Supabase client & API services
│   ├── package.json                     # Frontend dependencies (React 19, Leaflet, Supabase)
│   └── vite.config.js                   # Vite bundler configuration
├── data/demo/                           # Curated Offshore & Inshore Marine Datasets
│   ├── gazetteer.json                   # 20+ Indian coastal ports (Mumbai, Ratnagiri, Goa, etc.)
│   ├── pfz.json                         # Validated Potential Fishing Zones
│   ├── ocean_conditions.json            # Historical & forecast SST / Chlorophyll
│   ├── weather.json                     # Wind speed, direction, wave height
│   ├── hazards.json                     # IMD cyclone tracks & lightning strikes
│   └── geofences.json                   # Marine Protected Areas & maritime borders
├── tests/                               # Comprehensive Automated Test Suite
│   ├── test_nlu_agent.py                # Intent & multilingual parsing tests
│   ├── test_marine_agent.py             # PFZ retrieval & sorting tests
│   ├── test_weather_hazard_agent.py     # Atmospheric hazard threshold tests
│   ├── test_gis_agent.py                # A* pathfinding & geofence collision tests
│   ├── test_risk_engine.py              # Deterministic risk math & hard-block tests
│   ├── test_decision_agent.py           # Ranking & explanation generation tests
│   ├── test_orchestrator_e2e.py         # End-to-end full pipeline integration tests
│   └── test_prompt6_verification.py     # Prompt #6 edge case validation test
├── 00_ORCA_ARCHITECTURE_OVERVIEW.md     # Detailed architecture specification
├── 01_NLU_LANGUAGE_AGENT.md             # NLU agent design spec
├── 02_PLANNER_AGENT.md                  # Autonomous planner design spec
├── 03_MARINE_PFZ_AGENT.md               # Marine & PFZ agent design spec
├── 04_WEATHER_HAZARD_AGENT.md           # Weather hazard agent design spec
├── 05_GIS_AGENT.md                      # GIS agent design spec
├── 06_RISK_ENGINE.md                    # Deterministic risk engine design spec
├── 07_DECISION_EXPLANATION_AGENT.md     # Decision agent design spec
├── 08_ORCHESTRATOR_API.md               # API & orchestrator design spec
├── DATABASE_AUTH_GUIDE.md               # Supabase database & authentication guide
├── ORCA_AI_AGENTS_SIH_REPORT.html       # Comprehensive SIH agent technical report
├── ORCA_FULL_SYSTEM_WORKFLOW_REPORT.html# SIH system workflow & verification report
├── supabase_schema.sql                  # Idempotent PostgreSQL DDL with RLS
├── supabase_seed.sql                    # Initial seed data for ports & zones
├── docker-compose.yml                   # Containerized multi-service deployment
├── start_orca.bat                       # One-click Windows startup script
├── build_frontend.ps1                   # Frontend build script
└── requirements.txt                     # Backend Python dependencies
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11+** installed
- **Node.js 18+ & npm** installed
- Modern web browser (Chrome, Edge, Firefox)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/heyash-6/sih2026_ps26176.git
cd sih2026_ps26176
```

---

### Step 2: Set Up Backend Environment
```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default settings run in **DEMO mode** (`ORCA_MODE=demo`), allowing the platform to run 100% offline with zero external API dependencies.

To enable live Gemini AI reasoning and live data feeds:
```env
ORCA_MODE=demo                      # or 'live'
LLM_PROVIDER=gemini                 # 'gemini', 'openai', or 'mock'
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://byikekhtwiewlpxbuwgo.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

---

### Step 4: Build Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

---

### Step 5: Run the Platform

#### Option A: One-Click Startup (Windows)
Double-click [`start_orca.bat`](file:///start_orca.bat) or run in terminal:
```cmd
start_orca.bat
```
This automatically launches the server on `http://localhost:8000` and opens the application in your default browser.

#### Option B: Manual Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Web Dashboard:** [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/query` | **Master Conversational Entry Point**. Processes natural language queries, runs 7-agent pipeline, and returns recommendations, evidence, risk, and map payload. |
| `GET` | `/api/pfz` | Potential Fishing Zone candidate lookup (`?lat=16.99&lon=73.31&date=2026-09-09`). |
| `GET` | `/api/weather` | Sea surface temperature, wave height, and wind conditions lookup. |
| `GET` | `/api/hazards` | Active marine warnings, cyclone alerts, and convective lightning strikes. |
| `POST` | `/api/route` | Safe A\* sea-lane route generation avoiding landmasses and MPA geofences. |
| `POST` | `/api/risk` | Deterministic Risk Engine evaluation returning 0–100 composite risk score and component breakdown. |
| `GET` | `/api/health` | Health check endpoint returning system status and operational mode. |

---

## 🧪 Testing & Verification

Run the entire automated pytest test suite:
```bash
pytest -v
```

Run specific test modules:
```bash
# Test End-to-End Orchestrator Killer Demo Query
pytest tests/test_orchestrator_e2e.py -v

# Test Deterministic Risk Engine & Hard Safety Blocks
pytest tests/test_risk_engine.py -v

# Test Safe A* Marine Pathfinding & Geofencing
pytest tests/test_gis_agent.py -v

# Verify Prompt #6 edge cases, multilingual strictness, and ETA determinism
python test_prompt6_verification.py
```

---

## 🌊 Supported Indian Coastal Ports (Gazetteer)

ORCA includes built-in geospatial data, bathymetry, and tide tables for key ports across the Indian coastline:

| Port / Harbor | State | Latitude | Longitude |
|---|---|---|---|
| **Ratnagiri (Mirya Bay)** | Maharashtra | 16.99° N | 73.31° E |
| **Mumbai (Sassoon Dock)** | Maharashtra | 18.92° N | 72.83° E |
| **Malvan** | Maharashtra | 16.06° N | 73.46° E |
| **Panaji** | Goa | 15.49° N | 73.82° E |
| **Mangalore (New Port)** | Karnataka | 12.91° N | 74.82° E |
| **Kochi (Cochin Harbor)** | Kerala | 9.93° N | 76.26° E |
| **Veraval** | Gujarat | 20.90° N | 70.37° E |
| **Porbandar** | Gujarat | 21.64° N | 69.62° E |
| **Chennai Harbor** | Tamil Nadu | 13.08° N | 80.27° E |
| **Visakhapatnam** | Andhra Pradesh | 17.68° N | 83.21° E |
| **Paradip** | Odisha | 20.31° N | 86.61° E |

---

## 📜 Problem Statement Alignment (SIH 2026 - PS26176)

| PS26176 Key Requirement | ORCA Solution |
|---|---|
| **Multilingual Conversational Access** | Full NLU and speech/text translation in English, Hindi, and Marathi with vernacular coastal fishing jargon. |
| **Multi-Source Oceanographic Synthesis** | Real-time integration of INCOIS PFZ satellite advisories, SST gradients, Chlorophyll-a, and sea-state forecasts. |
| **Safety First & Risk Determinism** | Mathematical risk engine with zero hallucination. Hard blocks prevent voyages during cyclones, high waves ($>3.5\text{ m}$), or into protected sanctuaries. |
| **Obstacle-Free Marine Navigation** | A\* sea-lane routing strictly routed around landmasses, shallow shoals, and Marine Protected Areas (MPAs). |
| **Transparent Explainability** | Every recommendation provides an inspectable **Evidence Trail** detailing exact satellite timestamps, sensors, and risk weight contributions. |

---

## 👥 Hackathon Team & Acknowledgments

- **Team:** Smart India Hackathon (SIH) 2026 Finalists
- **Problem Statement:** PS26176 — Marine EcOsystem Reasoning with Collaborative Agents (ORCA)
- **Data Acknowledgments:** Indian National Centre for Ocean Information Services (INCOIS), India Meteorological Department (IMD), Open-Meteo, and OpenStreetMap.

