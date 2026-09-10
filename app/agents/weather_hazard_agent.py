from typing import List
from app.config import settings
from app.schemas.weather import WeatherReading, MarineConditions, HazardAlert
from app.datasources.base import BaseWeatherDataSource, BaseHazardDataSource
from app.datasources.demo_datasources import DemoWeatherDataSource, DemoHazardDataSource
from app.datasources.live_datasources import LiveWeatherDataSource

class WeatherHazardAgent:
    """
    Stage 4: Weather & Hazard Specialist Agent.
    Provides weather forecasts, sea state calculations, and active hazard warnings.
    """

    def __init__(self):
        if settings.orca_mode == "live":
            self.weather_ds: BaseWeatherDataSource = LiveWeatherDataSource()
        else:
            self.weather_ds: BaseWeatherDataSource = DemoWeatherDataSource()
            
        self.hazard_ds: BaseHazardDataSource = DemoHazardDataSource()

    def get_weather(self, lat: float, lon: float, datetime_str: str) -> WeatherReading:
        return self.weather_ds.get_weather(lat, lon, datetime_str)

    def get_marine_conditions(self, lat: float, lon: float, datetime_str: str) -> MarineConditions:
        return self.weather_ds.get_marine_conditions(lat, lon, datetime_str)

    def get_hazards(self, lat: float, lon: float, datetime_str: str, window_hours: int = 24) -> List[HazardAlert]:
        return self.hazard_ds.get_hazards(lat, lon, datetime_str, window_hours)

weather_hazard_agent = WeatherHazardAgent()
