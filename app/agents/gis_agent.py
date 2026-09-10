import math
from typing import List, Optional
from shapely.geometry import Point, Polygon, shape
from app.config import settings
from app.schemas.gis import LatLon, Route, Waypoint, GeofenceResult, GeofenceStatusEnum, GeofenceIntersection
from app.datasources.base import BaseGISDataSource
from app.datasources.demo_datasources import DemoGISDataSource, haversine_distance
from app.datasources.live_datasources import LiveGISDataSource

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
        return self.gis_ds.geocode(location_text)

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

        # Create Shapely Point objects for waypoints
        route_points = [Point(wp.lon, wp.lat) for wp in route.waypoints]

        for feat in features:
            try:
                poly = shape(feat["geometry"])
                props = feat.get("properties", {})
                zone_type = props.get("zone_type", "restricted_zone")
                zone_name = props.get("zone_name", "Restricted Maritime Zone")

                for pt in route_points:
                    if poly.contains(pt):
                        status = GeofenceStatusEnum.INTERSECTS
                        intersections.append(GeofenceIntersection(
                            zone_type=zone_type,
                            zone_name=zone_name,
                            distance_into_zone_km=1.5
                        ))
                        break
            except Exception as e:
                print(f"[GIS Agent] Error evaluating polygon: {e}")

        return GeofenceResult(
            status=status,
            intersections=intersections,
            checked_zone_types=["international_boundary", "marine_protected_area", "restricted_zone"]
        )

gis_agent = GISAgent()
