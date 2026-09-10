import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.schemas.nlu import NLUInput, NLUOutput, EntityBundle, IntentEnum
from app.schemas.common import LatLon, TimeWindow
from app.agents.llm_client import llm_client

COASTAL_LOCATIONS = {
    "ratnagiri": "Ratnagiri",
    "रत्नागिरी": "Ratnagiri",
    "mumbai": "Mumbai",
    "मुंबई": "Mumbai",
    "bombay": "Mumbai",
    "goa": "Goa",
    "गोवा": "Goa",
    "panaji": "Goa",
    "पणजी": "Goa",
    "mormugao": "Goa",
    "mangalore": "Mangalore",
    "मंगलौर": "Mangalore",
    "kochi": "Kochi",
    "कोच्चि": "Kochi",
    "cochin": "Kochi",
    "veraval": "Veraval",
    "वेरावळ": "Veraval",
    "visakhapatnam": "Visakhapatnam",
    "vizag": "Visakhapatnam",
    "विशाखापट्टनम": "Visakhapatnam",
    "chennai": "Chennai",
    "चेन्नई": "Chennai",
    "malvan": "Malvan",
    "मालवण": "Malvan",
    "alibaug": "Alibaug",
    "अलिबाग": "Alibaug",
    "karwar": "Karwar",
    "कारवार": "Karwar",
    "porbandar": "Porbandar",
    "पोरबंदर": "Porbandar",
    "kanyakumari": "Kanyakumari",
    "कन्याकुमारी": "Kanyakumari",
}

