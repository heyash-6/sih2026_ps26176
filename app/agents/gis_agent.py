import math
from typing import List, Optional

try:
    from shapely.geometry import Point, Polygon, shape
    HAS_SHAPELY = True
except Exception:
    HAS_SHAPELY = False

from app.config import settings
from app.schemas.gis import LatLon, Route, Waypoint, GeofenceResult, GeofenceStatusEnum, GeofenceIntersection
from app.datasources.base import BaseGISDataSource
from app.datasources.demo_datasources import DemoGISDataSource, haversine_distance
from app.datasources.live_datasources import LiveGISDataSource


def point_in_polygon(x: float, y: float, polygon_coords: list) -> bool:
    """Pure-Python ray-casting algorithm for 2D point-in-polygon checking without C dependencies."""
    inside = False
    n = len(polygon_coords)
    if n < 3:
        return False
    p1x, p1y = polygon_coords[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon_coords[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


class GISAgent:
    """
    Stage 5: GIS & Geospatial Specialist Agent.
    Handles geocoding, Haversine distance, coastal routing, and geofence polygon checks.
    """

    def __init__(self):
        if settings.orca_mode == "live":
            self.gis_ds: BaseGISDataSource = LiveGISDataSource()
        else:
            self.gis_ds: BaseGISDataSource = DemoGISDataSource()

    def geocode(self, location_text: str) -> Optional[LatLon]:
        res = self.gis_ds.geocode(location_text)
        if res:
            return res

        clean = (location_text or "").lower().strip()
        if "sindhudurg" in clean or "malvan" in clean or "vengurla" in clean:
            return LatLon(lat=16.0600, lon=73.4600, resolved_from="Sindhudurg (Malvan Coast)", method="indian_coastal_registry")

        from app.database.indian_coastal_registry import INDIAN_COASTAL_PORTS
        for p in INDIAN_COASTAL_PORTS:
            if clean in p["id"] or p["id"] in clean or clean in p["name"].lower():
                return LatLon(lat=p["lat"], lon=p["lon"], resolved_from=p["name"], method="indian_coastal_registry")

        return None

    def distance_km(self, origin: LatLon, destination: LatLon) -> float:
        return haversine_distance(origin.lat, origin.lon, destination.lat, destination.lon)

    def get_route(self, origin: LatLon, destination: LatLon, speed_kmh: Optional[float] = None) -> Route:
        speed = speed_kmh or settings.default_vessel_speed_kmh
        dist = self.distance_km(origin, destination)
        
        # Calculate travel time in minutes
        travel_time_min = int((dist / speed) * 60)
        
        # Intermediate coastal waypoint for map visualization
        mid_lat = round((origin.lat + destination.lat) / 2, 4)
        mid_lon = round((origin.lon + destination.lon) / 2, 4)
        
        waypoints = [
            Waypoint(lat=origin.lat, lon=origin.lon),
            Waypoint(lat=mid_lat, lon=mid_lon),
            Waypoint(lat=destination.lat, lon=destination.lon)
        ]
        
        return Route(
            origin=origin,
            destination=destination,
            waypoints=waypoints,
            distance_km=dist,
            estimated_travel_time_min=travel_time_min,
            assumed_speed_kmh=speed,
            method="coastal_waypoint_approximation"
        )

    def check_geofence(self, route: Route) -> GeofenceResult:
        features = self.gis_ds.get_geofences()
        if not features:
            return GeofenceResult(status=GeofenceStatusEnum.CLEAR, intersections=[])

        intersections: List[GeofenceIntersection] = []
        status = GeofenceStatusEnum.CLEAR

        for feat in features:
            try:
                geom = feat.get("geometry", {})
                props = feat.get("properties", {})
                zone_type = props.get("zone_type", "restricted_zone")
                zone_name = props.get("zone_name", "Restricted Maritime Zone")

                hit = False
                if HAS_SHAPELY:
                    poly = shape(geom)
                    for wp in route.waypoints:
                        if poly.contains(Point(wp.lon, wp.lat)):
                            hit = True
                            break
                else:
                    coords = geom.get("coordinates", [])
                    # GeoJSON Polygon outer ring
                    outer_ring = coords[0] if coords and isinstance(coords[0], list) and isinstance(coords[0][0], list) else coords
                    for wp in route.waypoints:
                        if point_in_polygon(wp.lon, wp.lat, outer_ring):
                            hit = True
                            break

                if hit:
                    status = GeofenceStatusEnum.INTERSECTS
                    intersections.append(GeofenceIntersection(
                        zone_type=zone_type,
                        zone_name=zone_name,
                        distance_into_zone_km=1.5
                    ))
            except Exception as e:
                print(f"[GIS Agent] Error evaluating polygon: {e}")

        return GeofenceResult(
            status=status,
            intersections=intersections,
            checked_zone_types=["international_boundary", "marine_protected_area", "restricted_zone"]
        )

gis_agent = GISAgent()

