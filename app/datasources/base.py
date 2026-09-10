from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.marine import PFZCandidate, OceanConditions, ProductivityTrend
from app.schemas.weather import WeatherReading, MarineConditions, HazardAlert
from app.schemas.gis import LatLon, Route, GeofenceResult

class BasePFZDataSource(ABC):
    @abstractmethod
    def get_pfz_candidates(self, lat: float, lon: float, date: str, radius_km: float = 50.0) -> List[PFZCandidate]:
        pass

    @abstractmethod
    def get_ocean_conditions(self, lat: float, lon: float, date: str) -> OceanConditions:
        pass

    @abstractmethod
    def explain_productivity_trend(self, lat: float, lon: float, date_range: List[str]) -> ProductivityTrend:
        pass

class BaseWeatherDataSource(ABC):
    @abstractmethod
    def get_weather(self, lat: float, lon: float, datetime_str: str) -> WeatherReading:
        pass

    @abstractmethod
    def get_marine_conditions(self, lat: float, lon: float, datetime_str: str) -> MarineConditions:
        pass

class BaseHazardDataSource(ABC):
    @abstractmethod
    def get_hazards(self, lat: float, lon: float, datetime_str: str, window_hours: int = 24) -> List[HazardAlert]:
        pass

class BaseGISDataSource(ABC):
    @abstractmethod
    def geocode(self, location_text: str) -> Optional[LatLon]:
        pass

    @abstractmethod
    def get_geofences(self) -> List[dict]:
        pass
