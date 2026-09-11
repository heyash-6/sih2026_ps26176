"""
Marine Voyage Navigator
High-level navigational planning engine combining risk-aware A* pathfinding,
live INCOIS ocean wave telemetry, and maritime boundary geofencing.
"""

import math
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from app.gis.grid import create_marine_grid, mark_restricted_cells
from app.gis.routing import find_safe_route
from app.datasources.incois_client import incois_client

_GEOFENCES_FILE = Path(__file__).parent.parent.parent / "data" / "demo" / "geofences.json"

def _load_geofences() -> List[dict]:
    if _GEOFENCES_FILE.is_file():
        try:
            with open(_GEOFENCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("features", [])
        except Exception:
            pass
    return []

def _find_nearest_cell(lat: float, lon: float, grid: List[List[dict]]) -> Tuple[int, int]:
    best_r, best_c = 0, 0
    min_dist_sq = float("inf")
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            d_sq = (cell["latitude"] - lat) ** 2 + (cell["longitude"] - lon) ** 2
            if d_sq < min_dist_sq:
                min_dist_sq = d_sq
                best_r, best_c = r, c
    return best_r, best_c

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate compass heading bearing in degrees from point 1 to point 2."""
    r_lat1 = math.radians(lat1)
    r_lat2 = math.radians(lat2)
    diff_lon = math.radians(lon2 - lon1)

    x = math.sin(diff_lon) * math.cos(r_lat2)
    y = math.cos(r_lat1) * math.sin(r_lat2) - (math.sin(r_lat1) * math.cos(r_lat2) * math.cos(diff_lon))
    initial_bearing = math.atan2(x, y)
    compass_bearing = (math.degrees(initial_bearing) + 360) % 360
    return round(compass_bearing, 1)

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class MarineNavigator:
    """Core navigation orchestrator for ORCA safe marine routing."""

    def __init__(self):
        self.geofences = _load_geofences()

    def calculate_safe_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        vessel_speed_kmh: float = 18.0
    ) -> Dict[str, Any]:
        """Compute optimal risk-aware marine path avoiding geofences and hazards."""
        # 1. Fetch live INCOIS wave height at departure to parameterize grid risk
        base_wave = 1.1
        try:
            swh, _ = incois_client.get_live_wave(start_lat, start_lon)
            if swh is not None:
                base_wave = swh
        except Exception:
            pass

        # 2. Adaptive bounding box with safety buffer
        lat_diff = abs(end_lat - start_lat)
        lon_diff = abs(end_lon - start_lon)
        buffer = max(0.08, max(lat_diff, lon_diff) * 0.25)

        min_lat = min(start_lat, end_lat) - buffer
        max_lat = max(start_lat, end_lat) + buffer
        min_lon = min(start_lon, end_lon) - buffer
        max_lon = max(start_lon, end_lon) + buffer

        # 3. Create marine grid
        rows, cols = 28, 28
        grid = create_marine_grid(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            rows=rows,
            cols=cols,
            base_wave_height=base_wave
        )

        # 4. Mark restricted zones / geofences
        mark_restricted_cells(grid, self.geofences)

        # 5. Snap coordinates to grid
        start_r, start_c = _find_nearest_cell(start_lat, start_lon, grid)
        end_r, end_c = _find_nearest_cell(end_lat, end_lon, grid)

        # Ensure start and end are traversable
        grid[start_r][start_c]["blocked"] = False
        grid[end_r][end_c]["blocked"] = False

        # 6. Run A* pathfinding
        res = find_safe_route(grid, start_r, start_c, end_r, end_c)
        path_nodes = res.get("path", [])

        # 7. Generate precise coordinates and waypoints
        coordinates = []
        waypoints_detail = []
        total_distance_km = 0.0

        if path_nodes:
            # Build smoothed coordinate track
            for node in path_nodes:
                cell = grid[node["row"]][node["col"]]
                coordinates.append([cell["longitude"], cell["latitude"]])

            # Pin exact start and destination coordinates
            if len(coordinates) == 1:
                coordinates.append([end_lon, end_lat])
            else:
                coordinates[0] = [start_lon, start_lat]
                coordinates[-1] = [end_lon, end_lat]

            # Build navigational waypoints
            cum_dist = 0.0
            for idx in range(len(coordinates)):
                curr_lon, curr_lat = coordinates[idx]
                leg_dist = 0.0
                bearing = 0.0
                if idx > 0:
                    prev_lon, prev_lat = coordinates[idx - 1]
                    leg_dist = haversine_km(prev_lat, prev_lon, curr_lat, curr_lon)
                    bearing = calculate_bearing(prev_lat, prev_lon, curr_lat, curr_lon)
                    cum_dist += leg_dist

                # Associated cell risk
                node_idx = min(idx, len(path_nodes) - 1)
                cell_risk = grid[path_nodes[node_idx]["row"]][path_nodes[node_idx]["col"]]["risk_score"]

                waypoints_detail.append({
                    "step": idx + 1,
                    "latitude": curr_lat,
                    "longitude": curr_lon,
                    "leg_distance_km": round(leg_dist, 2),
                    "cumulative_distance_km": round(cum_dist, 2),
                    "heading_deg": bearing,
                    "cell_risk": cell_risk,
                })

            total_distance_km = round(cum_dist, 2)
            msg = "Navigable route calculated successfully with risk-aware A* algorithm."
        else:
            # Fallback direct line
            coordinates = [[start_lon, start_lat], [end_lon, end_lat]]
            total_distance_km = haversine_km(start_lat, start_lon, end_lat, end_lon)
            msg = res.get("error", "Direct navigational corridor generated.")

        # Voyage duration
        duration_hours = round(total_distance_km / max(vessel_speed_kmh, 5.0), 2)
        duration_minutes = int(round(duration_hours * 60))
        direct_dist = haversine_km(start_lat, start_lon, end_lat, end_lon)
        initial_heading = calculate_bearing(start_lat, start_lon, end_lat, end_lon)

        avg_risk = res.get("average_risk", 35.0)
        if avg_risk <= 30.0:
            risk_band = "LOW"
        elif avg_risk <= 60.0:
            risk_band = "MODERATE"
        elif avg_risk <= 80.0:
            risk_band = "HIGH"
        else:
            risk_band = "CRITICAL"

        return {
            "start": {"latitude": start_lat, "longitude": start_lon},
            "destination": {"latitude": end_lat, "longitude": end_lon},
            "route": {
                "type": "LineString",
                "coordinates": coordinates,
            },
            "summary": {
                "total_distance_km": total_distance_km,
                "total_distance_nm": round(total_distance_km * 0.539957, 2),
                "direct_distance_km": direct_dist,
                "estimated_duration_minutes": duration_minutes,
                "estimated_duration_hours": duration_hours,
                "vessel_speed_kmh": vessel_speed_kmh,
                "initial_heading_deg": initial_heading,
                "average_risk": avg_risk,
                "risk_band": risk_band,
                "base_wave_height_m": base_wave,
                "geofence_zones_avoided": len(self.geofences),
            },
            "waypoints": waypoints_detail,
            "message": msg,
            "algorithm": "A* Pathfinding on 28x28 Marine Risk Surface",
        }

    def analyze_navigation(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        vessel_speed_kmh: float = 18.0
    ) -> Dict[str, Any]:
        """Comprehensive multi-factor voyage navigation analysis."""
        from app.agents.marine_agent import marine_agent
        from app.agents.weather_hazard_agent import weather_hazard_agent

        # 1. Calculate safe route
        route_data = self.calculate_safe_route(start_lat, start_lon, end_lat, end_lon, vessel_speed_kmh)

        # 2. Nearby PFZs at departure
        pfzs = marine_agent.get_pfz_candidates(lat=start_lat, lon=start_lon, radius_km=50.0)

        # 3. Weather and marine conditions at departure & destination
        w_start = weather_hazard_agent.get_weather(start_lat, start_lon, "")
        m_start = weather_hazard_agent.get_marine_conditions(start_lat, start_lon, "")
        w_dest = weather_hazard_agent.get_weather(end_lat, end_lon, "")
        m_dest = weather_hazard_agent.get_marine_conditions(end_lat, end_lon, "")

        # 4. Hazards along route
        hazards = weather_hazard_agent.get_hazards(start_lat, start_lon, "", window_hours=24)

        return {
            "start": {"latitude": start_lat, "longitude": start_lon},
            "destination": {"latitude": end_lat, "longitude": end_lon},
            "navigation": route_data,
            "pfz_candidates_nearby": [p.model_dump() for p in pfzs[:3]],
            "departure_conditions": {
                "weather": w_start.model_dump(),
                "marine": m_start.model_dump(),
            },
            "destination_conditions": {
                "weather": w_dest.model_dump(),
                "marine": m_dest.model_dump(),
            },
            "active_hazards": [h.model_dump() for h in hazards],
            "source": "ORCA Multi-Agent GIS & INCOIS Live Navigation Engine",
        }

navigator = MarineNavigator()
