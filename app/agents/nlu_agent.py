import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.schemas.nlu import NLUInput, NLUOutput, EntityBundle, IntentEnum
from app.schemas.common import LatLon, TimeWindow
from app.agents.llm_client import llm_client

class NLULanguageAgent:
    """
    Stage 1: Intent & Language Understanding (NLU) Agent.
    Parses user input, detects language (en, hi, mr), extracts entities,
    normalizes relative times into absolute ISO dates, and merges prior turn context.
    """

    def process(self, input_data: NLUInput) -> NLUOutput:
        text = input_data.text.strip()
        ref_time_str = input_data.request_timestamp or datetime.now().isoformat()
        
        # 1. Try LLM execution if configured
        llm_response = self._run_llm_nlu(text, input_data.prior_context)
        if llm_response:
            return llm_response

        # 2. Rule-based / Fallback processing
        return self._rule_based_nlu(text, ref_time_str, input_data.prior_context)

    def _run_llm_nlu(self, text: str, prior_context: Optional[Dict[str, Any]]) -> Optional[NLUOutput]:
        system_prompt = (
            "You are the NLU Agent for ORCA, a marine conversational decision platform. "
            "Analyze the user request and extract language (en, hi, mr), intent, and entities.\n"
            "Supported intents: fishing_trip_planning, pfz_lookup, safety_check, condition_lookup, "
            "hazard_alert_check, chlorophyll_sst_lookup, route_planning, productivity_explanation, "
            "geofence_check, followup, other.\n"
            "Return JSON adhering strictly to: {language, intent, entities: {location_text, date, time_window, duration_hours}}."
        )
        user_prompt = f"User input: {text}\nPrior context: {prior_context}"
        data = llm_client.generate_json(system_prompt, user_prompt)
        if data and "intent" in data and "language" in data:
            try:
                entities_data = data.get("entities", {})
                time_win = None
                if "time_window" in entities_data and isinstance(entities_data["time_window"], dict):
                    time_win = TimeWindow(**entities_data["time_window"])

                entities = EntityBundle(
                    location_text=entities_data.get("location_text"),
                    date=entities_data.get("date"),
                    time_window=time_win,
                    duration_hours=entities_data.get("duration_hours")
                )
                return NLUOutput(
                    session_id="llm_session",
                    language=data.get("language", "en"),
                    language_confidence=0.95,
                    intent=IntentEnum(data["intent"]),
                    intent_confidence=0.90,
                    entities=entities
                )
            except Exception as e:
                print(f"[NLU Agent] Failed to parse LLM output: {e}")
        return None

    def _rule_based_nlu(self, text: str, ref_time_str: str, prior_context: Optional[Dict[str, Any]]) -> NLUOutput:
        text_lower = text.lower()
        
        # Language detection (Devanagari script detection for Hindi / Marathi)
        language = "en"
        devanagari_chars = re.findall(r'[\u0900-\u097F]', text)
        if devanagari_chars:
            # Check Marathi specific words (उदा., उद्या, समुद्रात, आहे, का)
            if any(w in text_lower for w in ["उद्या", "समुद्रात", "आहे", "का", "सकाळी", "मच्छीमार"]):
                language = "mr"
            else:
                language = "hi"

        # Intent detection
        intent = IntentEnum.FISHING_TRIP_PLANNING
        if any(kw in text_lower for kw in ["safe", "safety", "सुरक्षित", "खतरा", "सुरक्षा"]):
            intent = IntentEnum.SAFETY_CHECK
        elif any(kw in text_lower for kw in ["nearest pfz", "fishing zone", "pfz", "मछली पकड़ने"]):
            intent = IntentEnum.PFZ_LOOKUP
        elif any(kw in text_lower for kw in ["lightning", "cyclone", "storm", "alert", "बिजली", "तूफान", "इशारा"]):
            intent = IntentEnum.HAZARD_ALERT_CHECK
        elif any(kw in text_lower for kw in ["chlorophyll", "sst", "surface temp"]):
            intent = IntentEnum.CHLOROPHYLL_SST_LOOKUP
        elif any(kw in text_lower for kw in ["why has fish productivity declined", "productivity"]):
            intent = IntentEnum.PRODUCTIVITY_EXPLANATION
        elif any(kw in text_lower for kw in ["what if i leave at", "instead"]):
            intent = IntentEnum.FOLLOWUP

        # Entity extraction: location
        location_text = None
        for loc in ["ratnagiri", "mangalore", "kochi", "veraval", "visakhapatnam", "रत्नागिरी", "मंगलौर", "कोच्चि"]:
            if loc in text_lower:
                location_text = "Ratnagiri" if "ratnagiri" in loc or "रत्नागिरी" in loc else loc.title()
                break

        # Date normalization
        ref_dt = datetime.now()
        try:
            ref_dt = datetime.fromisoformat(ref_time_str)
        except Exception:
            pass

        target_date = ref_dt.strftime("%Y-%m-%d")
        if any(w in text_lower for w in ["tomorrow", "कल", "उद्या"]):
            target_date = (ref_dt + timedelta(days=1)).strftime("%Y-%m-%d")

        # Time window
        time_window = TimeWindow(start="05:00", end="11:00")
        if "7 am" in text_lower or "7:00" in text_lower:
            time_window = TimeWindow(start="07:00", end="13:00")

        duration_hours = 6.0

        # Prior context merge
        if prior_context:
            if not location_text and prior_context.get("location"):
                location_text = prior_context["location"]
            if prior_context.get("date") and "tomorrow" not in text_lower and "कल" not in text_lower and "उद्या" not in text_lower:
                target_date = prior_context["date"]

        entities = EntityBundle(
            location_text=location_text,
            date=target_date,
            time_window=time_window,
            duration_hours=duration_hours
        )

        # Clarification check
        needs_clarification = False
        clarification_q = None
        if not location_text and intent in [IntentEnum.FISHING_TRIP_PLANNING, IntentEnum.SAFETY_CHECK, IntentEnum.PFZ_LOOKUP]:
            needs_clarification = True
            if language == "mr":
                clarification_q = "तुम्ही कोणत्या बंदरावरून किंवा स्थानावरून निघणार आहात?"
            elif language == "hi":
                clarification_q = "आप किस स्थान या बंदरगाह से यात्रा शुरू कर रहे हैं?"
            else:
                clarification_q = "Which departure location or port are you asking about?"

        return NLUOutput(
            session_id="nlu_session",
            language=language,
            language_confidence=0.96,
            intent=intent,
            intent_confidence=0.92,
            entities=entities,
            missing_required_fields=["location_text"] if needs_clarification else [],
            needs_clarification=needs_clarification,
            clarification_question=clarification_q
        )

nlu_agent = NLULanguageAgent()
