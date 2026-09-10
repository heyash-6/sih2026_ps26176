# Agent Spec: Weather & Hazard Agent

## Purpose
Provides meteorological and marine-hazard data for a location/time. A tool module called by the Planner, not an LLM-facing chat agent.

## Responsibilities
- `get_weather(lat, lon, datetime) -> WeatherReading`
  Wind speed/direction, rainfall probability/intensity, air temperature.
- `get_marine_conditions(lat, lon, datetime) -> MarineConditions`
  Wave height, swell period/direction, sea state category.
- `get_hazards(lat, lon, datetime, window_hours=24) -> List[HazardAlert]`
  Lightning, cyclone, storm surge, high-wave advisories active in the window.

## Output schema — WeatherReading
```json
{
  "lat": 16.99, "lon": 73.30, "datetime": "2026-09-09T05:00:00+05:30",
  "wind_speed_kmh": 12.4,
  "wind_direction_deg": 245,
  "rain_probability_pct": 20,
  "air_temp_celsius": 27.1,
  "source": "Open-Meteo (demo snapshot) / IMD"
}
```

## Output schema — MarineConditions
```json
{
  "lat": 16.99, "lon": 73.30, "datetime": "2026-09-09T05:00:00+05:30",
  "wave_height_m": 0.8,
  "swell_period_s": 6.2,
  "sea_state": "slight",
  "source": "INCOIS ocean state forecast (demo snapshot)"
}
```

## Output schema — HazardAlert
```json
{
  "hazard_type": "lightning",
  "severity": "moderate",
  "active_window": {"start": "2026-09-09T14:00:00+05:30", "end": "2026-09-09T18:00:00+05:30"},
  "area_description": "coastal Ratnagiri and adjoining waters",
  "source": "IMD nowcast bulletin (demo snapshot)",
  "advisory_text_raw": null
}
```
`hazard_type` enum: `lightning | cyclone | high_wave | storm_surge | strong_wind | other`.
`severity` enum: `low | moderate | high | severe`.

## Behavior rules
- If no hazards are active for the queried window, return an empty list — never omit the field or return null (Decision agent needs to positively state "no active hazard alerts").
- Every reading must include `source`. If DEMO mode, source string must say so explicitly (e.g. `"(demo snapshot)"`) — never claim demo data is a live official bulletin. This matters for judge scrutiny and is an easy integrity win.
- Time zone: always work in and return `+05:30` (IST) explicitly in datetimes, since this is an India-focused system.

## Data sourcing plan
- **DEMO mode:** `data/demo/weather.json`, `data/demo/hazards.json` covering the same curated points/date range as the Marine/PFZ demo data, including at least one scenario with an active hazard (to demonstrate the alert path) and one clean scenario (to demonstrate the "all clear" path).
- **LIVE mode:** wrap Open-Meteo (free, no key needed, good for wind/rain) and, if time permits, IMD/INCOIS bulletins for hazards. Treat this as a stretch goal — DEMO mode carries the 3-day build.
- Same `WeatherDataSource` interface pattern as file 03, switched by `ORCA_MODE`.

## Implementation notes for Antigravity
- No LLM inside this module.
- Build a tiny synthetic "hazard injector" for the demo: a config flag that turns ON a lightning alert for one of your candidate PFZs specifically so the risk engine and decision agent visibly downgrade/avoid that zone in the live demo — this is what makes the "AVOID" branch of your demo credible instead of everything always being LOW risk.

## Test cases
- Query at a datetime inside an active hazard window returns that hazard in the list with correct `severity`.
- Query at a datetime outside any hazard window returns `[]`.
- `get_marine_conditions` `sea_state` classification matches a documented wave-height→sea-state mapping table (define this table explicitly in code/comments, e.g. WMO sea state scale, so it's not a magic string).
