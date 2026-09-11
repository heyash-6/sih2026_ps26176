"""Synthetic marine risk grid generation for pathfinding and navigation."""

import math
from typing import Any, List
from shapely.geometry import Point, box
from shapely.prepared import prep

try:
    from geoalchemy2.shape import to_shape
    from geoalchemy2.elements import WKBElement, WKTElement
except ImportError:
    to_shape = None
    WKBElement = None
    WKTElement = None


def create_marine_grid(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    rows: int = 20,
    cols: int = 20,
) -> List[List[dict]]:
    """Divide a rectangular marine bounding box into a rows x cols grid.

    Each cell contains:
    - row: Row index (0 to rows-1)
    - col: Column index (0 to cols-1)
    - latitude: Center latitude of the cell
    - longitude: Center longitude of the cell
    - risk_score: Deterministic synthetic risk score (0 to 100)
    - blocked: Boolean flag indicating if cell is traversable (initially False)
    """
    lat_step = (max_lat - min_lat) / rows
    lon_step = (max_lon - min_lon) / cols

    grid = []
    for r in range(rows):
        row_cells = []
        cell_lat = min_lat + (r + 0.5) * lat_step
        norm_r = r / max(rows - 1, 1)

        for c in range(cols):
            cell_lon = min_lon + (c + 0.5) * lon_step
            norm_c = c / max(cols - 1, 1)

            # Deterministic wave pattern based on row and column
            raw_score = (
                50.0
                + 25.0 * math.sin(math.pi * norm_r) * math.cos(math.pi * norm_c)
                + 15.0 * math.sin(2.0 * math.pi * norm_r)
                + 10.0 * math.cos(2.0 * math.pi * norm_c)
            )
            risk_score = round(min(max(raw_score, 0.0), 100.0), 2)

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


def _extract_shapely_geometry(zone: Any):
    """Convert input zone or model to a Shapely geometry."""
    if hasattr(zone, "geometry"):
        geom = zone.geometry
    elif isinstance(zone, dict) and "geometry" in zone:
        geom = zone["geometry"]
    else:
        geom = zone

    if to_shape and isinstance(geom, (WKBElement, WKTElement)):
        return to_shape(geom)

    if isinstance(geom, str):
        import shapely.wkt
        return shapely.wkt.loads(geom)

    return geom


def mark_restricted_cells(grid: Any, restricted_zones: list) -> Any:
    """Mark grid cells as blocked if they intersect any restricted zones.

    Parameters:
    - grid: 2D list or 1D list of cell dictionaries
    - restricted_zones: List of Shapely geometries, GeoAlchemy2 models, or WKT strings

    Returns:
    The grid with intersecting cells marked blocked=True.
    """
    if not restricted_zones or not grid:
        return grid

    # Convert all zones to prepared Shapely geometries for fast spatial intersection
    prepared_zones = []
    for z in restricted_zones:
        try:
            s_geom = _extract_shapely_geometry(z)
            if s_geom is not None and hasattr(s_geom, "intersects"):
                prepared_zones.append(prep(s_geom))
        except Exception:
            continue

    if not prepared_zones:
        return grid

    is_2d = isinstance(grid, list) and len(grid) > 0 and isinstance(grid[0], list)

    # Estimate cell dimensions for spatial bounding box check
    half_lat = 0.0
    half_lon = 0.0
    if is_2d and len(grid) > 1 and len(grid[0]) > 0:
        half_lat = abs(grid[1][0]["latitude"] - grid[0][0]["latitude"]) / 2.0
    if is_2d and len(grid) > 0 and len(grid[0]) > 1:
        half_lon = abs(grid[0][1]["longitude"] - grid[0][0]["longitude"]) / 2.0

    cells = [cell for row in grid for cell in row] if is_2d else grid

    for cell in cells:
        lon = cell["longitude"]
        lat = cell["latitude"]

        if half_lat > 0 and half_lon > 0:
            cell_geom = box(lon - half_lon, lat - half_lat, lon + half_lon, lat + half_lat)
        else:
            cell_geom = Point(lon, lat)

        for p_zone in prepared_zones:
            if p_zone.intersects(cell_geom):
                cell["blocked"] = True
                break

    return grid
