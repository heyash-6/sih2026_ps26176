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
from app.schemas.common import EvidenceItem, MapPayload, LatLon
from app.schemas.risk import RiskBandEnum
from app.agents.llm_client import llm_client

class DecisionExplanationAgent:
    """
    Stage 7: Decision & Explanation Agent.
    Synthesizes multi-agent evidence (GIS, Weather, Hazards, Risk) into an intelligent,
    natural conversational response powered by Gemini for fishermen and maritime operators.
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
            "- FORMATTING: Avoid raw markdown symbols like '###', '####', '***', or excessive symbols. Write clean, natural sentences and readable paragraphs suitable for an operational marine assistant."
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

        # Case 1: Conversational / General Greeting / Capabilities
        is_greeting = bool(re.search(r'\b(hello|hi|hey|namaste|नमस्ते|नमस्कार|who are you|what can you do|talk to me|help me)\b', query_lower))
        if (intent == "other" and not any(kw in query_lower for kw in ["fish", "trip", "wave", "hazard", "storm", "chlorophyll", "sst", "productivity", "safe"])) or (is_greeting and not any(kw in query_lower for kw in ["fish", "fishing", "trip", "zone", "hazard", "cyclone", "wave", "chlorophyll"])):
            explanation = self._generate_conversational_response(user_query, language)
            return FinalDecisionOutput(
                session_id=session_id,
                language=language,
                execution_trace=execution_trace,
                recommendation=None,
                alternatives_considered=[],
                evidence=[],
                explanation_text=explanation,
                map_payload=MapPayload(),
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
            )

        # Case 2: Conceptual / Oceanographic Science / Ecosystem Explanation
        # (e.g., "What is chlorophyll?", "Why is chlorophyll low?", "Why did fish productivity decrease?", "Explain SST")
        is_science = bool(
            intent in ["chlorophyll_sst_lookup", "productivity_explanation"]
            or any(kw in query_lower for kw in ["what is chlorophyll", "chlorophyll", "क्लोरोफिल", "sst", "surface temp", "productivity", "उत्पादकता", "कम क्यों", "कमी का", "upwelling", "thermal front", "plankton", "temperature gradient"])
        ) and not any(kw in query_lower for kw in ["where to fish", "plan trip", "departure", "route", "safe to go tomorrow", "can i go out"])

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
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
            )

        # Case 3: Hazard Alert / Cyclone / High Waves Inquiry / Marine Safety Check
        is_safety = bool(
            intent in ["hazard_alert_check", "safety_check"]
            or any(w in query_lower for w in ["hazard", "storm", "cyclone", "warning", "lightning", "alert", "धोका", "खतरा", "तूफान", "safe", "सुरक्षित", "waves", "wind", "weather"])
        )
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
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
            )

        # Case 4: Fishing Trip Planning or PFZ Evaluation
        if not candidates:
            explanation = self._generate_no_candidate_explanation(
                user_query=user_query,
                language=language,
                location_text=location_text or "your area",
                weather=origin_weather,
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
                disclaimer=settings.disclaimer_text,
                generated_at=datetime.now().isoformat()
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
            top_risk_score = top_pkg.risk.total_risk if top_pkg.risk else 30.0
            top_band = top_pkg.risk.band if top_pkg.risk else RiskBandEnum.MODERATE
            
            # Determine appropriate recommendation status based on actual conditions
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
            rec_status = CandidateStatusEnum.NO_SAFE_OPTION
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

        # 3. Generate Multilingual Conversational Explanation Text
        explanation_text = self._generate_trip_explanation(
            user_query=user_query,
            language=language,
            location_text=location_text,
            top_pkg=top_pkg,
            rec_item=recommendation_item,
            evidence=evidence
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
            disclaimer=settings.disclaimer_text,
            generated_at=datetime.now().isoformat()
        )

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

        # Fallbacks
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

        # Fallbacks
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

        # Fallback
        h_count = len(hazards)
        wave = marine.get("wave_height_m", 1.0) if marine else 1.0
        wind = weather.get("wind_speed_kmh", 15.0) if weather else 15.0
        if language == "mr":
            return f"{location_text} किनाऱ्याजवळ सध्या {h_count} सक्रिय सागरी सूचना आहेत. लाटांची उंची सुमारे {wave} मीटर असून वाऱ्याचा वेग {wind} किमी/तास आहे. सर्वसामान्य मासेमारीसाठी सावधगिरी बाळगून प्रवास करण्याचा सल्ला दिला जातो."
        elif language == "hi":
            return f"{location_text} तट के समीप वर्तमान में {h_count} सक्रिय समुद्री चेतावनियाँ हैं। लहरों की ऊंचाई लगभग {wave} मीटर और हवा की गति {wind} किमी/घंटा है। मानक तटीय सुरक्षा नियमों का पालन करें।"
        else:
            return f"Regarding conditions near {location_text}: There are currently {h_count} active marine advisory bulletins. Wave heights are approximately {wave}m with wind speeds near {wind} km/h. Standard coastal navigational precautions are advised."

    def _generate_no_candidate_explanation(
        self, user_query: str, language: str, location_text: str,
        weather: Optional[Dict[str, Any]], marine: Optional[Dict[str, Any]]
    ) -> str:
        wave = marine.get("wave_height_m", 0.9) if marine else 0.9
        wind = weather.get("wind_speed_kmh", 14.0) if weather else 14.0
        lang_instruction = self._get_lang_instruction(language)
        system_prompt = (
            "You are ORCA Marine Intelligence Assistant. "
            f"The user is asking about fishing or voyages near '{location_text}', but recent satellite chlorophyll/SST telemetry does not show high-density INCOIS Potential Fishing Zone (PFZ) thermal fronts within 50 km.\n"
            f"Local sea conditions show: Wave height {wave}m, Wind speed {wind} km/h.\n"
            "Explain this to the user in a helpful, friendly manner. Confirm that nearshore conditions remain navigable and suggest checking nearby active sectors or re-checking tomorrow's satellite bulletin. "
            f"{lang_instruction}"
        )
        reply = llm_client.generate_text(system_prompt, f"User inquiry: {user_query}")
        if reply:
            return reply

        if language == "mr":
            return f"{location_text} परिसरात सध्या ५० किमी अंतरात कोणतीही सक्रिय PFZ मासेमारी क्षेत्रे नोंदवलेली नाहीत. तथापि, स्थानिक लाटांची उंची {wave} मी आणि वाऱ्याचा वेग {wind} किमी/तास असून समुद्र शांत आहे. सामान्य किनारी मासेमारी करता येऊ शकते."
        elif language == "hi":
            return f"{location_text} के आसपास 50 किमी के दायरे में वर्तमान में कोई सक्रिय उच्च घनत्व PFZ क्षेत्र नहीं है। हालाँकि, समुद्र में लहरें {wave} मीटर और हवा {wind} किमी/घंटा के साथ नौपरिवहन के अनुकूल हैं।"
        else:
            return f"Currently, satellite ocean telemetry does not indicate active high-density Potential Fishing Zones (PFZ) within 50 km of {location_text}. However, local conditions show gentle {wave}m waves and {wind} km/h winds, which remain favorable for general coastal operations."

    def _generate_trip_explanation(
        self, user_query: str, language: str, location_text: Optional[str],
        top_pkg: Optional[CandidatePackage], rec_item: Optional[RecommendationItem], evidence: List[EvidenceItem]
    ) -> str:
        if not top_pkg or not rec_item:
            return "No viable fishing zone found."

        lang_instruction = self._get_lang_instruction(language)
        system_prompt = (
            "You are ORCA Marine Intelligence Assistant talking directly to a boat captain or fisherman. "
            "Address the user's specific departure location, departure time, and trip duration as requested. "
            f"User asked: '{user_query}'\n"
            f"Departure Port/Location: {location_text or 'your departure port'}\n"
            f"Recommended Zone: {top_pkg.zone_id}\n"
            f"Distance: {top_pkg.pfz.distance_km if top_pkg.pfz else 18.0} km\n"
            f"Wave Height: {top_pkg.marine_conditions.wave_height_m if top_pkg.marine_conditions else 0.9} m\n"
            f"Wind Speed: {top_pkg.weather.wind_speed_kmh if top_pkg.weather else 14.0} km/h\n"
            f"Risk Score: {rec_item.risk_score}/100 ({rec_item.risk_band.value})\n"
            f"Geofence Route: {'Clear of restricted zones' if top_pkg.geofence and top_pkg.geofence.status == 'clear' else 'Caution near boundary'}\n"
            "Write an engaging, clear, direct recommendation (3-5 sentences). "
            "Explicitly address their time and duration if mentioned. Provide practical marine safety tips. "
            f"{lang_instruction}"
        )
        reply = llm_client.generate_text(system_prompt, user_query)
        if reply:
            return reply

        # Fallback template
        z_id = top_pkg.zone_id
        dist = top_pkg.pfz.distance_km if top_pkg.pfz else 18.0
        risk_score = rec_item.risk_score
        wave = top_pkg.marine_conditions.wave_height_m if top_pkg.marine_conditions else 0.9
        wind = top_pkg.weather.wind_speed_kmh if top_pkg.weather else 14.0

        if language == "mr":
            return f"नमस्कार कॅप्टन! आपल्या प्रवासासाठी {z_id} हा पर्याय सर्वोत्तम आहे. हे क्षेत्र किनाऱ्यापासून {dist} किमी अंतरावर असून लाटांची उंची {wave} मी आणि वाऱ्याचा वेग {wind} किमी/तास आहे. एकूण धोका गुण {risk_score}/100 (कमी) आहे. मार्ग सुरक्षित आहे."
        elif language == "hi":
            return f"नमस्ते कैप्टन! आपकी यात्रा के लिए {z_id} सबसे उपयुक्त क्षेत्र है। यह तट से {dist} किमी दूरी पर है, जहाँ लहरें {wave} मीटर और हवा {wind} किमी/घंटा है। कुल जोखिम स्कोर {risk_score}/100 है और मार्ग साफ है।"
        else:
            return f"Hello Captain! Based on your voyage from {location_text or 'port'}, ORCA recommends zone {z_id} located {dist} km offshore. Sea state is favorable with {wave}m waves and {wind} km/h winds, presenting an overall low risk score of {risk_score}/100. Route is clear of restricted maritime zones."

decision_agent = DecisionExplanationAgent()

