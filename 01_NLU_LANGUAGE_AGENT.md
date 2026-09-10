# Agent Spec: Language & Intent (NLU) Agent

## Purpose
First stage of the pipeline. Takes raw user text (any language) and turns it into a structured, typed object the Planner can act on. Also detects the language so the final response can be generated back in that language.

## Responsibilities
- Detect the language of the input (emphasis: English, Hindi, Marathi at minimum; architecture must allow adding more Indian languages later without redesign).
- Classify user **intent** into a fixed enum (extend as needed):
  - `fishing_trip_planning`
  - `pfz_lookup`
  - `safety_check` ("is it safe to go tomorrow")
  - `condition_lookup` (tide/weather/sea state near a location)
  - `hazard_alert_check` (lightning/cyclone)
  - `chlorophyll_sst_lookup`
  - `route_planning`
  - `productivity_explanation` ("why has fish productivity declined")
  - `geofence_check`
  - `followup` (refinement of a previous turn — see multi-turn handling below)
  - `other`
- Extract entities: `location` (free text + resolve to lat/lon if resolvable, else pass through for GIS agent to geocode), `date` (absolute or relative like "tomorrow"), `time`/`time_window`, `duration`, `vessel_id` (if mentioned).
- Normalize relative time expressions ("tomorrow morning", "in 6 hours") into ISO 8601 using the request timestamp as the reference point.
- Preserve conversation context: accept an optional `prior_context` object (last resolved entities) and merge/override with new entities found in this turn — this is how "What if I leave at 7 AM instead?" gets resolved without re-asking everything.

## Input schema
```json
{
  "session_id": "string",
  "text": "उद्या सकाळी समुद्रात जाणे सुरक्षित आहे का?",
  "request_timestamp": "2026-09-08T10:00:00+05:30",
  "prior_context": {
    "location": "Ratnagiri",
    "date": "2026-09-09",
    "intent": "safety_check"
  }
}
```

## Output schema
```json
{
  "language": "mr",
  "language_confidence": 0.97,
  "intent": "safety_check",
  "intent_confidence": 0.91,
  "entities": {
    "location_text": "समुद्र (near Ratnagiri, inferred from context)",
    "location_latlon": null,
    "date": "2026-09-09",
    "time_window": {"start": "05:00", "end": "10:00"},
    "duration_hours": null,
    "vessel_id": null
  },
  "missing_required_fields": [],
  "needs_clarification": false,
  "clarification_question": null
}
```

## Behavior rules
- If a required field for the detected intent is missing AND cannot be inferred from `prior_context`, set `needs_clarification: true` and produce ONE short clarification question **in the detected language**. Do not guess a location silently.
- Never hallucinate lat/lon — if the location can't be resolved to coordinates here, leave `location_latlon: null` and let the GIS agent geocode it.
- Always return `entities.date` as an absolute ISO date, resolved using `request_timestamp`, never "tomorrow" as a string.
- Confidence scores are required outputs (even if approximate) — used later for explanation transparency, not just decoration.

## Implementation notes for Antigravity
- Single LLM call with a strict JSON-only system prompt + the schema above as a target shape (use function/tool calling with a JSON schema if the chosen LLM API supports it, e.g. Anthropic tool-use or Gemini function calling — prefer this over "ask for JSON and hope").
- Validate the LLM output against the Pydantic model; on validation failure, retry once with the error appended to the prompt, then fail gracefully with `needs_clarification: true`.
- Keep a small hand-written test set of ~15 example queries (5 English, 5 Hindi, 5 Marathi) covering each intent, and assert correct intent + entity extraction. This becomes your regression suite — do not skip it, it's what proves multilingual support actually works for the demo.

## Example test cases (put these in `tests/test_nlu_agent.py`)
| Input | Expected language | Expected intent |
|---|---|---|
| "Where is the nearest PFZ today?" | en | pfz_lookup |
| "Is it safe to venture into the sea tomorrow morning?" | en | safety_check |
| "मुझे कल सुबह मछली पकड़ने जाना है, क्या यह सुरक्षित है?" | hi | safety_check |
| "उद्या सकाळी समुद्रात जाणे सुरक्षित आहे का?" | mr | safety_check |
| "Which regions show high chlorophyll and favourable SST?" | en | chlorophyll_sst_lookup |
| "What if I leave at 7 AM instead?" (with prior_context set) | same as prior | followup, time_window overridden |

## Out of scope
- Speech-to-text (voice interface is explicitly SKIP for the 3-day build).
- Supporting more than 3 languages in the demo (architecture should allow it, implementation doesn't need to).
