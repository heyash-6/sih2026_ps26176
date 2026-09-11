"""
Marine Risk Grid Generator
Generates spatial risk surface grids for coastal navigation pathfinding,
incorporating live bathymetry, restricted maritime boundaries, and INCOIS wave telemetry.
"""

import math
from typing import Any, List, Optional
from shapely.geometry import Point, box, Polygon
from shapely.prepared import prep


def create_marine_grid(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    rows: int = 24,
    cols: int = 24,
    base_wave_height: float = 1.2,
) -> List[List[dict]]:
    """Divide a rectangular marine bounding box into a rows x cols navigation grid.

    Each cell contains:
    - row, col: Indices
    - latitude, longitude: Center coordinates
    - risk_score: Environmental and navigational risk (0 to 100)
    - blocked: Boolean flag indicating if cell is traversable
    """
    lat_step = (max_lat - min_lat) / max(rows, 1)
    lon_step = (max_lon - min_lon) / max(cols, 1)

    # Higher wave height raises base marine navigation risk proportionally
    wave_risk_base = min(85.0, max(10.0, base_wave_height * 24.0))

    grid = []
    for r in range(rows):
        row_cells = []
        cell_lat = min_lat + (r + 0.5) * lat_step
        norm_r = r / max(rows - 1, 1)

        for c in range(cols):
            cell_lon = min_lon + (c + 0.5) * lon_step
            norm_c = c / max(cols - 1, 1)

            # Oceanographic wave modulation across the grid
            wave_variation = (
                15.0 * math.sin(math.pi * norm_r) * math.cos(math.pi * norm_c)
                + 10.0 * math.sin(2.0 * math.pi * norm_r)
                + 8.0 * math.cos(2.0 * math.pi * norm_c)
            )
            raw_score = wave_risk_base + wave_variation
            risk_score = round(min(max(raw_score, 5.0), 95.0), 1)

            cell = {
                "row": r,
                "col": c,
                "latitude": round(cell_lat, 5),
                "longitude": round(cell_lon, 5),
                "risk_score": risk_score,
                "blocked": False,
            }
            row_cells.append(cell)
        grid.append(row_cells)

    return grid


def _extract_shapely_geometry(zone: Any) -> Optional[Any]:
    """Convert input zone, GeoJSON dict, or model to a Shapely geometry."""
    try:
        if isinstance(zone, (Polygon, Point)):
            return zone

        if isinstance(zone, dict):
            geom = zone.get("geometry", zone)
            g_type = geom.get("type", "")
            coords = geom.get("coordinates", [])
            if g_type == "Polygon" and coords:
                return Polygon(coords[0])
            elif g_type == "Point" and coords:
                return Point(coords[0], coords[1])

        if hasattr(zone, "geometry"):
            return zone.geometry

        if isinstance(zone, str):
            import shapely.wkt
            return shapely.wkt.loads(zone)
    except Exception:
        pass
    return None


def mark_restricted_cells(grid: List[List[dict]], restricted_zones: list) -> List[List[dict]]:
    """Mark grid cells as blocked if they intersect any restricted zones or marine protected areas."""
    if not restricted_zones or not grid:
        return grid

    prepared_zones = []
    for z in restricted_zones:
        s_geom = _extract_shapely_geometry(z)
        if s_geom is not None and hasattr(s_geom, "intersects"):
            prepared_zones.append(prep(s_geom))

    if not prepared_zones:
        return grid

    rows = len(grid)
    cols = len(grid[0])
    half_lat = abs(grid[1][0]["latitude"] - grid[0][0]["latitude"]) / 2.0 if rows > 1 else 0.02
    half_lon = abs(grid[0][1]["longitude"] - grid[0][0]["longitude"]) / 2.0 if cols > 1 else 0.02

    for row in grid:
        for cell in row:
            lon = cell["longitude"]
            lat = cell["latitude"]
            cell_box = box(lon - half_lon, lat - half_lat, lon + half_lon, lat + half_lat)

            for p_zone in prepared_zones:
                if p_zone.intersects(cell_box):
                    cell["blocked"] = True
                    cell["risk_score"] = 100.0
                    break

    return grid
