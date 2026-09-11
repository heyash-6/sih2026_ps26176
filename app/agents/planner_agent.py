import time
from typing import List, Dict, Any, Optional
from app.schemas.nlu import NLUOutput, IntentEnum
from app.schemas.planner import PlanInput, PlanOutput, ExecutionTraceStep, PlanStepItem
from app.schemas.common import ErrorDetail, LatLon
from app.agents.marine_agent import marine_agent
from app.agents.weather_hazard_agent import weather_hazard_agent
from app.agents.gis_agent import gis_agent
from app.agents.risk_engine import risk_engine

class PlannerAgent:
    """
    Stage 2: Planner Agent.
    Decomposes requests into executable task lists, invokes specialized modules
    (Marine, Weather/Hazard, GIS, Risk Engine), logs execution traces, and aggregates results.
    """

    def plan_and_execute(self, nlu_output: NLUOutput) -> PlanOutput:
        session_id = nlu_output.session_id
        intent = nlu_output.intent
        entities = nlu_output.entities

        execution_trace: List[ExecutionTraceStep] = []
        plan: List[PlanStepItem] = []
        results: Dict[str, Any] = {}
        errors: List[ErrorDetail] = []
        step_counter = 1

        location_text = entities.location_text or "Mumbai"
        date_str = entities.date or "2026-09-09"
        datetime_str = f"{date_str}T05:00:00+05:30"

        # Step 1: Geocode location if LatLon not already set
        t0 = time.time()
        plan.append(PlanStepItem(step=step_counter, tool="geocode", params={"location_text": location_text}))
        coords = gis_agent.geocode(location_text)
        duration_ms = int((time.time() - t0) * 1000)
        
        if not coords:
            coords = LatLon(lat=18.9400, lon=72.8300, resolved_from="Mumbai Harbour", method="coastal_hub")

        execution_trace.append(ExecutionTraceStep(
            step=step_counter, tool="geocode", status="done", duration_ms=duration_ms,
            details=f"Resolved '{location_text}' to ({coords.lat}, {coords.lon})"
        ))
        results["origin_coords"] = coords
        step_counter += 1

        # Step 2: Retrieve PFZ candidates (if intent requires PFZ or full trip planning)
        candidates = []
        if intent in [IntentEnum.FISHING_TRIP_PLANNING, IntentEnum.PFZ_LOOKUP, IntentEnum.SAFETY_CHECK]:
            t0 = time.time()
            plan.append(PlanStepItem(
                step=step_counter, tool="get_pfz_candidates",
                params={"lat": coords.lat, "lon": coords.lon, "date": date_str}
            ))
            try:
                candidates = marine_agent.get_pfz_candidates(coords.lat, coords.lon, date_str, radius_km=50.0)
                duration_ms = int((time.time() - t0) * 1000)
                execution_trace.append(ExecutionTraceStep(
                    step=step_counter, tool="get_pfz_candidates", status="done", duration_ms=duration_ms,
                    details=f"Retrieved {len(candidates)} PFZ candidates"
                ))
            except Exception as e:
                errors.append(ErrorDetail(tool="get_pfz_candidates", error_message=str(e)))
                execution_trace.append(ExecutionTraceStep(
                    step=step_counter, tool="get_pfz_candidates", status="failed", duration_ms=0, details=str(e)
                ))
            step_counter += 1

        results["pfz_candidates"] = [c.model_dump() for c in candidates]

        # Step 3: Fetch Weather & Marine Conditions per candidate
        weather_by_candidate = {}
        marine_by_candidate = {}
        t0 = time.time()
        plan.append(PlanStepItem(
            step=step_counter, tool="get_weather_and_marine",
            params={"candidate_count": len(candidates), "datetime": datetime_str}
        ))
        for cand in candidates:
            try:
                w_reading = weather_hazard_agent.get_weather(cand.lat, cand.lon, datetime_str)
                m_reading = weather_hazard_agent.get_marine_conditions(cand.lat, cand.lon, datetime_str)
                weather_by_candidate[cand.zone_id] = w_reading.model_dump()
                marine_by_candidate[cand.zone_id] = m_reading.model_dump()
            except Exception as e:
                errors.append(ErrorDetail(tool="get_weather_and_marine", error_message=str(e)))

        duration_ms = int((time.time() - t0) * 1000)
        execution_trace.append(ExecutionTraceStep(
            step=step_counter, tool="get_weather_and_marine", status="done", duration_ms=duration_ms,
            details=f"Retrieved weather and sea state for {len(candidates)} candidates"
        ))
        results["weather_by_candidate"] = weather_by_candidate
        results["marine_by_candidate"] = marine_by_candidate
        step_counter += 1

        # Step 4: Fetch Active Hazard Alerts & Regional Sea State
        t0 = time.time()
        plan.append(PlanStepItem(step=step_counter, tool="get_hazards", params={"datetime": datetime_str}))
        hazards = weather_hazard_agent.get_hazards(coords.lat, coords.lon, datetime_str)
        origin_weather = weather_hazard_agent.get_weather(coords.lat, coords.lon, datetime_str)
        origin_marine = weather_hazard_agent.get_marine_conditions(coords.lat, coords.lon, datetime_str)
        duration_ms = int((time.time() - t0) * 1000)
        execution_trace.append(ExecutionTraceStep(
            step=step_counter, tool="get_hazards", status="done", duration_ms=duration_ms,
            details=f"Found {len(hazards)} active hazard bulletins for ({coords.lat}, {coords.lon})"
        ))
        results["hazards"] = [h.model_dump() for h in hazards]
        results["origin_weather"] = origin_weather.model_dump()
        results["origin_marine"] = origin_marine.model_dump()
        step_counter += 1

        # Step 5: Route Calculation & Geofence Checks per candidate
        routes_by_candidate = {}
        geofence_by_candidate = {}
        t0 = time.time()
        plan.append(PlanStepItem(
            step=step_counter, tool="get_routes_and_geofence",
            params={"origin": [coords.lat, coords.lon]}
        ))
        for cand in candidates:
            dest = LatLon(lat=cand.lat, lon=cand.lon)
            route = gis_agent.get_route(coords, dest)
            geofence_res = gis_agent.check_geofence(route)
            
            routes_by_candidate[cand.zone_id] = route.model_dump()
            geofence_by_candidate[cand.zone_id] = geofence_res.model_dump()

        duration_ms = int((time.time() - t0) * 1000)
        execution_trace.append(ExecutionTraceStep(
            step=step_counter, tool="get_routes_and_geofence", status="done", duration_ms=duration_ms,
            details=f"Computed routes and geofences for {len(candidates)} candidates"
        ))
        results["routes_by_candidate"] = routes_by_candidate
        results["geofence_by_candidate"] = geofence_by_candidate
        step_counter += 1

        # Step 6: Deterministic Risk Engine Evaluation
        t0 = time.time()
        plan.append(PlanStepItem(step=step_counter, tool="compute_risk", params={"candidate_count": len(candidates)}))
        risk_by_candidate = {}
        for cand in candidates:
            w_dict = weather_by_candidate.get(cand.zone_id, {})
            m_dict = marine_by_candidate.get(cand.zone_id, {})
            g_dict = geofence_by_candidate.get(cand.zone_id, {})
            
            # Extract hazard list applicable to candidate
            cand_hazards = hazards
            
            r_result = risk_engine.compute_risk_from_dicts(
                zone_id=cand.zone_id,
                distance_km=cand.distance_km,
                wave_height_m=m_dict.get("wave_height_m", 0.8),
                wind_speed_kmh=w_dict.get("wind_speed_kmh", 12.0),
                hazards=cand_hazards,
                geofence_status=g_dict.get("status", "clear"),
                trip_duration_hours=entities.duration_hours or 6.0
            )
            risk_by_candidate[cand.zone_id] = r_result.model_dump()

        duration_ms = int((time.time() - t0) * 1000)
        execution_trace.append(ExecutionTraceStep(
            step=step_counter, tool="compute_risk", status="done", duration_ms=duration_ms,
            details=f"Evaluated risk scores for {len(candidates)} candidates"
        ))
        results["risk_by_candidate"] = risk_by_candidate

        return PlanOutput(
            session_id=session_id,
            plan=plan,
            execution_trace=execution_trace,
            results=results,
            errors=errors
        )

planner_agent = PlannerAgent()
