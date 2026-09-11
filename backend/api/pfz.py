from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import cast
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_Distance, ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from database.connection import SessionLocal
from database.models import PFZZone

router = APIRouter(prefix="/api/gis/pfz", tags=["Potential Fishing Zones"])


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/nearby")
def get_nearby_pfz(
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
    zone_geog = cast(PFZZone.geometry, Geography)
    user_geog = cast(user_point, Geography)

    # 4. Calculate distance from user point to PFZ zone geometry
    distance_meters = ST_Distance(zone_geog, user_geog)

    # 3. Find PFZ zones within radius_meters using ST_DWithin
    results = (
        db.query(PFZZone, distance_meters.label("distance_meters"))
        .filter(ST_DWithin(zone_geog, user_geog, radius_meters))
        .order_by(distance_meters)
        .all()
    )

    # 5. Format and return results as JSON
    pfz_list = [
        {
            "id": zone.id,
            "name": zone.name,
            "distance_km": round(dist_m / 1000.0, 2),
            "sst": zone.sst,
            "chlorophyll": zone.chlorophyll,
            "suitability_score": zone.suitability_score,
            "observation_date": zone.observation_date.isoformat() if zone.observation_date else None,
            "source": zone.source,
        }
        for zone, dist_m in results
    ]

    return {
        "user_location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "radius_km": radius_km,
        "count": len(pfz_list),
        "pfz_zones": pfz_list,
    }
