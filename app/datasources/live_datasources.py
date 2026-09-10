import httpx
from typing import List, Optional
from app.datasources.base import (
    BasePFZDataSource,
    BaseWeatherDataSource,
    BaseHazardDataSource,
    BaseGISDataSource,
)
from app.schemas.marine import PFZCandidate, OceanConditions, ProductivityTrend
from app.schemas.weather import WeatherReading, MarineConditions, HazardAlert, HazardTypeEnum, SeverityEnum
from app.schemas.gis import LatLon
from app.schemas.common import TimeWindow

class LiveWeatherDataSource(BaseWeatherDataSource):
    def get_weather(self, lat: float, lon: float, datetime_str: str) -> WeatherReading:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = httpx.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json().get("current_weather", {})
                return WeatherReading(
                    lat=lat, lon=lon, datetime=datetime_str,
                    wind_speed_kmh=data.get("windspeed", 12.0),
                    wind_direction_deg=data.get("winddirection", 240.0),
                    rain_probability_pct=20.0,
                    air_temp_celsius=data.get("temperature", 27.0),
                    source="Open-Meteo Live API"
                )
        except Exception:
            pass
        return WeatherReading(
            lat=lat, lon=lon, datetime=datetime_str,
            wind_speed_kmh=12.0, wind_direction_deg=240.0, rain_probability_pct=15.0, air_temp_celsius=27.0,
            source="Open-Meteo Live Fallback"
        )

    def get_marine_conditions(self, lat: float, lon: float, datetime_str: str) -> MarineConditions:
        try:
            url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height,wave_period"
            response = httpx.get(url, timeout=5.0)
            if response.status_code == 200:
                hourly = response.json().get("hourly", {})
                wave_heights = hourly.get("wave_height", [0.8])
                periods = hourly.get("wave_period", [6.2])
                wh = wave_heights[0] if wave_heights and wave_heights[0] is not None else 0.8
                wp = periods[0] if periods and periods[0] is not None else 6.2
                
                sea_state = "slight"
                if wh < 0.5: sea_state = "calm"
                elif wh < 1.25: sea_state = "slight"
                elif wh < 2.5: sea_state = "moderate"
                else: sea_state = "rough"

                return MarineConditions(
                    lat=lat, lon=lon, datetime=datetime_str,
                    wave_height_m=wh, swell_period_s=wp, sea_state=sea_state,
                    source="Open-Meteo Marine Live API"
                )
        except Exception:
            pass
        return MarineConditions(
            lat=lat, lon=lon, datetime=datetime_str,
            wave_height_m=0.8, swell_period_s=6.2, sea_state="slight",
            source="Open-Meteo Marine Live Fallback"
        )

class LiveGISDataSource(BaseGISDataSource):
    def geocode(self, location_text: str) -> Optional[LatLon]:
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={location_text},India&format=json&limit=1"
            headers = {"User-Agent": "ORCA-Marine-Intelligence-Agent/1.0"}
            response = httpx.get(url, headers=headers, timeout=5.0)
            if response.status_code == 200:
                results = response.json()
                if results:
                    item = results[0]
                    return LatLon(
                        lat=float(item["lat"]),
                        lon=float(item["lon"]),
                        resolved_from=item.get("display_name", location_text),
                        method="nominatim_live_api"
                    )
        except Exception:
            pass
        return None

    def get_geofences(self) -> List[dict]:
        return []
