from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_Contains
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from database.connection import SessionLocal
from database.models import RestrictedZone

router = APIRouter(prefix="/api/gis/geofence", tags=["Geofencing"])


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class GeofenceCheckRequest(BaseModel):
    latitude: float
    longitude: float


@router.post("/check")
def check_geofence(
    request: GeofenceCheckRequest,
    db: Session = Depends(get_db),
):
    # 1 & 2. Create WGS84 POINT using (longitude, latitude) order
    user_point = from_shape(Point(request.longitude, request.latitude), srid=4326)

    # 3 & 4. Query restricted_zones containing the user point using PostGIS ST_Contains
    matching_zones = (
        db.query(RestrictedZone)
        .filter(ST_Contains(RestrictedZone.geometry, user_point))
        .all()
    )

    # 5. Build response
    is_restricted = len(matching_zones) > 0
    zone_list = [
        {
            "id": zone.id,
            "name": zone.name,
            "zone_type": zone.zone_type,
            "source": zone.source,
        }
        for zone in matching_zones
    ]

    return {
        "latitude": request.latitude,
        "longitude": request.longitude,
        "restricted": is_restricted,
        "zones": zone_list,
    }
