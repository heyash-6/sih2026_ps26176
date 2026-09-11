import math
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import RestrictedZone
from gis.grid import create_marine_grid, mark_restricted_cells
from gis.routing import find_safe_route
from api.pfz import get_nearby_pfz
from api.hazards import get_nearby_hazards
from api.geofence import check_geofence, GeofenceCheckRequest

router = APIRouter(prefix="/api/gis/route", tags=["Routing"])
navigation_router = APIRouter(prefix="/api/gis/navigation", tags=["Navigation"])


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RouteRequest(BaseModel):
    start_latitude: float
    start_longitude: float
    end_latitude: float
    end_longitude: float


def _find_nearest_cell(lat: float, lon: float, grid: list) -> tuple:
    """Find row and col indices of the grid cell nearest to (lat, lon)."""
    best_r, best_c = 0, 0
    min_dist_sq = float("inf")
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            d_sq = (cell["latitude"] - lat) ** 2 + (cell["longitude"] - lon) ** 2
            if d_sq < min_dist_sq:
                min_dist_sq = d_sq
                best_r, best_c = r, c
    return best_r, best_c


@router.post("/safe")
def calculate_safe_route(
    request: RouteRequest,
    db: Session = Depends(get_db),
):
    # 1 & 2. Create a marine grid covering both points with an adaptive buffer
    lat_diff = abs(request.end_latitude - request.start_latitude)
    lon_diff = abs(request.end_longitude - request.start_longitude)
    buffer = max(0.05, max(lat_diff, lon_diff) * 0.2)

    min_lat = min(request.start_latitude, request.end_latitude) - buffer
    max_lat = max(request.start_latitude, request.end_latitude) + buffer
    min_lon = min(request.start_longitude, request.end_longitude) - buffer
    max_lon = max(request.start_longitude, request.end_longitude) + buffer

    # 3. Generate marine grid
    grid = create_marine_grid(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        rows=25,
        cols=25,
    )

    # Mark restricted zones if any in database
    restricted_zones = db.query(RestrictedZone).all()
    mark_restricted_cells(grid, restricted_zones)

    # 5. Convert coordinates to nearest grid cells
    start_row, start_col = _find_nearest_cell(request.start_latitude, request.start_longitude, grid)
    end_row, end_col = _find_nearest_cell(request.end_latitude, request.end_longitude, grid)

    # 4 & 6. Calculate safest route using A* from gis.routing
    route_result = find_safe_route(
        grid=grid,
        start_row=start_row,
        start_col=start_col,
        end_row=end_row,
        end_col=end_col,
    )

    # 7 & 8. Convert path to GeoJSON LineString coordinates [longitude, latitude]
    path_nodes = route_result.get("path", [])
    coordinates = []

    if path_nodes:
        for node in path_nodes:
            cell = grid[node["row"]][node["col"]]
            coordinates.append([cell["longitude"], cell["latitude"]])

        # Pin precise start and destination coordinates
        if len(coordinates) == 1:
            coordinates.append([request.end_longitude, request.end_latitude])
        else:
            coordinates[0] = [request.start_longitude, request.start_latitude]
            coordinates[-1] = [request.end_longitude, request.end_latitude]

        message = "Safest route calculated successfully"
    else:
        message = route_result.get("error", "No route found between coordinates.")

    return {
        "start": {
            "latitude": request.start_latitude,
            "longitude": request.start_longitude,
        },
        "destination": {
            "latitude": request.end_latitude,
            "longitude": request.end_longitude,
        },
        "route": {
            "type": "LineString",
            "coordinates": coordinates,
        },
        "total_cost": route_result.get("total_cost", 0.0),
        "average_risk": route_result.get("average_risk", 0.0),
        "message": message,
    }


@navigation_router.post("/analyze")
def analyze_navigation(
    request: RouteRequest,
    db: Session = Depends(get_db),
):
    # 1. Check nearby PFZ zones around the start location
    pfz_data = get_nearby_pfz(
        latitude=request.start_latitude,
        longitude=request.start_longitude,
        radius_km=50.0,
        db=db,
    )

    # 2. Check nearby hazards around the route/start area
    hazards_data = get_nearby_hazards(
        latitude=request.start_latitude,
        longitude=request.start_longitude,
        radius_km=50.0,
        db=db,
    )

    # 3. Check whether start and destination intersect restricted zones
    start_geofence = check_geofence(
        GeofenceCheckRequest(
            latitude=request.start_latitude,
            longitude=request.start_longitude,
        ),
        db=db,
    )
    dest_geofence = check_geofence(
        GeofenceCheckRequest(
            latitude=request.end_latitude,
            longitude=request.end_longitude,
        ),
        db=db,
    )

    # 4. Calculate the safest route using existing A* routing implementation
    route_data = calculate_safe_route(request, db=db)

    avg_risk = route_data.get("average_risk", 0.0)
    if avg_risk <= 25.0:
        risk_level = "LOW"
    elif avg_risk <= 50.0:
        risk_level = "MEDIUM"
    elif avg_risk <= 75.0:
        risk_level = "HIGH"
    else:
        risk_level = "EXTREME"

    # 5. Return composite JSON response
    return {
        "start": {
            "latitude": request.start_latitude,
            "longitude": request.start_longitude,
        },
        "destination": {
            "latitude": request.end_latitude,
            "longitude": request.end_longitude,
        },
        "pfz": {
            "count": pfz_data.get("count", 0),
            "zones": pfz_data.get("pfz_zones", []),
        },
        "hazards": {
            "count": hazards_data.get("count", 0),
            "zones": hazards_data.get("hazards", []),
        },
        "geofence": {
            "start_restricted": start_geofence.get("restricted", False),
            "destination_restricted": dest_geofence.get("restricted", False),
        },
        "navigation": {
            "route": route_data.get("route", {"type": "LineString", "coordinates": []}),
            "total_cost": route_data.get("total_cost", 0.0),
            "average_risk": avg_risk,
            "risk_level": risk_level,
        },
        "source": "SYNTHETIC DEMO DATA",
    }
