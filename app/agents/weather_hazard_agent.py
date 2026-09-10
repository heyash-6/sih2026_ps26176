from typing import List
from app.config import settings
from app.schemas.weather import WeatherReading, MarineConditions, HazardAlert
from app.datasources.base import BaseWeatherDataSource, BaseHazardDataSource
from app.datasources.demo_datasources import DemoWeatherDataSource, DemoHazardDataSource
from app.datasources.live_datasources import LiveWeatherDataSource

from app.database.data_pipeline import data_pipeline

class WeatherHazardAgent:
    """
    Stage 4: Weather & Hazard Specialist Agent.
    Provides weather forecasts, sea state calculations, and active hazard warnings.
    Integrated directly with Supabase PostgreSQL data pipeline.
    """

    def __init__(self):
        if settings.orca_mode == "live":
            self.weather_ds: BaseWeatherDataSource = LiveWeatherDataSource()
        else:
            self.weather_ds: BaseWeatherDataSource = DemoWeatherDataSource()
            
        self.hazard_ds: BaseHazardDataSource = DemoHazardDataSource()

    def get_weather(self, lat: float, lon: float, datetime_str: str) -> WeatherReading:
        reading = self.weather_ds.get_weather(lat, lon, datetime_str)
        # Sync to Supabase in real-time
        return data_pipeline.sync_weather(lat, lon, reading)

    def get_marine_conditions(self, lat: float, lon: float, datetime_str: str) -> MarineConditions:
        conditions = self.weather_ds.get_marine_conditions(lat, lon, datetime_str)
        # Sync to Supabase in real-time
        return data_pipeline.sync_marine_conditions(lat, lon, conditions)

    def get_hazards(self, lat: float, lon: float, datetime_str: str, window_hours: int = 24) -> List[HazardAlert]:
        # Fetch active alerts directly from Supabase
        db_alerts = data_pipeline.get_database_alerts()
        local_alerts = self.hazard_ds.get_hazards(lat, lon, datetime_str, window_hours)
        
        # Merge alerts, prioritizing live Supabase alerts
        combined = []
        seen = set()
        for a in (db_alerts + local_alerts):
            aid = getattr(a, "alert_id", None) or f"{a.hazard_type}_{a.area_description}"
            if aid not in seen:
                combined.append(a)
                seen.add(aid)
        return combined

weather_hazard_agent = WeatherHazardAgent()

