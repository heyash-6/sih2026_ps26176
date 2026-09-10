from typing import List, Dict, Any
from app.config import settings
from app.schemas.risk import RiskInput, RiskResult, RiskBandEnum, ComponentRiskBreakdown
from app.schemas.weather import HazardAlert, SeverityEnum
from app.schemas.gis import GeofenceStatusEnum

class RiskEngine:
    """
    Stage 6: Deterministic Risk Engine.
    Computes objective, multi-component risk scores (0-100) using strict mathematical rules.
    NO LLM involved — 100% reproducible and auditable.
    """

    def compute_risk(self, input_data: RiskInput) -> RiskResult:
        weights = settings.risk_weights

        # 1. Wave Risk (30%)
        # Buckets: <0.5m -> 5, 0.5-1.25m -> 20, 1.25-2m -> 50, 2-4m -> 80, >4m -> 100
        wh = input_data.wave_height_m
        if wh < 0.5:
            wave_score = 5.0
        elif wh <= 1.25:
            wave_score = 20.0
        elif wh <= 2.0:
            wave_score = 50.0
        elif wh <= 4.0:
            wave_score = 80.0
        else:
            wave_score = 100.0

        # 2. Wind Risk (20%)
        # Buckets: <15 -> 5, 15-25 -> 25, 25-40 -> 60, >40 -> 100
        ws = input_data.wind_speed_kmh
        if ws < 15.0:
            wind_score = 5.0
        elif ws <= 25.0:
            wind_score = 25.0
        elif ws <= 40.0:
            wind_score = 60.0
        else:
            wind_score = 100.0

        # 3. Hazard Risk (30%)
        # Max severity across active hazards: none->0, low->30, moderate->60, high->85, severe->100
        hazard_score = 0.0
        flags = []
        if input_data.hazards:
            severity_map = {
                SeverityEnum.LOW: 30.0,
                SeverityEnum.MODERATE: 60.0,
                SeverityEnum.HIGH: 85.0,
                SeverityEnum.SEVERE: 100.0
            }
            for hz in input_data.hazards:
                s_val = severity_map.get(hz.severity, 0.0)
                if s_val > hazard_score:
                    hazard_score = s_val
                flags.append(f"active_{hz.hazard_type.value}_advisory_{hz.severity.value}")

        # 4. Distance & Duration Risk (10%)
        # Scales with distance and trip duration
        dist_score = min(100.0, (input_data.distance_km / 50.0) * 50.0 + (input_data.trip_duration_hours / 12.0) * 50.0)

        # 5. Geofence Risk (10%)
        hard_block = False
        if input_data.geofence_status == GeofenceStatusEnum.INTERSECTS:
            geofence_score = 100.0
            hard_block = True
            flags.append("intersects_restricted_zone")
        elif input_data.geofence_status == GeofenceStatusEnum.NEAR_BOUNDARY:
            geofence_score = 40.0
            flags.append("near_maritime_boundary")
        else:
            geofence_score = 0.0

        # Weighted calculation
        total_risk = round(
            (weights.wave * wave_score) +
            (weights.wind * wind_score) +
            (weights.hazard * hazard_score) +
            (weights.distance_duration * dist_score) +
            (weights.geofence * geofence_score),
            1
        )
        total_risk = min(100.0, max(0.0, total_risk))

        # Risk Band assignment
        if total_risk <= 25.0:
            band = RiskBandEnum.LOW
        elif total_risk <= 50.0:
            band = RiskBandEnum.MODERATE
        elif total_risk <= 75.0:
            band = RiskBandEnum.HIGH
        else:
            band = RiskBandEnum.VERY_HIGH

        components = ComponentRiskBreakdown(
            wave_risk=wave_score,
            wind_risk=wind_score,
            hazard_risk=hazard_score,
            distance_duration_risk=dist_score,
            geofence_risk=geofence_score
        )

        return RiskResult(
            zone_id=input_data.zone_id,
            total_risk=total_risk,
            band=band,
            components=components,
            weights_used=weights.model_dump(),
            hard_block=hard_block,
            flags=flags,
            disclaimer=settings.disclaimer_text
        )

    def compute_risk_from_dicts(
        self, zone_id: str, distance_km: float, wave_height_m: float,
        wind_speed_kmh: float, hazards: List[Any], geofence_status: str,
        trip_duration_hours: float = 6.0
    ) -> RiskResult:
        hz_alerts = []
        for h in hazards:
            if isinstance(h, HazardAlert):
                hz_alerts.append(h)
            elif isinstance(h, dict):
                hz_alerts.append(HazardAlert(**h))
                
        g_status = GeofenceStatusEnum(geofence_status) if isinstance(geofence_status, str) else geofence_status
        
        r_input = RiskInput(
            zone_id=zone_id,
            distance_km=distance_km,
            wave_height_m=wave_height_m,
            wind_speed_kmh=wind_speed_kmh,
            hazards=hz_alerts,
            geofence_status=g_status,
            trip_duration_hours=trip_duration_hours
        )
        return self.compute_risk(r_input)

risk_engine = RiskEngine()
