from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import cast
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_Distance, ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from database.connection import SessionLocal
from database.models import HazardZone

router = APIRouter(prefix="/api/gis/hazards", tags=["Hazards"])


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/nearby")
def get_nearby_hazards(
    latitude: float,
    longitude: float,
    radius_km: float = 50.0,
    db: Session = Depends(get_db),
):
    # 1 & 2. Create WGS84 POINT using (longitude, latitude) order
    user_point = from_shape(Point(longitude, latitude), srid=4326)

    # Convert radius from kilometers to meters for PostGIS geography calculations
    radius_meters = radius_km * 1000.0

    # Cast geometries to Geography for accurate geodesic calculations in meters
    zone_geog = cast(HazardZone.geometry, Geography)
    user_geog = cast(user_point, Geography)

    # 4. Calculate distance from user point to hazard polygon
    distance_meters = ST_Distance(zone_geog, user_geog)

    # 3. Find hazard zones within radius_meters using ST_DWithin
    results = (
        db.query(HazardZone, distance_meters.label("distance_meters"))
        .filter(ST_DWithin(zone_geog, user_geog, radius_meters))
        .order_by(distance_meters)
        .all()
    )

    # 5. Format and return results as JSON
    hazard_list = [
        {
            "id": hazard.id,
            "hazard_type": hazard.hazard_type,
            "severity": hazard.severity,
            "distance_km": round(dist_m / 1000.0, 2),
            "valid_from": hazard.valid_from.isoformat() if hazard.valid_from else None,
            "valid_until": hazard.valid_until.isoformat() if hazard.valid_until else None,
            "source": hazard.source,
        }
        for hazard, dist_m in results
    ]

    return {
        "user_location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "radius_km": radius_km,
        "count": len(hazard_list),
        "hazards": hazard_list,
    }