class NLULanguageAgent:
    """
    Stage 1: Intent & Language Understanding (NLU) Agent.
    Parses user input, detects language (en, hi, mr), extracts entities,
    normalizes relative times into absolute ISO dates, and merges prior turn context.
    """

    def process(self, input_data: NLUInput) -> NLUOutput:
        text = input_data.text.strip()
        ref_time_str = input_data.request_timestamp or datetime.now().isoformat()
        
        # 1. Fast, deterministic rule-based extractor (0ms latency, zero LLM quota consumed)
        fast_out = self._rule_based_nlu(text, ref_time_str, input_data.prior_context)
        if fast_out.intent != IntentEnum.OTHER or any(w in text.lower() for w in ["hello", "hi", "hey", "namaste", "who are you", "what can you do"]):
            return fast_out

        # 2. Fallback to LLM for highly complex unstructured queries
        llm_response = self._run_llm_nlu(text, input_data.prior_context)
        if llm_response:
            return llm_response

        return fast_out

    def _run_llm_nlu(self, text: str, prior_context: Optional[Dict[str, Any]]) -> Optional[NLUOutput]:
        system_prompt = (
            "You are the NLU Agent for ORCA, an AI marine conversational intelligence platform. "
            "Analyze the user request and extract language (en, hi, mr), intent, and entities.\n"
            "Supported intents:\n"
            "- 'other' (for greetings like hello/hi, general chatter, capabilities questions, small talk)\n"
            "- 'hazard_alert_check' (asking for hazards, storms, waves, cyclone, lightning, warnings)\n"
            "- 'fishing_trip_planning' (planning a fishing voyage with departure and duration)\n"
            "- 'pfz_lookup' (looking for nearest potential fishing zone)\n"
            "- 'safety_check' (asking if it's safe to venture into the sea)\n"
            "- 'condition_lookup' (asking for weather, sea state, wind, or ocean conditions)\n"
            "- 'chlorophyll_sst_lookup' (asking about SST or chlorophyll)\n"
            "- 'route_planning' (asking for safe coastal routes)\n"
            "Return JSON adhering strictly to: {language, intent, entities: {location_text, date, time_window, duration_hours}}."
        )
        user_prompt = f"User input: {text}\nPrior context: {prior_context}"
        data = llm_client.generate_json(system_prompt, user_prompt)
        if data and "intent" in data and "language" in data:
            try:
                entities_data = data.get("entities", {}) or {}
                time_win = None
                if "time_window" in entities_data and isinstance(entities_data["time_window"], dict):
                    time_win = TimeWindow(**entities_data["time_window"])

                raw_loc = entities_data.get("location_text")
                clean_loc = None
                if raw_loc:
                    clean_loc = COASTAL_LOCATIONS.get(raw_loc.lower().strip(), raw_loc.title())

                # Also detect location from text if LLM missed it
                if not clean_loc:
                    text_lower = text.lower()
                    for k, v in COASTAL_LOCATIONS.items():
                        if k in text_lower:
                            clean_loc = v
                            break

                entities = EntityBundle(
                    location_text=clean_loc,
                    date=entities_data.get("date"),
                    time_window=time_win,
                    duration_hours=entities_data.get("duration_hours")
                )

                intent_val = data["intent"]
                # Safeguard: if intent was not in Enum, default to other
                try:
                    intent_enum = IntentEnum(intent_val)
                except Exception:
                    intent_enum = IntentEnum.OTHER

                return NLUOutput(
                    session_id="llm_session",
                    language=data.get("language", "en"),
                    language_confidence=0.95,
                    intent=intent_enum,
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
            if any(w in text_lower for w in ["उद्या", "समुद्रात", "आहे", "का", "सकाळी", "मच्छीमार"]):
                language = "mr"
            else:
                language = "hi"

        # Intent detection - check domain specific actions first
        if any(kw in text_lower for kw in ["fish", "fishing", "trip", "मासे", "मासेमारी", "मछली", "पकड़ने"]):
            intent = IntentEnum.FISHING_TRIP_PLANNING
        elif any(kw in text_lower for kw in ["hazard", "storm", "cyclone", "warning", "lightning", "alert", "धोका", "खतरा", "तूफान"]):
            intent = IntentEnum.HAZARD_ALERT_CHECK
        elif any(kw in text_lower for kw in ["safe", "safety", "सुरक्षित", "सुरक्षा"]):
            intent = IntentEnum.SAFETY_CHECK
        elif any(kw in text_lower for kw in ["pfz", "nearest zone", "fishing zone"]):
            intent = IntentEnum.PFZ_LOOKUP
        elif any(kw in text_lower for kw in ["chlorophyll", "sst", "surface temp"]):
            intent = IntentEnum.CHLOROPHYLL_SST_LOOKUP
        elif any(kw in text_lower for kw in ["productivity", "declined"]):
            intent = IntentEnum.PRODUCTIVITY_EXPLANATION
        elif any(kw in text_lower for kw in ["what if", "instead"]):
            intent = IntentEnum.FOLLOWUP
        elif re.search(r'\b(hello|hi|hey|namaste|नमस्ते|नमस्कार|who are you|what can you do|talk to me|help me)\b', text_lower):
            intent = IntentEnum.OTHER
        else:
            intent = IntentEnum.OTHER

        # Entity extraction: location
        location_text = None
        for loc_key, loc_val in COASTAL_LOCATIONS.items():
            if loc_key in text_lower:
                location_text = loc_val
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

        # Time window extraction
        time_window = TimeWindow(start="06:00", end="12:00")
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text_lower)
        if time_match:
            hour = int(time_match.group(1))
            if time_match.group(3) == "pm" and hour < 12:
                hour += 12
            start_str = f"{hour:02d}:00"
            end_hour = min(hour + 6, 23)
            time_window = TimeWindow(start=start_str, end=f"{end_hour:02d}:00")

        # Duration extraction (e.g. 12 hrs, 8 hours)
        duration_hours = 6.0
        dur_match = re.search(r'(\d+)\s*(?:hrs?|hours?)', text_lower)
        if dur_match:
            duration_hours = float(dur_match.group(1))

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

        # Clarification check only for explicit trip planning queries missing a location
        needs_clarification = False
        clarification_q = None
        if not location_text and intent in [IntentEnum.FISHING_TRIP_PLANNING, IntentEnum.PFZ_LOOKUP]:
            needs_clarification = True
            if language == "mr":
                clarification_q = "तुम्ही कोणत्या बंदरावरून किंवा स्थानावरून (उदा. मुंबई, गोवा, रत्नागिरी) निघणार आहात?"
            elif language == "hi":
                clarification_q = "आप किस स्थान या बंदरगाह (उदा. मुंबई, गोवा, रत्नागिरी) से प्रस्थान कर रहे हैं?"
            else:
                clarification_q = "Which departure location or coastal port (e.g., Goa, Mumbai, Ratnagiri) are you departing from?"

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
