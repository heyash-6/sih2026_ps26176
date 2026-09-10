from typing import Dict, Any, Optional
from app.config import settings
from app.schemas.nlu import NLUInput, NLUOutput
from app.schemas.decision import FinalDecisionOutput, CandidatePackage
from app.schemas.marine import PFZCandidate
from app.schemas.weather import WeatherReading, MarineConditions, HazardAlert
from app.schemas.gis import Route, GeofenceResult
from app.schemas.risk import RiskResult
from app.agents.nlu_agent import nlu_agent
from app.agents.planner_agent import planner_agent
from app.agents.decision_agent import decision_agent

class Orchestrator:
    """
    ORCA Master Pipeline Orchestrator.
    Sequences NLU -> Clarification Check -> Planner & Specialist Execution -> Risk Scoring -> Decision Generation.
    """

    def process_query(self, session_id: str, text: str, prior_context: Optional[Dict[str, Any]] = None) -> FinalDecisionOutput:
        # Step 1: Run NLU Agent
        nlu_in = NLUInput(
            session_id=session_id,
            text=text,
            prior_context=prior_context
        )
        nlu_out: NLUOutput = nlu_agent.process(nlu_in)

        # Step 2: Check for clarification short-circuit
        if nlu_out.needs_clarification:
            return FinalDecisionOutput(
                session_id=session_id,
                language=nlu_out.language,
                needs_clarification=True,
                clarification_question=nlu_out.clarification_question,
                explanation_text=nlu_out.clarification_question or "Please provide your departure location.",
                disclaimer=settings.disclaimer_text
            )

        # Step 3: Run Planner Agent (Decomposes, calls specialist tools, evaluates risk)
        plan_out = planner_agent.plan_and_execute(nlu_out)
        res = plan_out.results

        # Step 4: Assemble candidate packages
        raw_candidates = res.get("pfz_candidates", [])
        weather_by_cand = res.get("weather_by_candidate", {})
        marine_by_cand = res.get("marine_by_candidate", {})
        hazards_list = res.get("hazards", [])
        routes_by_cand = res.get("routes_by_candidate", {})
        geofence_by_cand = res.get("geofence_by_candidate", {})
        risk_by_cand = res.get("risk_by_candidate", {})

        candidate_packages = []
        for cand_dict in raw_candidates:
            z_id = cand_dict.get("zone_id", "UNKNOWN")
            
            pfz_obj = PFZCandidate(**cand_dict)
            w_obj = WeatherReading(**weather_by_cand[z_id]) if z_id in weather_by_cand else None
            m_obj = MarineConditions(**marine_by_cand[z_id]) if z_id in marine_by_cand else None
            hz_objs = [HazardAlert(**h) for h in hazards_list]
            r_obj = Route(**routes_by_cand[z_id]) if z_id in routes_by_cand else None
            g_obj = GeofenceResult(**geofence_by_cand[z_id]) if z_id in geofence_by_cand else None
            risk_obj = RiskResult(**risk_by_cand[z_id]) if z_id in risk_by_cand else None

            pkg = CandidatePackage(
                zone_id=z_id,
                pfz=pfz_obj,
                weather=w_obj,
                marine_conditions=m_obj,
                hazards=hz_objs,
                route=r_obj,
                geofence=g_obj,
                risk=risk_obj
            )
            candidate_packages.append(pkg)

        # Step 5: Run Decision & Explanation Agent
        trace_dicts = [t.model_dump() for t in plan_out.execution_trace]
        final_output = decision_agent.decide_and_explain(
            session_id=session_id,
            language=nlu_out.language,
            candidates=candidate_packages,
            execution_trace=trace_dicts,
            user_query=text,
            intent=nlu_out.intent.value,
            location_text=nlu_out.entities.location_text,
            origin_coords=res.get("origin_coords"),
            origin_weather=res.get("origin_weather"),
            origin_marine=res.get("origin_marine"),
            hazards=res.get("hazards", [])
        )

        # Step 6: Persist analysis and route decision into Supabase database
        from app.database.data_pipeline import data_pipeline
        data_pipeline.persist_decision_output(final_output, text, res.get("origin_coords"))

        return final_output

orchestrator = Orchestrator()
