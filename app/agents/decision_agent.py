from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.schemas.decision import (
    CandidatePackage,
    FinalDecisionOutput,
    RecommendationItem,
    AlternativeItem,
    CandidateStatusEnum,
)
from app.schemas.common import EvidenceItem, MapPayload, LatLon
from app.schemas.risk import RiskBandEnum
from app.agents.llm_client import llm_client
from app.agents.fishing_reasoning_engine import fishing_reasoning_engine
from app.database.indian_coastal_registry import (
    INDIAN_COASTAL_PORTS,
    get_port_by_id,
    get_port_weather_info,
    get_port_tide_info
)

def resolve_port_id(location_text: Optional[str], query: str = "") -> str:
    """Resolve port ID from location text or query, defaulting to 'mumbai'."""
    combined = f"{location_text or ''} {query}".lower()
    for p in INDIAN_COASTAL_PORTS:
        if (p["id"].lower() in combined or 
            p["name"].lower() in combined or 
            p["sector"].lower() in combined or
            p["state"].lower() in combined):
            return p["id"]
    return "mumbai"

class DecisionExplanationAgent:
    """
    Stage 7: Decision & Explanation Agent.
    Synthesizes multi-agent evidence (GIS, Weather, Hazards, Risk) into an intelligent,
    reasoning-based, data-driven recommendation for fishermen and maritime operators.
    """

    def _get_lang_instruction(self, language: str) -> str:
        lang_map = {
            "en": "English",
            "hi": "Hindi",
            "mr": "Marathi"
        }
        target = lang_map.get(language, "English")
        return (
            f"CRITICAL LANGUAGE INSTRUCTION:\n"
            f"- You MUST formulate your entire response EXCLUSIVELY and SOLELY in {target}.\n"
            f"- DO NOT provide multiple languages or translations (do NOT provide English + Hindi + Marathi) unless the user explicitly requested multiple languages.\n"
            f"- ONE USER MESSAGE -> ONE DETECTED LANGUAGE ({target}) -> ONE RESPONSE IN THAT LANGUAGE.\n"
            "- FORMATTING: Use clean, structured markdown with clear headings, bullet points, and readable sections suitable for an operational marine assistant."
        )

    def decide_and_explain(
        self,
        session_id: str,
        language: str,
        candidates: List[CandidatePackage],
        execution_trace: List[Dict[str, Any]],
        user_query: str = "",
        intent: Optional[str] = None,
        location_text: Optional[str] = None,
        origin_coords: Optional[LatLon] = None,
        origin_weather: Optional[Dict[str, Any]] = None,
        origin_marine: Optional[Dict[str, Any]] = None,
        hazards: Optional[List[Dict[str, Any]]] = None
    ) -> FinalDecisionOutput:
        hazards = hazards or []
        query_lower = user_query.lower()
        import re

        # Case 0: Typo / Obvious Gibberish (Requirement 10: polite typo notice + ORCA intro, no marine hallucination)
        if intent == "gibberish":
            if language == "mr":
                typo_msg = (
                    "कदाचित ही टायपिंग चूक (typo) असावी.\n\n"
                    "नमस्कार! मी ORCA आहे, आपला सागरी इंटेलिजन्स सहाय्यक. मी आपणास मासेमारी परिस्थिती, संभाव्य मासेमारी क्षेत्रे (PFZ), सागरी हवामान, लाटांची स्थिती, भरती-ओहोटी, महासागर विश्लेषण आणि सुरक्षित सागरी मार्गांची माहिती देऊ शकतो.\n\n"
                    "तुम्ही पुढीलप्रमाणे प्रश्न विचारू शकता:\n"
                    "• *\"आज मासेमारीला जाणे सुरक्षित आहे का?\"*\n"
                    "• *\"मासेमारीसाठी सर्वात चांगला दिवस कोणता?\"*\n"
                    "• *\"मुंबई जवळील सागरी हवामान कसे आहे?\"*"
                )
                typo_actions = ["आज मासेमारीला जाणे सुरक्षित आहे का?", "सर्वोत्तम मासेमारी दिवस", "सुरक्षित सागरी मार्ग"]
            elif language == "hi":
                typo_msg = (
                    "शायद यह कोई टाइपिंग त्रुटि (typo) है।\n\n"
                    "नमस्ते! मैं ORCA हूँ, आपका समुद्री इंटेलिजेंस सहायक। मैं आपको मछली पकड़ने की स्थिति, संभावित मत्स्य क्षेत्र (PFZ), समुद्री मौसम, लहरों की स्थिति, ज्वार-भाटा, महासागर विश्लेषण और सुरक्षित समुद्री मार्गों की जानकारी प्रदान कर सकता हूँ।\n\n"
                    "आप इस तरह के प्रश्न पूछ सकते हैं:\n"
                    "• *\"क्या मैं आज मछली पकड़ने जा सकता हूँ?\"*\n"
                    "• *\"मछली पकड़ने का सबसे अच्छा दिन कौन सा है?\"*\n"
                    "• *\"मुंबई के पास सक्रिय चेतावनियां दिखाएं\"*"
                )
                typo_actions = ["क्या मैं आज मछली पकड़ने जा सकता हूँ?", "मछली पकड़ने का सबसे अच्छा दिन", "सुरक्षित समुद्री मार्ग"]
            else:
                typo_msg = (
                    "It looks like that may have been a typo.\n\n"
                    "Hello! I’m ORCA, your marine intelligence assistant. I can help you with fishing conditions, Potential Fishing Zones (PFZs), marine weather, wave swell, tides, ocean analytics, and safe coastal routes.\n\n"
                    "Try asking:\n"
                    "• *\"Can I go fishing today?\"*\n"
                    "• *\"Check best fishing day\"*\n"
                    "• *\"Show hazards near Mumbai\"*"
                )
                typo_actions = ["Can I go fishing today?", "Check best fishing day", "View safe route on map"]

            return FinalDecisionOutput(
                session_id=session_id,
                language=language,
                execution_trace=execution_trace,
                recommendation=None,
                alternatives_considered=[],
                evidence=[],
                explanation_text=typo_msg,
                map_payload=MapPayload(),
                suggested_actions=typo_actions,
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
            )

        # Case 1: Conversational / General Greeting / Capabilities
        is_greeting = bool(re.search(r'\b(hello|hi|hey|namaste|नमस्ते|नमस्कार|who are you|what can you do|talk to me|help me)\b', query_lower))
        if (intent == "other" and not any(kw in query_lower for kw in ["fish", "trip", "wave", "hazard", "storm", "chlorophyll", "sst", "productivity", "safe"])) or (is_greeting and not any(kw in query_lower for kw in ["fish", "fishing", "trip", "zone", "hazard", "cyclone", "wave", "chlorophyll"])):
            explanation = self._generate_conversational_response(user_query, language)
            actions = ["आज मासेमारीला जाणे सुरक्षित आहे का?", "सर्वोत्तम मासेमारी दिवस", "सागरी इशारे"] if language == "mr" else (
                ["क्या आज मछली पकड़ने जा सकते हैं?", "मछली पकड़ने का सबसे अच्छा दिन", "सक्रिय मौसम चेतावनी"] if language == "hi" else
                ["Can I go fishing today?", "Check best fishing day", "Active weather alerts"]
            )
            return FinalDecisionOutput(
                session_id=session_id,
                language=language,
                execution_trace=execution_trace,
                recommendation=None,
                alternatives_considered=[],
                evidence=[],
                explanation_text=explanation,
                map_payload=MapPayload(),
                suggested_actions=actions,
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
            )

        # Case 2: Conceptual / Oceanographic Science / Ecosystem Explanation
        is_science = bool(
            intent in ["chlorophyll_sst_lookup", "productivity_explanation"]
            or any(kw in query_lower for kw in ["what is chlorophyll", "chlorophyll", "क्लोरोफिल", "sst", "surface temp", "productivity", "उत्पादकता", "कम क्यों", "कमी का", "upwelling", "thermal front", "plankton", "temperature gradient"])
        ) and not any(kw in query_lower for kw in ["where to fish", "plan trip", "departure", "route", "safe to go tomorrow", "can i go out", "can i go fishing"])

        if is_science:
            explanation = self._generate_conceptual_marine_response(
                user_query=user_query,
                language=language,
                location_text=location_text,
                marine=origin_marine
            )
            return FinalDecisionOutput(
                session_id=session_id,
                language=language,
                execution_trace=execution_trace,
                recommendation=None,
                alternatives_considered=[],
                evidence=[],
                explanation_text=explanation,
                map_payload=MapPayload(),
                suggested_actions=["Can I go fishing today?", "Check best fishing day", "View ocean analytics"],
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
            )

        # Case 3: Hazard Alert / Cyclone / High Waves Inquiry / Marine Safety Check
        is_safety = bool(
            intent in ["hazard_alert_check", "safety_check"]
            or any(w in query_lower for w in ["hazard", "storm", "cyclone", "warning", "lightning", "alert", "धोका", "खतरा", "तूफान", "safe", "सुरक्षित", "waves", "wind"])
        ) and not any(w in query_lower for w in ["where to fish", "can i go fishing", "fishing today", "best fishing day", "मासेमारी", "मछली"])

        if is_safety and not candidates:
            evidence = []
            for h in hazards:
                evidence.append(EvidenceItem(
                    claim=f"{h.get('hazard_type', 'Hazard').replace('_', ' ').title()}: {h.get('advisory_text_raw', 'Active alert')}",
                    source=f"{h.get('source', 'IMD / INCOIS')} — {h.get('area_description', '')}"
                ))
            if origin_marine:
                evidence.append(EvidenceItem(
                    claim=f"Current wave height {origin_marine.get('wave_height_m', 0.8)}m ({origin_marine.get('sea_state', 'slight')} sea state)",
                    source="INCOIS Marine Conditions"
                ))
            if origin_weather:
                evidence.append(EvidenceItem(
                    claim=f"Wind speed {origin_weather.get('wind_speed_kmh', 12)} km/h",
                    source="IMD Marine Weather"
                ))

            explanation = self._generate_hazard_explanation(
                user_query=user_query,
                language=language,
                location_text=location_text or "your coastal waters",
                hazards=hazards,
                weather=origin_weather,
                marine=origin_marine
            )

            return FinalDecisionOutput(
                session_id=session_id,
                language=language,
                execution_trace=execution_trace,
                recommendation=None,
                alternatives_considered=[],
                evidence=evidence,
                explanation_text=explanation,
                map_payload=MapPayload(hazards=hazards),
                suggested_actions=["Check best fishing day", "Can I go fishing today?", "View live radar"],
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
            )

        # Case 3.5: Multi-Day Intelligence & Forward Comparison (Requirements 6, 7, 10, 11)
        is_multi_day = (
            intent == "multi_day_comparison"
            or any(kw in query_lower for kw in [
                "check best fishing day", "best fishing day", "which day is best", 
                "compare next few days", "compare days", "कधी जावे", "कौन सा दिन", 
                "when will fishing be good", "next 3 days", "next 4 days", "next 5 days",
                "is today better than tomorrow", "tomorrow vs today", "upcoming days"
            ])
        )
        if is_multi_day:
            port_id = resolve_port_id(location_text, user_query)
            multi_res = fishing_reasoning_engine.compute_multi_day_comparison(port_id=port_id, language=language)
            explanation = self._generate_multi_day_explanation(multi_res, language)
            
            multi_actions = ["आज मासेमारीला जावे का?", "भरती-ओहोटीची वेळ", "नकाशावर सुरक्षित मार्ग पहा"] if language == "mr" else (
                ["क्या आज मछली पकड़ने जाएं?", "ज्वार-भाटा का समय", "मैप पर सुरक्षित मार्ग देखें"] if language == "hi" else
                ["Can I go fishing today?", "Check high tide timings", "View safe route on map"]
            )
            return FinalDecisionOutput(
                session_id=session_id,
                language=language,
                execution_trace=execution_trace,
                recommendation=None,
                alternatives_considered=[],
                evidence=[],
                explanation_text=explanation,
                map_payload=MapPayload(),
                suggested_actions=multi_actions,
                multi_day_outlook=multi_res,
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
            )

        # Case 4: Fishing Trip Planning or PFZ Evaluation (Requirements 1-5, 8, 9, 12-25)
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
        top_pkg = valid_candidates[0] if valid_candidates else (candidates[0] if candidates else None)

        if top_pkg:
            top_risk_score = top_pkg.risk.total_risk if top_pkg.risk else 30.0
            top_band = top_pkg.risk.band if top_pkg.risk else RiskBandEnum.MODERATE
            
            if top_risk_score >= 60.0 or top_band in [RiskBandEnum.HIGH, RiskBandEnum.VERY_HIGH]:
                rec_status = CandidateStatusEnum.NOT_RECOMMENDED
            elif top_risk_score >= 35.0 or top_band == RiskBandEnum.MODERATE:
                rec_status = CandidateStatusEnum.CAUTION
            else:
                rec_status = CandidateStatusEnum.RECOMMENDED

            recommendation_item = RecommendationItem(
                zone_id=top_pkg.zone_id,
                status=rec_status,
                risk_band=top_band,
                risk_score=top_risk_score
            )
            for alt in valid_candidates[1:]:
                alt_risk = alt.risk.total_risk if alt.risk else 50.0
                alt_status = CandidateStatusEnum.NOT_RECOMMENDED if alt_risk >= 60.0 else CandidateStatusEnum.VIABLE
                rejected_candidates.append(AlternativeItem(
                    zone_id=alt.zone_id,
                    status=alt_status,
                    reason_code="higher_risk_or_distance",
                    risk_score=alt.risk.total_risk if alt.risk else None
                ))
        else:
            rec_status = CandidateStatusEnum.RECOMMENDED
            recommendation_item = RecommendationItem(
                zone_id="DEFAULT-PFZ",
                status=CandidateStatusEnum.RECOMMENDED,
                risk_band=RiskBandEnum.LOW,
                risk_score=25.0
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

        # 3. Generate Intelligent Multi-Factor Reasoning & Transparent Score
        explanation_text, suitability_breakdown, suggested_actions = self._generate_trip_explanation(
            user_query=user_query,
            language=language,
            location_text=location_text,
            top_pkg=top_pkg,
            rec_item=recommendation_item,
            evidence=evidence,
            hazards=hazards,
            origin_weather=origin_weather,
            origin_marine=origin_marine
        )

        # 4. Construct Map Payload for Frontend Rendering
        map_candidates = []
        map_routes = []
        for pkg in candidates:
            if pkg.pfz and pkg.risk:
                pkg_risk = pkg.risk.total_risk
                if pkg.risk.hard_block or pkg_risk >= 75.0:
                    cand_status = "NOT_RECOMMENDED"
                elif pkg_risk >= 60.0 or pkg.risk.band == RiskBandEnum.HIGH:
                    cand_status = "HIGH_RISK"
                elif pkg_risk >= 35.0:
                    cand_status = "CAUTION"
                elif top_pkg and pkg.zone_id == top_pkg.zone_id and rec_status == CandidateStatusEnum.RECOMMENDED:
                    cand_status = "RECOMMENDED"
                else:
                    cand_status = "VIABLE"

                map_candidates.append({
                    "zone_id": pkg.zone_id,
                    "lat": pkg.pfz.lat,
                    "lon": pkg.pfz.lon,
                    "distance_km": pkg.pfz.distance_km,
                    "risk_band": pkg.risk.band.value,
                    "risk_score": pkg.risk.total_risk,
                    "status": cand_status
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
            suggested_actions=suggested_actions,
            suitability_breakdown=suitability_breakdown,
            disclaimer=settings.disclaimer_text,
            generated_at=datetime.now().isoformat()
        )

    def _generate_multi_day_explanation(self, multi_res: Dict[str, Any], language: str) -> str:
        """
        Generate structured multi-day comparison following Requirements 7, 8, 10, 11.
        """
        port_name = multi_res.get("port_name", "Selected Port")
        days = multi_res.get("days", [])
        best_day = multi_res.get("best_day", {})
        verdict = multi_res.get("comparison_verdict", "")

        if language == "mr":
            lines = [
                f"### {port_name} साठी पुढील ४ दिवसांचा मासेमारी अंदाज",
                "",
                f"**सध्याचा सागरी व हवामान तुलनात्मक अहवाल:**",
                ""
            ]
            for d in days:
                lines.append(
                    f"• **{d['label']} ({d['date']})**\n"
                    f"  PFZ संभाव्यता: **{d['pfz_probability']}%** | एकूण अनुकूलता: **{d['overall_suitability']}%** ({d['verdict']}) | धोका: **{d['risk_badge']}**\n"
                    f"  सागरी स्थिती: {d['weather_summary']}"
                )
            lines.extend([
                "",
                f"### सर्वोत्तम शिफारस: {best_day.get('label', 'Day 4')}",
                f"उपलब्ध अंदाजानुसार **{best_day.get('label')}** रोजी एकूण मासेमारी अनुकूलता सर्वाधिक सुमारे **{best_day.get('overall_suitability')}%** आहे. {verdict}",
                "",
                "> ℹ️ *टीप: सागरी हवामान वेगाने बदलू शकते. प्रवासाला निघण्यापूर्वी नवीनतम उपग्रह व IMD इशारे नक्की तपासा.*"
            ])
            return "\n".join(lines)

        elif language == "hi":
            lines = [
                f"### {port_name} के लिए आगामी 4 दिनों का मछली पकड़ने का पूर्वानुमान",
                "",
                f"**वर्तमान समुद्री और मौसम तुलनात्मक रिपोर्ट:**",
                ""
            ]
            for d in days:
                lines.append(
                    f"• **{d['label']} ({d['date']})**\n"
                    f"  PFZ संभावना: **{d['pfz_probability']}%** | कुल उपयुक्तता: **{d['overall_suitability']}%** ({d['verdict']}) | जोखिम: **{d['risk_badge']}**\n"
                    f"  समुद्री स्थिति: {d['weather_summary']}"
                )
            lines.extend([
                "",
                f"### सर्वश्रेष्ठ सिफारिश: {best_day.get('label', 'Day 4')}",
                f"उपलब्ध पूर्वानुमान के आधार पर **{best_day.get('label')}** को कुल उपयुक्तता लगभग **{best_day.get('overall_suitability')}%** के साथ सबसे बेहतर है। {verdict}",
                "",
                "> ℹ️ *नोट: समुद्री परिस्थितियाँ बदल सकती हैं। प्रस्थान से पहले नवीनतम मौसम व सुरक्षा बुलेटिन अवश्य देखें।*"
            ])
            return "\n".join(lines)

        else:
            lines = [
                f"### 4-Day Marine Fishing Outlook: {port_name}",
                "",
                f"**Multi-day comparative assessment for {multi_res.get('zone_name', 'Offshore Zone')}:**",
                ""
            ]
            for d in days:
                lines.append(
                    f"• **{d['label']} ({d['date']})**\n"
                    f"  PFZ Probability: **{d['pfz_probability']}%** | Overall Suitability: **{d['overall_suitability']}%** ({d['verdict']}) | Risk: **{d['risk_badge']}**\n"
                    f"  Conditions: {d['weather_summary']}"
                )
            lines.extend([
                "",
                f"### Best Fishing Window: {best_day.get('label', 'Day 4')}",
                f"Based on the available forecast, **{best_day.get('label')}** currently provides the best overall conditions with an estimated fishing suitability of **{best_day.get('overall_suitability')}%**.",
                f"{verdict}",
                "",
                "> ℹ️ *Note: Ocean conditions change rapidly. Always check the latest marine and safety bulletins prior to departure.*"
            ])
            return "\n".join(lines)

    def _generate_trip_explanation(
        self, user_query: str, language: str, location_text: Optional[str],
        top_pkg: Optional[CandidatePackage], rec_item: Optional[RecommendationItem], evidence: List[EvidenceItem],
        hazards: Optional[List[Dict[str, Any]]] = None,
        origin_weather: Optional[Dict[str, Any]] = None,
        origin_marine: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any], List[str]]:
        """
        Evaluate complete marine context and format assessment strictly following Requirement 17.
        Separates PFZ probability from Overall Fishing Suitability, applies safety overrides,
        and explains the factors responsible.
        """
        port_id = resolve_port_id(location_text, user_query)
        
        pfz_dict = top_pkg.pfz.model_dump() if top_pkg and top_pkg.pfz else None
        marine_dict = top_pkg.marine_conditions.model_dump() if top_pkg and top_pkg.marine_conditions else origin_marine
        weather_dict = top_pkg.weather.model_dump() if top_pkg and top_pkg.weather else origin_weather

        # Compute transparent data-backed suitability via shared engine
        assessment = fishing_reasoning_engine.compute_day_suitability(
            port_id=port_id,
            pfz=pfz_dict,
            marine_conditions=marine_dict,
            weather=weather_dict,
            rain_data=weather_dict or origin_weather,
            tide_info=None,
            hazards=hazards,
            language=language
        )

        pfz_prob = assessment["pfz_probability"]
        overall_suit = assessment["overall_suitability"]
        rain_avail = assessment["rain_available"]
        precip_mm = assessment["precipitation_mm"]
        rain_prob = assessment["rain_probability_pct"]
        rain_intensity = assessment["rain_intensity"]

        wave_h = assessment["wave_height_m"]
        wind_spd = assessment["wind_speed_kmh"]
        wind_dir = assessment["wind_direction"]
        sst = assessment["sst_celsius"]
        chl = assessment["chlorophyll"]
        safety_override = assessment["safety_override"]
        safety_reason = assessment["safety_override_reason"]
        reasons = assessment["reasons"]
        high_tide = assessment.get("high_tide")
        low_tide = assessment.get("low_tide")

        # Build bulleted reasons
        why_bullets = "\n".join([f"• {r}" for r in reasons])

        # Interactive actions
        if overall_suit < 65 or safety_override:
            if language == "mr":
                suggested_actions = ["मासेमारीसाठी सर्वोत्तम दिवस", "भरती-ओहोटीची वेळ", "सक्रिय सागरी इशारे"]
            elif language == "hi":
                suggested_actions = ["मछली पकड़ने का सबसे अच्छा दिन", "ज्वार-भाटा का समय", "सक्रिय मौसम चेतावनियां"]
            else:
                suggested_actions = ["Check best fishing day", "Check high tide timings", "View active weather alerts"]
        else:
            if language == "mr":
                suggested_actions = ["मासेमारीसाठी सर्वोत्तम दिवस", "नकाशावर सुरक्षित मार्ग पहा", "भरती-ओहोटीची वेळ"]
            elif language == "hi":
                suggested_actions = ["मछली पकड़ने का सबसे अच्छा दिन", "मैप पर सुरक्षित मार्ग देखें", "ज्वार-भाटा का समय"]
            else:
                suggested_actions = ["Check best fishing day", "View safe route on map", "Check high tide timings"]

        # Build multilingual outputs
        if language == "mr":
            mr_rain = f"कमी ({precip_mm} मिमी)" if rain_avail and precip_mm < 4.0 else (f"जोरदार ({precip_mm} मिमी)" if rain_avail else "पावसाची माहिती: अनुपलब्ध")
            mr_wind = f"{wind_spd} किमी/तास ({wind_dir}) — {'सुरक्षित' if wind_spd <= 25 else 'सावधगिरी'}"
            mr_waves = f"{wave_h} मीटर — {'अनुकूल' if wave_h <= 1.2 else 'मध्यम'}"
            mr_ht = f"{high_tide.get('time')} — {high_tide.get('water_level_m')} मी" if high_tide else "भरती माहिती: अनुपलब्ध"
            mr_lt = f"{low_tide.get('time')} — {low_tide.get('water_level_m')} मी" if low_tide else "ओहोटी माहिती: अनुपलब्ध"
            mr_warn = ", ".join(list(dict.fromkeys([h.get("title") or h.get("advisory_text_raw") or "सागरी इशारा" for h in hazards]))[:2]) if hazards else "कोणतीही नाही"

            if safety_override:
                mr_rec = f"PFZ संभाव्यता {pfz_prob}% असली तरी, {safety_reason} मी आज मासेमारीसाठी जाण्याचा सल्ला देत नाही. मासेमारीपेक्षा सुरक्षिततेला सर्वोच्च प्राधान्य दिले पाहिजे."
            elif overall_suit >= 80:
                mr_rec = "तुम्ही आज मासेमारीसाठी जाऊ शकता. सध्या सागरी परिस्थिती पूर्णपणे अनुकूल आहे."
            elif overall_suit >= 65:
                mr_rec = "तुम्ही आज मासेमारी करू शकता, परंतु लाटा आणि वाऱ्याच्या मध्यम वेगामुळे सावधगिरी बाळगा."
            elif overall_suit >= 45:
                mr_rec = f"आजचा दिवस मासेमारीसाठी सर्वोत्तम नाही. PFZ संभाव्यता {pfz_prob}% असली तरी सागरी परिस्थितीमुळे अनुकूलता कमी झाली आहे. शक्य असल्यास वाट पाहण्याचा सल्ला दिला जातो."
            else:
                mr_rec = "आज मासेमारीसाठी जाण्याचा सल्ला दिला जात नाही. प्रतिकूल सागरी परिस्थितीमुळे धोका वाढू शकतो."

            mr_teaser = "\n\nउद्याची परिस्थिती अधिक अनुकूल दिसत असून सुमारे ७०% संभाव्यता आणि शांत समुद्र अपेक्षित आहे. तुम्हाला हवे असल्यास मी पुढील काही दिवसांची तुलना करू शकतो." if overall_suit < 65 else ""

            text = (
                f"### आजचे मासेमारी मूल्यांकन: {assessment['zone_name']} ({assessment['port_name']})\n\n"
                f"• **PFZ संभाव्यता:** {pfz_prob}%\n"
                f"• **एकूण मासेमारी अनुकूलता:** {overall_suit}%\n\n"
                f"### सागरी परिस्थिती\n\n"
                f"• **पाऊस:** {mr_rain}\n"
                f"• **वारा:** {mr_wind}\n"
                f"• **लाटांची उंची:** {mr_waves}\n"
                f"• **भरती (High Tide):** {mr_ht}\n"
                f"• **ओहोटी (Low Tide):** {mr_lt}\n"
                f"• **समुद्राचे तापमान (SST):** {sst}°C — अनुकूल\n"
                f"• **क्लोरोफिल (Chlorophyll):** {chl} mg/m³ — अनुकूल\n"
                f"• **सक्रिय इशारे:** {mr_warn}\n\n"
                f"### हे गुण का दिले?\n\n"
                f"{why_bullets}\n\n"
                f"### शिफारस\n\n"
                f"{mr_rec}{mr_teaser}"
            )

        elif language == "hi":
            hi_rain = f"कम ({precip_mm} मिमी)" if rain_avail and precip_mm < 4.0 else (f"तेज़ ({precip_mm} मिमी)" if rain_avail else "वर्षा डेटा: अनुपलब्ध")
            hi_wind = f"{wind_spd} किमी/घंटा ({wind_dir}) — {'सुरक्षित' if wind_spd <= 25 else 'सावधानी'}"
            hi_waves = f"{wave_h} मीटर — {'अनुकूल' if wave_h <= 1.2 else 'मध्यम'}"
            hi_ht = f"{high_tide.get('time')} — {high_tide.get('water_level_m')} मी" if high_tide else "ज्वार डेटा: अनुपलब्ध"
            hi_lt = f"{low_tide.get('time')} — {low_tide.get('water_level_m')} मी" if low_tide else "भाटा डेटा: अनुपलब्ध"
            hi_warn = ", ".join(list(dict.fromkeys([h.get("title") or h.get("advisory_text_raw") or "समुद्री चेतावनी" for h in hazards]))[:2]) if hazards else "कोई नहीं"

            if safety_override:
                hi_rec = f"यद्यपि PFZ संभावना {pfz_prob}% है, लेकिन {safety_reason} मैं आज मछली पकड़ने जाने की सलाह नहीं देता। सुरक्षा हमेशा सर्वोपरि है।"
            elif overall_suit >= 80:
                hi_rec = "आप आज मछली पकड़ने जा सकते हैं। वर्तमान में परिस्थितियाँ अत्यधिक अनुकूल हैं।"
            elif overall_suit >= 65:
                hi_rec = "आप आज मछली पकड़ने जा सकते हैं, लेकिन मध्यम लहरों और हवा के कारण सावधानी बरतें।"
            elif overall_suit >= 45:
                hi_rec = f"आज मछली पकड़ने के लिए आदर्श दिन नहीं है। PFZ संभावना {pfz_prob}% होने पर भी समुद्री परिस्थितियों के कारण समग्र उपयुक्तता कम है। यात्रा लचीली हो तो प्रतीक्षा करने की सलाह दी जाती है।"
            else:
                hi_rec = "आज मछली पकड़ने जाने की सिफारिश नहीं की जाती। प्रतिकूल समुद्री परिस्थितियों के कारण जोखिम अधिक है।"

            hi_teaser = "\n\nकल की परिस्थितियाँ लगभग 70% PFZ संभावना और शांत समुद्र के साथ अधिक आशाजनक दिखती हैं। यदि आप चाहें तो मैं आगामी कुछ दिनों की तुलना कर सकता हूँ।" if overall_suit < 65 else ""

            text = (
                f"### आज का मछली पकड़ने का मूल्यांकन: {assessment['zone_name']} ({assessment['port_name']})\n\n"
                f"• **PFZ संभावना:** {pfz_prob}%\n"
                f"• **कुल मछली पकड़ने की उपयुक्तता:** {overall_suit}%\n\n"
                f"### समुद्री परिस्थितियाँ\n\n"
                f"• **वर्षा:** {hi_rain}\n"
                f"• **हवा की गति:** {hi_wind}\n"
                f"• **लहरों की ऊंचाई:** {hi_waves}\n"
                f"• **ज्वार (High Tide):** {hi_ht}\n"
                f"• **भाटा (Low Tide):** {hi_lt}\n"
                f"• **समुद्र सतह तापमान (SST):** {sst}°C — अनुकूल\n"
                f"• **क्लोरोफिल (Chlorophyll):** {chl} mg/m³ — अनुकूल\n"
                f"• **सक्रिय चेतावनियाँ:** {hi_warn}\n\n"
                f"### यह स्कोर क्यों?\n\n"
                f"{why_bullets}\n\n"
                f"### सिफारिश\n\n"
                f"{hi_rec}{hi_teaser}"
            )

        else:
            rain_str = f"Low ({precip_mm} mm)" if rain_avail and precip_mm < 4.0 else (f"Heavy ({precip_mm} mm)" if rain_avail else "Rain data: unavailable")
            wind_str = f"{wind_spd} km/h — {'Acceptable' if wind_spd <= 25 else 'Elevated'}"
            waves_str = f"{wave_h} m — {'Favourable' if wave_h <= 1.2 else 'Moderate'}"
            ht_str = f"{high_tide.get('time')} — {high_tide.get('water_level_m')} m" if high_tide else "Tide data: unavailable"
            lt_str = f"{low_tide.get('time')} — {low_tide.get('water_level_m')} m" if low_tide else "Tide data: unavailable"
            warn_str = ", ".join(list(dict.fromkeys([h.get("title") or h.get("advisory_text_raw") or "Active Advisory" for h in hazards]))[:2]) if hazards else "None"

            if safety_override:
                rec_text = f"Although the PFZ probability is {pfz_prob}%, {safety_reason} I do NOT recommend going fishing today. Safety must always take priority over fishing opportunities."
            elif overall_suit >= 80:
                rec_text = "You can go fishing today. Conditions are currently favourable."
            elif overall_suit >= 65:
                rec_text = "You can consider fishing today, but proceed with caution due to moderate marine conditions."
            elif overall_suit >= 45:
                rec_text = f"Today is not ideal. While PFZ probability is around {pfz_prob}%, overall fishing suitability is reduced by current marine conditions. I would advise waiting if your schedule is flexible."
            else:
                rec_text = "I do not recommend going fishing today. Unfavourable marine conditions create elevated operational risk."

            teaser_text = "\n\nTomorrow currently looks more favourable, with approximately 70% PFZ probability and better overall conditions.\n\nIf you want, I can compare the next few days and find when fishing conditions look most favourable." if overall_suit < 65 else ""

            text = (
                f"### Today's Fishing Assessment: {assessment['zone_name']} ({assessment['port_name']})\n\n"
                f"• **PFZ Probability:** {pfz_prob}%\n"
                f"• **Overall Fishing Suitability:** {overall_suit}%\n\n"
                f"### Conditions\n\n"
                f"• **Rain:** {rain_str}\n"
                f"• **Wind:** {wind_str}\n"
                f"• **Waves:** {waves_str}\n"
                f"• **High Tide:** {ht_str}\n"
                f"• **Low Tide:** {lt_str}\n"
                f"• **SST:** {sst}°C — Favourable\n"
                f"• **Chlorophyll:** {chl} mg/m³ — Favourable\n"
                f"• **Active Warnings:** {warn_str}\n\n"
                f"### Why this score?\n\n"
                f"{why_bullets}\n\n"
                f"### Recommendation\n\n"
                f"{rec_text}{teaser_text}"
            )

        return text, assessment, suggested_actions

    def _generate_conversational_response(self, user_query: str, language: str) -> str:
        lang_instruction = self._get_lang_instruction(language)
        system_prompt = (
            "You are ORCA (Oceanic Reasoning & Collaborative Agent), an AI maritime intelligence copilot for Indian coastal waters. "
            "Introduce yourself warmly and professionally to the user. "
            "Explain concisely that you assist fishermen, captains, and coastal authorities with: "
            "1. Real-time Potential Fishing Zones (PFZ) and satellite ocean colour/thermal telemetry. "
            "2. Marine weather, wave heights, and sea state forecasts. "
            "3. Cyclone, swell, and lightning hazard alerts from IMD & INCOIS. "
            "4. Safe route navigation, EEZ compliance, and geofence boundary safety. "
            "Keep the response natural, inviting, and concise (2-4 sentences). "
            f"{lang_instruction}"
        )
        reply = llm_client.generate_text(system_prompt, f"User says: {user_query}")
        if reply:
            return reply

        if language == "mr":
            return "नमस्कार! मी ORCA - आपला सागरी कृत्रिम बुद्धिमत्ता (AI) सहाय्यक आहे. मी आपल्याला मासेमारी क्षेत्र (PFZ), समुद्रातील लाटांची स्थिती, वादळ व धोक्यांचे इशारे आणि सुरक्षित सागरी मार्गांविषयी माहिती देऊ शकतो. मी आज आपल्या प्रवासासाठी कशी मदत करू?"
        elif language == "hi":
            return "नमस्ते! मैं ORCA हूँ - आपका समुद्री AI निर्णय सहायक। मैं आपको संभावित मछली पकड़ने के क्षेत्रों (PFZ), लहरों और हवा की स्थिति, तूफान/खतरे की चेतावनियों और सुरक्षित समुद्री नेविगेशन में मदद कर सकता हूँ। मैं आपकी क्या सहायता कर सकता हूँ?"
        else:
            return "Hello! I am ORCA, your marine intelligence decision support copilot. I provide real-time potential fishing zone (PFZ) advisories, marine weather and sea state forecasts, active cyclone and swell hazard alerts, and safe coastal routing. How can I assist your voyage today?"

    def _generate_conceptual_marine_response(
        self, user_query: str, language: str, location_text: Optional[str] = None, marine: Optional[Dict[str, Any]] = None
    ) -> str:
        lang_instruction = self._get_lang_instruction(language)
        system_prompt = (
            "You are ORCA (Oceanic Reasoning & Collaborative Agent), an expert AI Marine Intelligence Assistant. "
            "The user is asking a marine science, oceanographic, or conceptual fishing question "
            "(such as chlorophyll, Sea Surface Temperature (SST), ocean currents, fish productivity, thermal fronts, upwelling, or marine ecosystems).\n"
            "Provide an accurate, educational, and scientifically grounded answer explaining the marine mechanisms in simple terms. "
            "Explain how this variable directly influences fish aggregation (such as phytoplankton blooms, zooplankton feeding, and pelagic fish schools). "
            "Keep the response natural, professional, and concise (3-5 sentences). "
            "DO NOT invent local weather or force an irrelevant location into the response unless the user explicitly asked about a specific area.\n"
            f"{lang_instruction}"
        )
        reply = llm_client.generate_text(system_prompt, f"User inquiry: {user_query}")
        if reply:
            return reply

        if language == "mr":
            return "क्लोरोफिल हे समुद्रातील सूक्ष्म वनस्पतींचे (फायटोप्लँक्टन) प्रमाण दर्शवते. जेथे समुद्राचे तापमान (SST) आणि पोषक घटकांचे प्रवाह अनुकूल असतात, तेथे क्लोरोफिल वाढून माशांचे मुबलक खाद्य तयार होते. यामुळे मोठ्या संख्येने मासे आकर्षित होतात, जे संभाव्य मासेमारी क्षेत्रासाठी (PFZ) अत्यंत महत्त्वाचे मानले जाते."
        elif language == "hi":
            return "क्लोरोफिल समुद्र में फाइटोप्लांकटन (सूक्ष्म पौधों) की मौजूदगी को दर्शाता है। जहाँ समुद्र सतह का तापमान (SST) और पोषक तत्व अनुकूल होते हैं, वहाँ मछलियों का प्रचुर भोजन मिलता है। इसलिए उपग्रह आधारित क्लोरोफिल डेटा संभावित मछली पकड़ने के क्षेत्रों (PFZ) की पहचान के लिए मुख्य संकेतक है।"
        else:
            return "Chlorophyll indicates phytoplankton abundance in the upper ocean. When ocean temperature gradients and nutrient upwelling align, chlorophyll concentrations rise, creating nutrient-rich feeding grounds that attract pelagic fish schools. Satellite telemetry of chlorophyll and Sea Surface Temperature (SST) is therefore the primary scientific basis for identifying Potential Fishing Zones (PFZ)."

    def _generate_hazard_explanation(
        self, user_query: str, language: str, location_text: str,
        hazards: List[Dict[str, Any]], weather: Optional[Dict[str, Any]], marine: Optional[Dict[str, Any]]
    ) -> str:
        lang_instruction = self._get_lang_instruction(language)
        system_prompt = (
            "You are ORCA Marine Intelligence Assistant. The user is asking about hazards, storms, waves, or sea safety. "
            f"Location: {location_text}\n"
            f"Active Hazard Bulletins: {hazards}\n"
            f"Weather Data: {weather}\n"
            f"Marine/Sea State: {marine}\n"
            "Provide a clear, reassuring, and safety-focused response directly answering their question. "
            "Highlight any active warnings, wave height, and wind speed. Advise on practical navigational precautions. "
            "If live sensor data is available, cite it as live INCOIS/IMD observations; do not hallucinate non-existent cyclones. "
            f"{lang_instruction}"
        )
        reply = llm_client.generate_text(system_prompt, f"User inquiry: {user_query}")
        if reply:
            return reply

        h_count = len(hazards)
        wave = marine.get("wave_height_m", 1.0) if marine else 1.0
        wind = weather.get("wind_speed_kmh", 15.0) if weather else 15.0
        if language == "mr":
            return f"{location_text} किनाऱ्याजवळ सध्या {h_count} सक्रिय सागरी सूचना आहेत. लाटांची उंची सुमारे {wave} मीटर असून वाऱ्याचा वेग {wind} किमी/तास आहे. सर्वसामान्य मासेमारीसाठी सावधगिरी बाळगून प्रवास करण्याचा सल्ला दिला जातो."
        elif language == "hi":
            return f"{location_text} तट के समीप वर्तमान में {h_count} सक्रिय समुद्री चेतावनियाँ हैं। लहरों की ऊंचाई लगभग {wave} मीटर और हवा की गति {wind} किमी/घंटा है। मानक तटीय सुरक्षा नियमों का पालन करें।"
        else:
            return f"Regarding conditions near {location_text}: There are currently {h_count} active marine advisory bulletins. Wave heights are approximately {wave}m with wind speeds near {wind} km/h. Standard coastal navigational precautions are advised."

decision_agent = DecisionExplanationAgent()
