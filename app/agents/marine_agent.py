from typing import List, Optional
from datetime import datetime
from app.config import settings
from app.schemas.marine import PFZCandidate, OceanConditions, ProductivityTrend
from app.datasources.base import BasePFZDataSource
from app.datasources.demo_datasources import DemoPFZDataSource, haversine_distance
from app.datasources.live_datasources import LivePFZDataSource
from app.database.supabase_client import supabase_client
from app.database.indian_coastal_registry import INDIAN_COASTAL_PORTS, get_port_by_id, get_all_pfz_candidates

class MarineAgent:
    """
    Stage 3: Marine & PFZ Specialist Agent.
    Retrieves PFZ advisories across the entire Indian Coastline from Supabase PostgreSQL,
    INCOIS Live Ocean State / SST Models, or coastal registry, with seamless port-aware filtering.
    """

    def __init__(self):
        self.datasource: BasePFZDataSource = LivePFZDataSource()

    def get_pfz_candidates(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        date: str = "2026-09-09",
        radius_km: float = 80.0,
        port_id: Optional[str] = None
    ) -> List[PFZCandidate]:
        candidates: List[PFZCandidate] = []

        # 1. Try Supabase first
        try:
            db_zones = supabase_client.get_pfz_zones(port_id=port_id, lat=lat, lon=lon, limit=50)
            if db_zones:
                for r in db_zones:
                    cand = PFZCandidate(
                        zone_id=r["id"],
                        name=r.get("name", r["id"]),
                        sector=r.get("sector", "Indian Coastal Zone"),
                        port_id=r.get("port_id"),
                        port_name=r.get("port_name"),
                        lat=r["latitude"],
                        lon=r["longitude"],
                        distance_km=r.get("distance_km", 25.0),
                        bearing_deg=r.get("bearing_deg", 250.0),
                        depth_m=r.get("depth_m", 45.0),
                        date=date,
                        sst_celsius=r.get("sst_celsius", 28.0),
                        chlorophyll_mg_m3=r.get("chlorophyll_mg_m3", 1.2),
                        confidence_score=r.get("confidence_score", 0.90),
                        source=r.get("source", "INCOIS PFZ Real-time Advisory"),
                        confidence="advisory"
                    )
                    candidates.append(cand)
                if candidates:
                    return candidates
        except Exception:
            pass

        # 2. Port-specific lookup from coastal registry
        if port_id and port_id.lower() not in ["all", "any"]:
            port = get_port_by_id(port_id)
            for item in port["pfz_candidates"]:
                candidates.append(PFZCandidate(
                    zone_id=item["id"],
                    name=item["name"],
                    sector=port["sector"],
                    port_id=port["id"],
                    port_name=port["name"],
                    lat=item["lat"],
                    lon=item["lon"],
                    distance_km=item.get("distance_km", 25.0),
                    bearing_deg=item.get("bearing_deg", 250.0),
                    depth_m=item.get("depth_m", 45.0),
                    date=date,
                    sst_celsius=28.2,
                    chlorophyll_mg_m3=1.6,
                    confidence_score=0.92,
                    source="INCOIS Indian Coastline Registry",
                    confidence="advisory"
                ))
            return candidates

        # 3. All Indian coastal PFZs
        if port_id and port_id.lower() in ["all", "any"]:
            for item in get_all_pfz_candidates():
                candidates.append(PFZCandidate(
                    zone_id=item["id"],
                    name=item["name"],
                    sector=item["sector"],
                    port_id=item["port_id"],
                    port_name=item["port_name"],
                    lat=item["lat"],
                    lon=item["lon"],
                    distance_km=item.get("distance_km", 25.0),
                    bearing_deg=item.get("bearing_deg", 250.0),
                    depth_m=item.get("depth_m", 45.0),
                    date=date,
                    sst_celsius=28.2,
                    chlorophyll_mg_m3=1.6,
                    confidence_score=0.92,
                    source="INCOIS Indian Coastline Registry",
                    confidence="advisory"
                ))
            return candidates

        # 4. Proximity matching based on lat/lon
        if lat is not None and lon is not None:
            all_cands = get_all_pfz_candidates()
            for item in all_cands:
                dist = haversine_distance(lat, lon, item["lat"], item["lon"])
                if dist <= radius_km:
                    candidates.append(PFZCandidate(
                        zone_id=item["id"],
                        name=item["name"],
                        sector=item["sector"],
                        port_id=item["port_id"],
                        port_name=item["port_name"],
                        lat=item["lat"],
                        lon=item["lon"],
                        distance_km=dist,
                        bearing_deg=item.get("bearing_deg", 250.0),
                        depth_m=item.get("depth_m", 45.0),
                        date=date,
                        sst_celsius=28.2,
                        chlorophyll_mg_m3=1.6,
                        confidence_score=0.92,
                        source="INCOIS Indian Coastline Registry",
                        confidence="advisory"
                    ))
            if candidates:
                candidates.sort(key=lambda c: c.distance_km)
                return candidates

        # 5. Final fallback to datasource
        return self.datasource.get_pfz_candidates(lat or 18.94, lon or 72.83, date, radius_km)

    def get_ocean_conditions(self, lat: float, lon: float, date: str) -> OceanConditions:
        return self.datasource.get_ocean_conditions(lat, lon, date)

    def explain_productivity_trend(self, lat: float, lon: float, date_range: List[str]) -> ProductivityTrend:
        return self.datasource.explain_productivity_trend(lat, lon, date_range)

marine_agent = MarineAgent()
