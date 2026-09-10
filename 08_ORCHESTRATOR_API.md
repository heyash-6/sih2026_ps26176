# Spec: Orchestrator & API Layer

## Purpose
Wires all agents into one pipeline and exposes it as HTTP endpoints for the frontend/nav team. This is the "glue" file — it contains no AI logic of its own, just sequencing, error handling, and the public contract.

## Pipeline (implements `00_ORCA_ARCHITECTURE_OVERVIEW.md` §3)
```
POST /api/query
  1. Run NLU Agent on (text, prior_context)
  2. If needs_clarification -> return clarification question immediately (short-circuit, no Planner call)
  3. Run Planner Agent -> dispatches to Marine/Weather/GIS agents (parallel where possible)
  4. Run Risk Engine per candidate
  5. Run Decision & Explanation Agent
  6. Return combined payload (below) + persist session context for next turn
     (persistence itself is DB team's responsibility — this layer just calls
     their `save_session_context(session_id, context)` function/endpoint)
```

## Public endpoints

### `POST /api/query` — primary conversational entry point
Request:
```json
{
  "session_id": "sess_123",
  "text": "I'm at Ratnagiri. I want to leave at 5 AM tomorrow, fish for 6 hours...",
  "request_timestamp": "2026-09-08T10:00:00+05:30"
}
```
Response (success):
```json
{
  "session_id": "sess_123",
  "language": "en",
  "needs_clarification": false,
  "execution_trace": [ "...from Planner..." ],
  "recommendation": { "...from Decision Agent..." },
  "evidence": [ "..." ],
  "explanation_text": "...",
  "map_payload": {
    "candidates": [
      {"zone_id":"PFZ-02","lat":16.98,"lon":73.31,"risk_band":"MODERATE","status":"RECOMMENDED"},
      {"zone_id":"PFZ-01","lat":16.99,"lon":73.29,"risk_band":"HIGH","status":"REJECTED"}
    ],
    "routes": [ "...GIS Route objects..." ],
    "geofence_zones_checked": [ "..." ],
    "hazards": [ "...HazardAlert objects with lat/lon if applicable..." ]
  },
  "disclaimer": "..."
}
```
Response (needs clarification):
```json
{
  "session_id": "sess_123",
  "language": "en",
  "needs_clarification": true,
  "clarification_question": "Which location are you asking about?"
}
```

### Direct/debug endpoints (useful for frontend dev against mocks, and for your own testing)
- `GET /api/pfz?lat=&lon=&date=` → Marine Agent output directly
- `GET /api/weather?lat=&lon=&datetime=`
- `GET /api/hazards?lat=&lon=&datetime=`
- `POST /api/route` `{origin, destination}` → Route + GeofenceResult
- `POST /api/risk` `{RiskInput}` → RiskResult
- `GET /api/evidence/{session_id}` → last full evidence bundle for a session (for an "explain again" UI affordance)
- `GET /api/health` → `{status: "ok", mode: "demo|live"}`

## Error handling contract
- Any specialist agent failure → captured, does not 500 the whole request; reflected in `execution_trace` with `status: "failed"` and in `map_payload`/`evidence` as a gap, not silently dropped.
- LLM call failure (NLU or Decision agent) → one retry, then a graceful fallback response: `{"error": "temporarily_unavailable", "retry_suggested": true}` with HTTP 503 — never let the frontend hang indefinitely.
- All responses are JSON; no server-rendered HTML from this layer.

## Config / environment
```
ORCA_MODE=demo            # demo | live
LLM_PROVIDER=anthropic    # anthropic | gemini
LLM_API_KEY=...
ORCA_MAX_CANDIDATES=5
ORCA_DEFAULT_VESSEL_SPEED_KMH=15
```

## Implementation notes for Antigravity
- FastAPI app; each agent module imported and called from `orchestrator.py`; keep `main.py` thin (route registration + request validation only).
- Use `asyncio.gather` for the independent specialist calls (weather + hazards + route can run concurrently once candidates/coordinates are known).
- Add CORS config for the frontend dev server.
- Ship a `tests/test_orchestrator_e2e.py` that runs the full "killer demo query" end-to-end in DEMO mode and asserts a non-error, well-formed response — this is your safety net for the final 12 hours mentioned in the hackathon plan.

## Hand-off checklist for teammates
Give the frontend team: the `POST /api/query` response schema above, plus a running DEMO-mode server they can point at from day 1.
Give the DB team: the exact shape you need from `save_session_context` / `get_session_context`, and the exact GeoJSON shape you expect for geofence polygons (see `05_GIS_AGENT.md`).
