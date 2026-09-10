# Agent Spec: GIS / Geospatial Agent

## Purpose
Handles all spatial computation: geocoding, distance, routing, and geofence intersection. A tool module called by the Planner. This talks to the DB team's PostGIS layer for geofence polygons and route geometry storage — define that interface with them on day 1.

## Responsibilities
- `geocode(location_text) -> LatLon`
  Resolves a place name (e.g. "Ratnagiri") to coordinates. Use a static gazetteer of Indian coastal towns for DEMO mode; a real geocoding API (e.g. Nominatim/OpenStreetMap) for LIVE mode.
- `distance_km(origin: LatLon, destination: LatLon) -> float`
  Haversine great-circle distance. (Straight-line, not sea-route — flag this explicitly in the output so the Decision agent doesn't overstate precision.)
- `get_route(origin: LatLon, destination: LatLon) -> Route`
  For the 3-day build: a simplified route (straight line or a small number of waypoints hugging the coastline if you have a coastline polyline available from the DB team) plus estimated travel time based on an assumed vessel speed (configurable, default e.g. 15 km/h).
- `check_geofence(route_or_point) -> GeofenceResult`
  Given a route (list of lat/lon points) or a single point, checks intersection against geofence polygons: international maritime boundary, marine protected areas, restricted/hazard zones. This is a spatial query — call into PostGIS via the DB team's function/endpoint (`ST_Intersects`), don't reimplement polygon math yourself unless PostGIS isn't ready in time, in which case fall back to a pure-Python point-in-polygon check (e.g. `shapely`) against a small demo GeoJSON of restricted zones.

## Output schema — LatLon
```json
{ "lat": 16.9902, "lon": 73.3120, "resolved_from": "Ratnagiri", "method": "gazetteer|geocoding_api" }
```

## Output schema — Route
```json
{
  "origin": {"lat": 16.99, "lon": 73.30},
  "destination": {"lat": 16.98, "lon": 73.31},
  "waypoints": [{"lat":16.99,"lon":73.30},{"lat":16.985,"lon":73.305},{"lat":16.98,"lon":73.31}],
  "distance_km": 18.4,
  "estimated_travel_time_min": 74,
  "assumed_speed_kmh": 15,
  "method": "straight_line_approx"
}
```

## Output schema — GeofenceResult
```json
{
  "status": "clear",
  "intersections": [],
  "checked_zone_types": ["international_boundary", "marine_protected_area", "restricted_zone"]
}
```
or, if intersecting:
```json
{
  "status": "intersects",
  "intersections": [
    {"zone_type": "marine_protected_area", "zone_name": "Malvan Marine Sanctuary buffer", "distance_into_zone_km": 1.2}
  ],
  "checked_zone_types": ["international_boundary", "marine_protected_area", "restricted_zone"]
}
```
`status` enum: `clear | intersects | near_boundary` (use `near_boundary` for e.g. within a configurable buffer of the IMBL even without actual intersection — this powers proactive geofencing notifications per the PS requirement).

## Implementation notes for Antigravity
- No LLM inside this module.
- Keep the `distance_km` / `Route` / `GeofenceResult` functions pure and independently unit-testable with hardcoded coordinates.
- Coordinate with the DB teammate early on the exact geofence polygon format and query interface (GeoJSON via a DB-owned FastAPI endpoint is simplest — you shouldn't need direct DB credentials).
- If PostGIS access isn't ready by the time you need it, ship a **DEMO fallback**: 2–3 hand-drawn GeoJSON polygons (one restricted zone, one MPA buffer) bundled in `data/demo/geofences.json`, checked with `shapely.geometry.Point/Polygon` — swap for the real DB-backed version later without changing the function signature.

## Test cases
- `geocode("Ratnagiri")` returns the correct known demo coordinates.
- `distance_km` between two known points matches an independently computed haversine value within a small tolerance.
- A route deliberately crossing the demo restricted polygon returns `status: "intersects"` with the correct `zone_name`.
- A route that stays clear returns `status: "clear"` and empty `intersections`.
