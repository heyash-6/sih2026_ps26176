# Agent Spec: Risk Engine

## Purpose
Converts the raw data gathered by the other agents (marine, weather, hazard, GIS) into a single, explainable, **deterministic** risk score per candidate PFZ/route. **This module must NOT call an LLM.** It is pure rules/arithmetic so it's auditable, reproducible, and defensible in front of judges.

## Responsibilities
`compute_risk(candidate: RiskInput) -> RiskResult`

## Input schema — RiskInput
```json
{
  "zone_id": "PFZ-02",
  "distance_km": 18.4,
  "wave_height_m": 0.8,
  "wind_speed_kmh": 12.4,
  "hazards": [
    {"hazard_type": "lightning", "severity": "moderate"}
  ],
  "geofence_status": "clear",
  "trip_duration_hours": 6
}
```

## Scoring model (transparent, tunable, documented — treat these weights as prototype assumptions, not an official standard, and say so in the report)

Each component contributes 0–100, then a weighted sum produces the total, capped at 100:

| Component | How it's scored | Weight |
|---|---|---|
| Wave risk | `wave_height_m` bucketed: <0.5m→5, 0.5–1.25m→20, 1.25–2m→50, 2–4m→80, >4m→100 | 30% |
| Wind risk | `wind_speed_kmh` bucketed: <15→5, 15–25→25, 25–40→60, >40→100 | 20% |
| Hazard risk | max severity across active hazards: none→0, low→30, moderate→60, high→85, severe→100 | 30% |
| Distance/duration risk | scales with `distance_km` and `trip_duration_hours` vs a safe-return threshold (configurable, e.g. flag if round trip time + fishing time exceeds daylight window) | 10% |
| Geofence risk | `clear`→0, `near_boundary`→40, `intersects`→100 | 10% |

```
total_risk = 0.30*wave + 0.20*wind + 0.30*hazard + 0.10*distance_duration + 0.10*geofence
```

Risk bands:
| Score | Band |
|---|---|
| 0–25 | LOW |
| 26–50 | MODERATE |
| 51–75 | HIGH |
| 76–100 | VERY HIGH |

## Output schema — RiskResult
```json
{
  "zone_id": "PFZ-02",
  "total_risk": 34.6,
  "band": "MODERATE",
  "components": {
    "wave_risk": 20, "wind_risk": 25, "hazard_risk": 60,
    "distance_duration_risk": 10, "geofence_risk": 0
  },
  "weights_used": {"wave":0.30,"wind":0.20,"hazard":0.30,"distance_duration":0.10,"geofence":0.10},
  "flags": ["active_lightning_advisory"],
  "disclaimer": "Prototype risk scoring for demonstration purposes. Not an official safety certification — always consult current government marine advisories before departure."
}
```

## Rules
- All bucket thresholds and weights must live in a single config file/module (`risk_config.py`), not scattered magic numbers — this lets you tune them live during dev/demo and lets you cite them precisely in your report.
- `geofence_risk = 100` (i.e. `intersects`) should be flagged as a hard warning even if the total weighted score is moderate — expose a separate `hard_block: true/false` field so the Decision agent can say "AVOID regardless of score" for restricted-zone intersections, matching the PS's geofencing requirement.
- Function must be pure: same input → same output, no randomness, no external calls, no LLM. This is what you unit-test exhaustively and what you point to when a judge asks "how do you know this isn't the AI hallucinating a risk number."

## Implementation notes for Antigravity
- Implement as one small, heavily unit-tested Python module. This should be the single most over-tested file in your repo — it's your strongest "we didn't just wrap an LLM and call it a day" evidence.
- Write a `risk_config.yaml` or `.py` dict so non-engineers on your team can see/tweak the thresholds without reading code.

## Test cases
- All-calm input (low wave, low wind, no hazards, clear geofence, short trip) → LOW band, `total_risk` roughly in single digits to low twenties.
- Active severe hazard + intersecting geofence → VERY HIGH band, `hard_block: true`.
- Boundary values at each bucket edge (e.g. exactly 0.5m wave) resolve to the documented bucket, not an off-by-one.
- Weighted sum never exceeds 100 even with all components maxed.
