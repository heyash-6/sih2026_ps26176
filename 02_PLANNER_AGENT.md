# Agent Spec: Planner Agent

## Purpose
This is the core "agentic" component the judges will look for. It takes the structured intent+entities from the NLU Agent and decomposes it into a concrete task list — deciding **which specialist agents/tools to call, with what parameters, in what order** — then executes that plan and collects results. This is autonomous planning + tool selection + task execution, per the PS wording.

## Responsibilities
- Given `{intent, entities}`, decide which of the following tool calls are required:
  - `get_pfz_candidates(lat, lon, date)` → Marine/PFZ Agent
  - `get_weather(lat, lon, datetime)` → Weather/Hazard Agent
  - `get_hazards(lat, lon, datetime)` → Weather/Hazard Agent
  - `get_route(origin, destination)` → GIS Agent
  - `check_geofence(route_or_point)` → GIS Agent
  - `compute_risk(candidate_bundle)` → Risk Engine
- Resolve any unresolved `location_text` to lat/lon by calling the GIS Agent's geocode tool BEFORE dispatching other calls that need coordinates.
- Call independent tools concurrently where possible (e.g. weather + hazards for the same candidate can run in parallel); call dependent tools sequentially (e.g. risk computation needs PFZ + weather + hazard + route results first).
- Assemble all tool results into one `PlanExecutionResult` object and hand off to the Decision & Explanation Agent. The Planner itself does NOT write the final answer.
- Produce a **visible execution trace** (ordered list of steps taken with tool name + short status) — this is what powers the "🤖 Planning... ✓ PFZ Agent ✓ Weather Agent ..." demo UI the frontend team will render. Emit this as structured data, not text.

## Input schema
```json
{
  "session_id": "string",
  "intent": "fishing_trip_planning",
  "entities": {
    "location_text": "Ratnagiri",
    "location_latlon": null,
    "date": "2026-09-09",
    "time_window": {"start": "05:00", "end": "11:00"},
    "duration_hours": 6
  }
}
```

## Output schema
```json
{
  "session_id": "string",
  "plan": [
    {"step": 1, "tool": "geocode", "params": {"location_text": "Ratnagiri"}},
    {"step": 2, "tool": "get_pfz_candidates", "params": {"lat": 16.99, "lon": 73.30, "date": "2026-09-09"}},
    {"step": 3, "tool": "get_weather", "params": {"candidates": ["PFZ-01","PFZ-02","PFZ-03"], "datetime": "2026-09-09T05:00:00+05:30"}},
    {"step": 4, "tool": "get_hazards", "params": {"lat": 16.99, "lon": 73.30, "datetime": "2026-09-09T05:00:00+05:30"}},
    {"step": 5, "tool": "get_route", "params": {"origin": [16.99,73.30], "destinations": ["PFZ-01","PFZ-02","PFZ-03"]}},
    {"step": 6, "tool": "check_geofence", "params": {"routes": ["route_1","route_2","route_3"]}},
    {"step": 7, "tool": "compute_risk", "params": {"candidates": "..."}}
  ],
  "execution_trace": [
    {"step": 1, "tool": "geocode", "status": "done", "duration_ms": 120},
    {"step": 2, "tool": "get_pfz_candidates", "status": "done", "duration_ms": 340}
  ],
  "results": {
    "pfz_candidates": [ "...see 03_MARINE_PFZ_AGENT.md output schema..." ],
    "weather_by_candidate": { "PFZ-01": "...", "PFZ-02": "..." },
    "hazards": [ "..." ],
    "routes_by_candidate": { "PFZ-01": "...", "PFZ-02": "..." },
    "geofence_by_candidate": { "PFZ-01": "clear", "PFZ-02": "intersects_restricted" }
  },
  "errors": []
}
```

## Behavior rules
- If `needs_clarification` was true upstream, the Planner should not run — the orchestrator returns the clarification question directly instead of invoking the Planner. Document this as a short-circuit at the orchestrator level (see file 08).
- If a specialist tool call fails or times out, record it in `errors` with the tool name and continue with the remaining candidates rather than failing the whole request — degrade gracefully (e.g. "hazard data unavailable" is shown in evidence rather than crashing).
- Cap candidate fan-out (e.g. max 5 PFZ candidates evaluated in parallel) to keep latency predictable for a live demo.
- The Planner LLM should be given the tool list as actual function/tool definitions (JSON schema per tool) via the LLM API's native tool-calling, not as a text description it has to parse. This is what makes "tool selection" real rather than simulated.

## Implementation notes for Antigravity
- Implement as a thin LLM-driven controller: system prompt describes available tools (from files 03–06) as callable functions; the LLM proposes a plan (or directly emits tool calls via tool-use); your orchestrator code executes the actual Python functions and feeds results back to the LLM only if it needs to decide on further calls (e.g. "do we need geofence check for this route based on region flags").
- For time-boxed hackathon reliability, a **hybrid** approach is acceptable and recommended: hard-code the "known" plan templates per intent (e.g. `fishing_trip_planning` always needs pfz+weather+hazard+route+geofence+risk) and use the LLM only to fill in parameters and to decide edge cases (e.g. skip PFZ lookup for a pure `condition_lookup` intent). Pure LLM-decides-everything is more impressive but higher risk for a 3-day build — document in your report that this is a deliberate engineering trade-off, which is itself a good talking point for judges.
- Log every plan + trace to make the "agent collaboration" visible in the demo and in an evidence/debug endpoint.

## Test cases
- `safety_check` intent → plan must include weather + hazard + (optionally route if underway) but NOT necessarily full PFZ ranking.
- `pfz_lookup` intent → plan must include geocode (if needed) + get_pfz_candidates + weather (for filtering unsafe zones) but can skip full route/geofence if user only asked "where," not "how do I get there."
- `fishing_trip_planning` intent → full plan (all 6 steps above).
- Simulate one tool failure (e.g. hazard API times out) and assert the Planner still returns partial results with the failure recorded, not an exception.
