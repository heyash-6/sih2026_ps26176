from typing import List, Optional
from app.config import settings
from app.schemas.marine import PFZCandidate, OceanConditions, ProductivityTrend
from app.datasources.base import BasePFZDataSource
from app.datasources.demo_datasources import DemoPFZDataSource

class MarineAgent:
    """
    Stage 3: Marine & PFZ Specialist Agent.
    Retrieves PFZ advisories, SST/chlorophyll levels, and ocean conditions.
    Switches cleanly between DEMO mode and LIVE mode via config setting.
    """

    def __init__(self):
        self.datasource: BasePFZDataSource = DemoPFZDataSource()

    def get_pfz_candidates(self, lat: float, lon: float, date: str, radius_km: float = 50.0) -> List[PFZCandidate]:
        return self.datasource.get_pfz_candidates(lat, lon, date, radius_km)

    def get_ocean_conditions(self, lat: float, lon: float, date: str) -> OceanConditions:
        return self.datasource.get_ocean_conditions(lat, lon, date)

    def explain_productivity_trend(self, lat: float, lon: float, date_range: List[str]) -> ProductivityTrend:
        return self.datasource.explain_productivity_trend(lat, lon, date_range)

marine_agent = MarineAgent()
