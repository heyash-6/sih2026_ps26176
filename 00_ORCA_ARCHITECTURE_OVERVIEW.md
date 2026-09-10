# ORCA — AI Agent Backend Architecture Overview
**PS 26176 — Marine EcOsystem Reasoning with Collaborative Agents**
**Scope of this document:** backend AI agents only. Frontend, database schema/ops, and navigation UI are owned by teammates and consumed as APIs/tables by this backend.

---

## 1. What this backend must do

Given a natural-language marine query (any supported language) plus optional structured context (lat/lon, vessel id, timestamps), return:
1. A structured, machine-usable **recommendation** (e.g. best PFZ, go/no-go, route status, risk score).
2. A human-readable **explanation** in the user's language.
3. The **evidence trail** (which data sources / agent calls produced the answer).
4. Enough structured data for the frontend team to render it on a map/chart without re-deriving anything.

This backend is the "brain." It does NOT own PostGIS, does NOT render maps, does NOT store conversation history permanently (that's the DB team's job) — but it DOES expose clean APIs that the frontend/DB layers call.

---

## 2. Agent list (5 logical agents + 1 orchestrator)

| # | Agent | Type | Spec file |
|---|-------|------|-----------|
| 1 | Language & Intent (NLU) Agent | LLM | `01_NLU_LANGUAGE_AGENT.md` |
| 2 | Planner Agent | LLM (tool-calling) | `02_PLANNER_AGENT.md` |
| 3 | Marine/PFZ Agent | Tool/function (LLM-optional) | `03_MARINE_PFZ_AGENT.md` |
| 4 | Weather & Hazard Agent | Tool/function | `04_WEATHER_HAZARD_AGENT.md` |
| 5 | GIS/Geospatial Agent | Tool/function | `05_GIS_AGENT.md` |
| 6 | Risk Engine | **Deterministic, NO LLM** | `06_RISK_ENGINE.md` |
| 7 | Decision & Explanation Agent | LLM | `07_DECISION_EXPLANATION_AGENT.md` |
| — | Orchestrator / API layer | Code (FastAPI) | `08_ORCHESTRATOR_API.md` |

