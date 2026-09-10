import pytest
from app.schemas.decision import CandidatePackage, CandidateStatusEnum
from app.schemas.marine import PFZCandidate
from app.schemas.risk import RiskResult, RiskBandEnum, ComponentRiskBreakdown
from app.agents.decision_agent import decision_agent

def test_decision_agent_ranking():
    # Candidate 1: Blocked
    c1 = CandidatePackage(
        zone_id="PFZ-1",
        pfz=PFZCandidate(zone_id="PFZ-1", lat=16.85, lon=73.10, distance_km=20.0, date="2026-09-09", sst_celsius=28.0, chlorophyll_mg_m3=1.5),
        risk=RiskResult(
            zone_id="PFZ-1", total_risk=30.0, band=RiskBandEnum.MODERATE,
            components=ComponentRiskBreakdown(wave_risk=10, wind_risk=10, hazard_risk=0, distance_duration_risk=10, geofence_risk=100),
            weights_used={}, hard_block=True, disclaimer=""
        )
    )

    # Candidate 2: Valid, low risk
    c2 = CandidatePackage(
        zone_id="PFZ-2",
        pfz=PFZCandidate(zone_id="PFZ-2", lat=16.98, lon=73.12, distance_km=18.4, date="2026-09-09", sst_celsius=28.2, chlorophyll_mg_m3=1.4),
        risk=RiskResult(
            zone_id="PFZ-2", total_risk=22.0, band=RiskBandEnum.LOW,
            components=ComponentRiskBreakdown(wave_risk=10, wind_risk=10, hazard_risk=0, distance_duration_risk=10, geofence_risk=0),
            weights_used={}, hard_block=False, disclaimer=""
        )
    )

    out = decision_agent.decide_and_explain(
        session_id="s1",
        language="en",
        candidates=[c1, c2],
        execution_trace=[]
    )

    assert out.recommendation.zone_id == "PFZ-2"
    assert out.recommendation.status == CandidateStatusEnum.RECOMMENDED
    assert len(out.alternatives_considered) > 0
    assert out.alternatives_considered[0].zone_id == "PFZ-1"
    assert out.alternatives_considered[0].status == CandidateStatusEnum.REJECTED
