import json
import math
from pathlib import Path
from typing import List, Optional
from app.datasources.base import (
    BasePFZDataSource,
    BaseWeatherDataSource,
    BaseHazardDataSource,
    BaseGISDataSource,
)
from app.schemas.marine import PFZCandidate, OceanConditions, ProductivityTrend, TideSchedule
from app.schemas.weather import WeatherReading, MarineConditions, HazardAlert, HazardTypeEnum, SeverityEnum
from app.schemas.gis import LatLon
from app.schemas.common import TimeWindow

DEMO_DIR = Path(__file__).parent.parent.parent / "data" / "demo"

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class DemoPFZDataSource(BasePFZDataSource):
    def __init__(self):
        with open(DEMO_DIR / "pfz.json", "r", encoding="utf-8") as f:
            self.pfz_data = json.load(f)
        with open(DEMO_DIR / "ocean_conditions.json", "r", encoding="utf-8") as f:
            self.ocean_data = json.load(f)

    def get_pfz_candidates(self, lat: float, lon: float, date: str, radius_km: float = 50.0) -> List[PFZCandidate]:
        candidates = []
        for item in self.pfz_data:
            dist = haversine_distance(lat, lon, item["lat"], item["lon"])
            if dist <= radius_km:
                cand = PFZCandidate(
                    zone_id=item["zone_id"],
                    lat=item["lat"],
                    lon=item["lon"],
                    distance_km=dist,
                    date=date,
                    sst_celsius=item["sst_celsius"],
                    chlorophyll_mg_m3=item["chlorophyll_mg_m3"],
                    source=item.get("source", "INCOIS PFZ Advisory (demo snapshot)"),
                    confidence=item.get("confidence", "advisory")
                )
                candidates.append(cand)
        # Sort candidates ascending by distance_km
        candidates.sort(key=lambda c: c.distance_km)
        return candidates

    def get_ocean_conditions(self, lat: float, lon: float, date: str) -> OceanConditions:
        key = f"{round(lat, 2)},{round(lon, 2)}"
        if key in self.ocean_data:
            data = self.ocean_data[key]
            tide_obj = TideSchedule(**data.get("tide", {})) if "tide" in data else None
            return OceanConditions(
                lat=lat,
                lon=lon,
                date=date,
                sst_celsius=data["sst_celsius"],
                chlorophyll_mg_m3=data["chlorophyll_mg_m3"],
                tide=tide_obj,
                source=data.get("source", "INCOIS Ocean State Advisory")
            )
        # Fallback default
        return OceanConditions(
            lat=lat, lon=lon, date=date,
            sst_celsius=28.2, chlorophyll_mg_m3=1.4,
            tide=TideSchedule(high=["04:12", "16:40"], low=["10:05", "22:30"]),
            source="INCOIS Ocean State Advisory (demo snapshot)"
        )

    def explain_productivity_trend(self, lat: float, lon: float, date_range: List[str]) -> ProductivityTrend:
        return ProductivityTrend(
            region=f"Coastal belt around lat {lat:.2f}, lon {lon:.2f}",
            baseline_window=["2026-08-01", "2026-08-31"],
            current_window=date_range if date_range else ["2026-09-01", "2026-09-08"],
            sst_delta_celsius=1.8,
            chlorophyll_delta_pct=-32.0,
            likely_factors=[
                "SST elevated by +1.8°C above seasonal baseline",
                "Chlorophyll concentration declined by 32%"
            ],
            source="derived from ocean dataset, correlation-based assessment"
        )

class DemoWeatherDataSource(BaseWeatherDataSource):
    def __init__(self):
        with open(DEMO_DIR / "weather.json", "r", encoding="utf-8") as f:
            self.weather_data = json.load(f)

    def get_weather(self, lat: float, lon: float, datetime_str: str) -> WeatherReading:
        # Search by key or fallback
        data = self.weather_data.get("default")
        for k, v in self.weather_data.items():
            if isinstance(v, dict) and abs(v.get("lat", 0) - lat) < 0.1 and abs(v.get("lon", 0) - lon) < 0.1:
                data = v
                break
        return WeatherReading(
            lat=lat, lon=lon, datetime=datetime_str,
            wind_speed_kmh=data["wind_speed_kmh"],
            wind_direction_deg=data["wind_direction_deg"],
            rain_probability_pct=data["rain_probability_pct"],
            air_temp_celsius=data["air_temp_celsius"],
            source=data.get("source", "Open-Meteo & IMD (demo snapshot)")
        )

    def get_marine_conditions(self, lat: float, lon: float, datetime_str: str) -> MarineConditions:
        data = self.weather_data.get("default")
        for k, v in self.weather_data.items():
            if isinstance(v, dict) and abs(v.get("lat", 0) - lat) < 0.1 and abs(v.get("lon", 0) - lon) < 0.1:
                data = v
                break
        return MarineConditions(
            lat=lat, lon=lon, datetime=datetime_str,
            wave_height_m=data.get("wave_height_m", 0.8),
            swell_period_s=data.get("swell_period_s", 6.2),
            sea_state=data.get("sea_state", "slight"),
            source=data.get("source", "INCOIS ocean state forecast (demo snapshot)")
        )

class DemoHazardDataSource(BaseHazardDataSource):
    def __init__(self):
        with open(DEMO_DIR / "hazards.json", "r", encoding="utf-8") as f:
            self.hazard_data = json.load(f)

    def get_hazards(self, lat: float, lon: float, datetime_str: str, window_hours: int = 24) -> List[HazardAlert]:
        alerts = []
        for item in self.hazard_data:
            # Check if requested point is near the hazard location description or coordinates
            alert = HazardAlert(
                hazard_type=HazardTypeEnum(item["hazard_type"]),
                severity=SeverityEnum(item["severity"]),
                active_window=TimeWindow(**item["active_window"]),
                area_description=item["area_description"],
                source=item.get("source", "IMD bulletin (demo snapshot)"),
                advisory_text_raw=item.get("advisory_text_raw")
            )
            alerts.append(alert)
        return alerts

class DemoGISDataSource(BaseGISDataSource):
    def __init__(self):
        with open(DEMO_DIR / "gazetteer.json", "r", encoding="utf-8") as f:
            self.gazetteer = json.load(f)
        with open(DEMO_DIR / "geofences.json", "r", encoding="utf-8") as f:
            self.geofences = json.load(f)

    def geocode(self, location_text: str) -> Optional[LatLon]:
        clean_text = location_text.lower().strip()
        for name, coords in self.gazetteer.items():
            if name in clean_text or clean_text in name:
                return LatLon(
                    lat=coords["lat"],
                    lon=coords["lon"],
                    resolved_from=coords["resolved_from"],
                    method=coords["method"]
                )
        # Default fallback to Ratnagiri if location text is generic like "sea" or "coast"
        if "sea" in clean_text or "ocean" in clean_text or "coast" in clean_text:
            return LatLon(lat=16.9902, lon=73.3120, resolved_from="Ratnagiri Coast", method="gazetteer_fallback")
        return None

    def get_geofences(self) -> List[dict]:
        return self.geofences.get("features", [])
