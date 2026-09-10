# Agent Spec: Decision & Explanation Agent

## Purpose
The final stage. Takes the assembled results from Planner + all specialist agents + Risk Engine and produces (a) a ranked recommendation and (b) a natural-language, evidence-cited explanation in the user's detected language. This is the ONLY agent besides the Planner and NLU agent that should call an LLM — and even here, the LLM explains and phrases; it never computes numbers itself.

## Responsibilities
- Rank candidates (e.g. PFZ options) using: `hard_block` first (exclude/flag), then ascending `total_risk`, then ascending `distance_km` as tiebreaker.
- Select a top recommendation (or explicitly state "no safe option found" if all candidates are HIGH/VERY HIGH or hard-blocked).
- Generate a structured **evidence list** — the raw facts that justify the recommendation, each tagged with its source agent/dataset.
- Generate the final **explanation text**, in the language detected by the NLU agent, in a plain, non-alarmist, practical tone appropriate for a fisherman making a real safety decision.
- Always append a **disclaimer** pointing to official advisories (do not let the LLM omit this — enforce it in the prompt template and/or append it in code regardless of LLM output).

## Input schema
```json
{
  "session_id": "string",
  "language": "mr",
  "intent": "fishing_trip_planning",
  "candidates": [
    {
      "zone_id": "PFZ-02",
      "distance_km": 18.4,
      "weather": { "...WeatherReading..." },
      "marine_conditions": { "...MarineConditions..." },
      "hazards": [ "...HazardAlert..." ],
      "route": { "...Route..." },
      "geofence": { "...GeofenceResult..." },
      "risk": { "...RiskResult..." }
    }
  ]
}
```

## Output schema
```json
{
  "session_id": "string",
  "recommendation": {
    "zone_id": "PFZ-02",
    "status": "RECOMMENDED",
    "risk_band": "MODERATE",
    "risk_score": 34.6
  },
  "alternatives_considered": [
    {"zone_id": "PFZ-01", "status": "REJECTED", "reason_code": "geofence_intersect"},
    {"zone_id": "PFZ-04", "status": "REJECTED", "reason_code": "high_wave"}
  ],
  "evidence": [
    {"claim": "18.4 km from your location", "source": "GIS Agent — distance_km"},
    {"claim": "Moderate wave conditions (0.8 m)", "source": "Weather/Hazard Agent — marine_conditions"},
    {"claim": "No active lightning alert at this zone", "source": "Weather/Hazard Agent — hazards"},
    {"claim": "Route does not intersect any restricted zone", "source": "GIS Agent — geofence"}
  ],
  "explanation_text": "PFZ-02 उद्या सकाळसाठी सर्वोत्तम पर्याय आहे कारण... (in Marathi)",
  "disclaimer": "This is a prototype decision-support assessment. Always verify current official marine advisories (IMD/INCOIS/Coast Guard) before departure.",
  "generated_at": "2026-09-08T10:03:00+05:30"
}
```

## Behavior rules
- The LLM prompt must include the full structured `candidates` data as context and an explicit instruction: *"Do not invent, alter, or round any numeric value beyond what is given. Cite each claim in `evidence` back to its source field. Write `explanation_text` in {language}."*
- If `hard_block` is true for the top-ranked-by-score candidate, it must be excluded from `recommendation` and listed under `alternatives_considered` with `status: "REJECTED"` — never recommend a hard-blocked zone even if its numeric score looks otherwise low.
- If no candidate is safe, `recommendation.status` should be `"NO_SAFE_OPTION"` and `explanation_text` should say so plainly and suggest checking again later / consulting official advisories — never force a recommendation to avoid an awkward answer.
- Keep `explanation_text` concise (roughly 3–6 sentences) — this is read aloud/glanced at by someone making a real decision, not a report.
- Always run the disclaimer append as a **code-level guarantee** (concatenate it after the LLM call), not solely trust the LLM to include it.

## Implementation notes for Antigravity
- Single LLM call per request. Use a strict system prompt with the schema above as the target output shape; validate with Pydantic; retry once on validation failure.
- For the `productivity_explanation` intent, this agent also converts the Marine Agent's `ProductivityTrend` object into prose — again, explaining given deltas, not inventing new causal claims.
- Reuse the same agent/prompt for all intents; branch only on which fields are populated in `candidates` (e.g. `safety_check` may have a single "location" pseudo-candidate rather than multiple PFZs).

## Test cases
- Candidate set where the lowest-score option is hard-blocked → recommendation must skip it and pick the next viable one, with the blocked one shown as REJECTED with `reason_code`.
- All candidates HIGH/VERY HIGH → `status: "NO_SAFE_OPTION"`, no recommendation forced.
- Language field `hi` → `explanation_text` is grammatically valid Hindi (spot-check manually; don't over-engineer automated language-quality testing for a 3-day build).
- Every entry in `evidence` traces back to a field that actually exists in the input `candidates` object (write an assertion that greps the source field names).