Golden rule (keep this in every agent's system prompt):
> **The LLM decides WHAT to ask for and HOW to explain results. It never invents numbers. All numeric facts (distances, wave heights, risk scores) come from deterministic tools/functions.**

---

## 3. Data flow (single canonical pipeline)

```
User message (any language, may be voice-to-text later)
        │
        ▼
[1] NLU Agent  → {language, intent, entities: location, datetime, duration, vessel_id}
        │
        ▼
[2] Planner Agent → task list: which of {pfz, weather, hazard, gis/route, geofence} are needed
        │
        ├──► [3] Marine/PFZ Agent    → candidate PFZs with lat/lon, distance, source
        ├──► [4] Weather/Hazard Agent→ wind, wave, rain, lightning, cyclone per candidate/time
        ├──► [5] GIS Agent           → route(s), ETA, geofence intersection results
        │
        ▼
[6] Risk Engine (deterministic) → risk_score (0-100) + component breakdown, per candidate
        │
        ▼
[7] Decision & Explanation Agent → ranks candidates, picks recommendation, writes explanation
        │                           in user's language, cites evidence
        ▼
Orchestrator returns JSON: { recommendation, risk, evidence[], explanation_text, map_payload }
```

All inter-agent messages are **typed JSON**, not free text. Define them with Pydantic. This is what lets you swap "5 agents" for "5 Python functions called by one LLM with tools" without changing the contract — see §5.

---

## 4. Tech stack recommendation

- **Language:** Python 3.11+
- **API framework:** FastAPI
- **LLM calls:** Anthropic API (Claude) or Gemini API — pick ONE for consistency; use function/tool calling, not prompt-and-parse where avoidable
- **Schema/validation:** Pydantic v2 for every agent input/output
- **Orchestration:** Start with a hand-written planner loop (function-calling), not a heavy framework. Only reach for LangGraph/CrewAI if you have time to spare on day 3 — don't burn day 1 learning a framework.
- **Data access:** thin repository functions that call the DB team's tables/API (`get_pfz_candidates()`, `get_geofences()`, etc.) — treat DB as a black box behind an interface you define together on day 1.
- **Weather/ocean data:** wrap real APIs (IMD, INCOIS, Open-Meteo) behind a `DataSource` interface with a `LIVE` and `DEMO` implementation, selected by env var `ORCA_MODE=live|demo`.
- **Testing:** pytest, with fixed demo-mode fixtures so the whole pipeline is deterministic and demoable offline.

## 5. Important architectural decision: "5 agents" ≠ "5 separate LLMs"

Implement each specialist agent (Marine/PFZ, Weather/Hazard, GIS) as a **plain Python module exposing typed functions** (i.e. tools). Only the **Planner** and the **Decision & Explanation** agent need an actual LLM call. This:
- saves latency/cost/time
- is exactly what the PS means by "tool selection" — the Planner LLM calls tools, tools don't need to be LLMs themselves
- still lets you say "5 specialized agents" truthfully in your report, because each is a distinct module with its own responsibility, interface, and (for the demo trace) its own name/log line

## 6. Folder structure

```
orca-backend/
├── app/
│   ├── main.py                 # FastAPI app, mounts orchestrator routes
│   ├── schemas/                # Pydantic models shared across agents
│   │   ├── common.py           # LatLon, TimeWindow, Evidence, etc.
│   │   ├── nlu.py
│   │   ├── planner.py
│   │   ├── marine.py
│   │   ├── weather.py
│   │   ├── gis.py
│   │   ├── risk.py
│   │   └── decision.py
│   ├── agents/
│   │   ├── nlu_agent.py
│   │   ├── planner_agent.py
│   │   ├── marine_agent.py
│   │   ├── weather_hazard_agent.py
│   │   ├── gis_agent.py
│   │   ├── risk_engine.py
│   │   └── decision_agent.py
│   ├── datasources/
│   │   ├── base.py             # DataSource interface (LIVE/DEMO switch)
│   │   ├── pfz_demo.py / pfz_live.py
│   │   ├── weather_demo.py / weather_live.py
│   │   └── gis_demo.py / gis_live.py
│   ├── orchestrator.py         # runs the pipeline in §3
│   └── config.py
├── tests/
│   ├── fixtures/                # frozen demo-mode JSON snapshots
│   └── test_*.py
├── data/demo/                   # PFZ.json, hazards.json, geofences.json, weather.json
├── requirements.txt
└── .env.example
```

## 7. API contract exposed to the rest of the team (frontend/nav/DB)

The orchestrator (see `08_ORCHESTRATOR_API.md`) exposes:

- `POST /api/query` — the single entry point: `{ session_id, text, lang?, location? }` → full pipeline result
- `GET /api/pfz?lat=&lon=&date=` — direct PFZ lookup
- `GET /api/weather?lat=&lon=&datetime=`
- `GET /api/hazards?lat=&lon=&datetime=`
- `POST /api/route` — `{origin, destination}` → route + geofence check
- `POST /api/risk` — `{pfz_candidate}` → risk score breakdown
- `GET /api/evidence/{recommendation_id}`

Give this list to your frontend teammate on day 1 so they can build against mocks while you build the real thing.

## 8. What NOT to build (reiterated for the AI-agent scope specifically)
- No custom PFZ prediction model — consume/replicate published PFZ advisory format.
- No custom weather/cyclone forecasting — wrap existing sources (IMD/INCOIS/Open-Meteo) or a frozen demo dataset.
- No fine-tuning — prompt engineering + tool calling only.
- No LLM-computed risk scores — Risk Engine is pure arithmetic (see file 06).
