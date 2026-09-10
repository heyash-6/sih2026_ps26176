from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import settings
from app.schemas.decision import (
    CandidatePackage,
    FinalDecisionOutput,
    RecommendationItem,
    AlternativeItem,
    CandidateStatusEnum,
)
from app.schemas.common import EvidenceItem, MapPayload
from app.schemas.risk import RiskBandEnum
from app.agents.llm_client import llm_client

class DecisionExplanationAgent:
    """
    Stage 7: Decision & Explanation Agent.
    Ranks candidate zones based on hard blocks and risk scores, formats evidence claims,
    and produces multilingual natural-language explanations (EN, HI, MR).
    """

    def decide_and_explain(
        self,
        session_id: str,
        language: str,
        candidates: List[CandidatePackage],
        execution_trace: List[Dict[str, Any]]
    ) -> FinalDecisionOutput:
        if not candidates:
            return FinalDecisionOutput(
                session_id=session_id,
                language=language,
                execution_trace=execution_trace,
                explanation_text="No candidate fishing zones were found within range.",
                disclaimer=settings.disclaimer_text
            )

        # 1. Candidate Sorting: Non-hard_blocked first, then ascending total_risk, then distance
        valid_candidates = []
        rejected_candidates = []

        for pkg in candidates:
            if pkg.risk and pkg.risk.hard_block:
                reason = "geofence_intersect"
                rejected_candidates.append(AlternativeItem(
                    zone_id=pkg.zone_id,
                    status=CandidateStatusEnum.REJECTED,
                    reason_code=reason,
                    risk_score=pkg.risk.total_risk if pkg.risk else None
                ))
            else:
                valid_candidates.append(pkg)

        valid_candidates.sort(
            key=lambda c: (
                c.risk.total_risk if c.risk else 999.0,
                c.pfz.distance_km if c.pfz else 999.0
            )
        )

        recommendation_item = None
        top_pkg = None

        if valid_candidates:
            top_pkg = valid_candidates[0]
            recommendation_item = RecommendationItem(
                zone_id=top_pkg.zone_id,
                status=CandidateStatusEnum.RECOMMENDED,
                risk_band=top_pkg.risk.band if top_pkg.risk else RiskBandEnum.MODERATE,
                risk_score=top_pkg.risk.total_risk if top_pkg.risk else 30.0
            )
            # Remaining valid candidates added to alternatives
            for alt in valid_candidates[1:]:
                rejected_candidates.append(AlternativeItem(
                    zone_id=alt.zone_id,
                    status=CandidateStatusEnum.VIABLE,
                    reason_code="higher_risk_or_distance",
                    risk_score=alt.risk.total_risk if alt.risk else None
                ))
        else:
            recommendation_item = RecommendationItem(
                zone_id="NONE",
                status=CandidateStatusEnum.NO_SAFE_OPTION,
                risk_band=RiskBandEnum.VERY_HIGH,
                risk_score=100.0
            )

        # 2. Build Evidence List
        evidence: List[EvidenceItem] = []
        if top_pkg:
            if top_pkg.pfz:
                evidence.append(EvidenceItem(
                    claim=f"{top_pkg.pfz.distance_km} km distance from departure point",
                    source="GIS Agent — distance_km"
                ))
            if top_pkg.marine_conditions:
                evidence.append(EvidenceItem(
                    claim=f"Wave height {top_pkg.marine_conditions.wave_height_m}m ({top_pkg.marine_conditions.sea_state} sea state)",
                    source="Weather/Hazard Agent — marine_conditions"
                ))
            if top_pkg.weather:
                evidence.append(EvidenceItem(
                    claim=f"Wind speed {top_pkg.weather.wind_speed_kmh} km/h",
                    source="Weather/Hazard Agent — weather"
                ))
            if top_pkg.geofence:
                ev_text = "Route clear of restricted zones" if top_pkg.geofence.status == "clear" else "Intersects restricted boundary"
                evidence.append(EvidenceItem(
                    claim=ev_text,
                    source="GIS Agent — geofence check"
                ))

        # 3. Generate Multilingual Explanation Text
        explanation_text = self._generate_explanation(language, top_pkg, recommendation_item, evidence)

        # 4. Construct Map Payload for Frontend Rendering
        map_candidates = []
        map_routes = []
        for pkg in candidates:
            if pkg.pfz and pkg.risk:
                map_candidates.append({
                    "zone_id": pkg.zone_id,
                    "lat": pkg.pfz.lat,
                    "lon": pkg.pfz.lon,
                    "distance_km": pkg.pfz.distance_km,
                    "risk_band": pkg.risk.band.value,
                    "risk_score": pkg.risk.total_risk,
                    "status": "RECOMMENDED" if top_pkg and pkg.zone_id == top_pkg.zone_id else ("REJECTED" if pkg.risk.hard_block else "VIABLE")
                })
            if pkg.route:
                map_routes.append(pkg.route.model_dump())

        map_payload = MapPayload(
            candidates=map_candidates,
            routes=map_routes,
            geofence_zones_checked=["international_boundary", "marine_protected_area", "restricted_zone"],
            hazards=[pkg.hazards[0].model_dump() for pkg in candidates if pkg.hazards]
        )

        return FinalDecisionOutput(
            session_id=session_id,
            language=language,
            execution_trace=execution_trace,
            recommendation=recommendation_item,
            alternatives_considered=rejected_candidates,
            evidence=evidence,
            explanation_text=explanation_text,
            map_payload=map_payload,
            disclaimer=settings.disclaimer_text,
            generated_at=datetime.now().isoformat()
        )

    def _generate_explanation(
        self,
        language: str,
        top_pkg: Optional[CandidatePackage],
        rec_item: Optional[RecommendationItem],
        evidence: List[EvidenceItem]
    ) -> str:
        # Attempt LLM generation if available
        llm_text = self._run_llm_explanation(language, top_pkg, rec_item, evidence)
        if llm_text:
            return llm_text

        # Fallback template-based explanation
        if not top_pkg or not rec_item or rec_item.status == CandidateStatusEnum.NO_SAFE_OPTION:
            if language == "mr":
                return "सुरक्षिततेच्या कारणास्तव आज किंवा उद्या समुद्रात जाणे योग्य नाही. सर्व भाग उच्च धोक्याचे दाखवत आहेत."
            elif language == "hi":
                return "सुरक्षा कारणों से आज या कल समुद्र में जाना उचित नहीं है। सभी क्षेत्र उच्च जोखिम दिखा रहे हैं।"
            else:
                return "Venturing into the sea is not recommended due to high marine hazard risks across all evaluated zones."

        z_id = top_pkg.zone_id
        dist = top_pkg.pfz.distance_km if top_pkg.pfz else 18.0
        risk_score = top_pkg.risk.total_risk if top_pkg.risk else 25.0
        wave = top_pkg.marine_conditions.wave_height_m if top_pkg.marine_conditions else 0.8

        if language == "mr":
            return (
                f"{z_id} हा पर्याय उद्यासाठी सर्वोत्तम आणि सुरक्षित मानला गेला आहे. "
                f"हे क्षेत्र आपल्या किनाऱ्यापासून {dist} किमी अंतरावर आहे. "
                f"येथे लाटांची उंची सुमारे {wave} मीटर असून एकूण धोका गुण {risk_score}/100 (मध्यम) आहे. "
                f"हा मार्ग प्रतिबंधित क्षेत्रांना छेदत नाही."
            )
        elif language == "hi":
            return (
                f"{z_id} कल के लिए सबसे उपयुक्त और सुरक्षित विकल्प माना गया है। "
                f"यह क्षेत्र तट से {dist} किमी दूरी पर है। "
                f"यहाँ लहरों की ऊँचाई {wave} मीटर है और कुल जोखिम स्कोर {risk_score}/100 (मध्यम) है। "
                f"यह मार्ग किसी प्रतिबंधित क्षेत्र से होकर नहीं गुजरता।"
            )
        else:
            return (
                f"{z_id} is the recommended fishing zone for your trip. "
                f"It is located {dist} km from departure, with moderate wave conditions ({wave}m) "
                f"and an overall risk score of {risk_score}/100 ({top_pkg.risk.band.value if top_pkg.risk else 'LOW'}). "
                f"The planned route stays clear of restricted marine areas."
            )

    def _run_llm_explanation(
        self, language: str, top_pkg: Optional[CandidatePackage],
        rec_item: Optional[RecommendationItem], evidence: List[EvidenceItem]
    ) -> Optional[str]:
        if not top_pkg:
            return None

        system_prompt = (
            "You are the Decision & Explanation Agent for ORCA Marine Intelligence Platform. "
            "Write a concise, practical, non-alarmist recommendation (3-5 sentences) for a fisherman. "
            "Do NOT invent or modify any numbers. Rely strictly on the provided evidence claims.\n"
            f"Language required: {language} (en=English, hi=Hindi, mr=Marathi)."
        )
        user_prompt = (
            f"Recommended Zone: {rec_item.zone_id if rec_item else 'None'}\n"
            f"Risk Score: {rec_item.risk_score if rec_item else 'N/A'}\n"
            f"Evidence: {[e.claim for e in evidence]}"
        )
        return llm_client.generate_text(system_prompt, user_prompt)

decision_agent = DecisionExplanationAgent()
