import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.schemas.nlu import NLUInput, NLUOutput, EntityBundle, IntentEnum
from app.schemas.common import LatLon, TimeWindow
from app.agents.llm_client import llm_client

COASTAL_LOCATIONS = {
    # Maharashtra - Konkan
    "sindhudurg": "Malvan",
    "सिंधुदुर्ग": "Malvan",
    "malvan": "Malvan",
    "मालवण": "Malvan",
    "vengurla": "Malvan",
    "वेंगुर्ला": "Malvan",
    "devgad": "Malvan",
    "देवगड": "Malvan",
    "vijaydurg": "Malvan",
    "विजयदुर्ग": "Malvan",
    "ratnagiri": "Ratnagiri",
    "रत्नागिरी": "Ratnagiri",
    "mirya": "Ratnagiri",
    "jaigad": "Ratnagiri",
    "जयगड": "Ratnagiri",
    "guhagar": "Ratnagiri",
    "गुहागर": "Ratnagiri",
    "harnai": "Ratnagiri",
    "हर्णे": "Ratnagiri",
    "dapoli": "Ratnagiri",
    "दापोली": "Ratnagiri",
    "alibaug": "Alibaug",
    "अलिबाग": "Alibaug",
    "raigad": "Alibaug",
    "रायगड": "Alibaug",
    "murud": "Alibaug",
    "मुरुड": "Alibaug",
    "mumbai": "Mumbai",
    "मुंबई": "Mumbai",
    "bombay": "Mumbai",
    "sassoon": "Mumbai",
    "versova": "Mumbai",
    "वर्सोवा": "Mumbai",
    "thane": "Mumbai",
    "ठाणे": "Mumbai",
    "palghar": "Mumbai",
    "पालघर": "Mumbai",
    "dahanu": "Mumbai",
    "डहाणू": "Mumbai",
    "vasai": "Mumbai",
    "वसई": "Mumbai",

    # Goa
    "goa": "Goa",
    "गोवा": "Goa",
    "panaji": "Goa",
    "पणजी": "Goa",
    "mormugao": "Goa",
    "vasco": "Goa",

    # Karnataka
    "karwar": "Karwar",
    "कारवार": "Karwar",
    "mangalore": "Mangalore",
    "मंगलौर": "Mangalore",
    "udupi": "Mangalore",
    "मंगळूर": "Mangalore",
    "malpe": "Mangalore",
    "bhatkal": "Karwar",

    # Kerala
    "kochi": "Kochi",
    "कोच्चि": "Kochi",
    "cochin": "Kochi",
    "kollam": "Kollam",
    "कोल्लम": "Kollam",
    "neendakara": "Kollam",
    "alappuzha": "Kochi",
    "alleppey": "Kochi",
    "kozhikode": "Kochi",
    "calicut": "Kochi",
    "kannur": "Kochi",

    # Tamil Nadu
    "kanyakumari": "Kanyakumari",
    "कन्याकुमारी": "Kanyakumari",
    "tuticorin": "Tuticorin",
    "thoothukudi": "Tuticorin",
    "தூத்துக்குடி": "Tuticorin",
    "nagapattinam": "Nagapattinam",
    "नागपट्टिनम": "Nagapattinam",
    "rameswaram": "Nagapattinam",
    "chennai": "Chennai",
    "चेन्नई": "Chennai",
    "madras": "Chennai",
    "kasimedu": "Chennai",

    # Andhra Pradesh
    "visakhapatnam": "Visakhapatnam",
    "vizag": "Visakhapatnam",
    "विशाखापट्टनम": "Visakhapatnam",
    "kakinada": "Kakinada",
    "काकीनाडा": "Kakinada",
    "machilipatnam": "Kakinada",

    # Odisha
    "paradip": "Paradip",
    "पारादीप": "Paradip",
    "puri": "Paradip",
    "पुरी": "Paradip",
    "gopalpur": "Paradip",

    # West Bengal
    "haldia": "Haldia",
    "हल्दिया": "Haldia",
    "kolkata": "Haldia",
    "digha": "Haldia",
    "दीघा": "Haldia",
    "diamond harbour": "Haldia",

    # Gujarat
    "veraval": "Veraval",
    "वेरावळ": "Veraval",
    "porbandar": "Porbandar",
    "पोरबंदर": "Porbandar",
    "okha": "Okha",
    "ओखा": "Okha",
    "dwarka": "Okha",
    "द्वारका": "Okha",
    "kandla": "Okha",
    "mandvi": "Okha",
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

    def extract_location(self, text: str) -> Optional[str]:
        text_lower = text.lower().strip()
        for loc_key, loc_val in COASTAL_LOCATIONS.items():
            if loc_key in text_lower:
                return loc_val
        return None

    def _is_gibberish(self, text: str) -> bool:
        """
        Carefully detect obvious meaningless / garbled text or typos (e.g. 'abcd', 'asdfgh', 'qwerty123').
        Preserves valid short conversational messages: 'hi', 'hello', 'ok', 'yes', 'no', 'thanks', 'namaste', etc.
        """
        clean = text.strip().lower()
        if not clean:
            return False

        # Valid conversational greetings, affirmatives and short ocean terms
        valid_short_words = {
            "hi", "hello", "hey", "namaste", "नमस्ते", "नमस्कार", "ok", "okay", "yes", "no",
            "thanks", "thank you", "thx", "dhanyawad", "धन्यवाद", "bye", "help", "who are you",
            "what can you do", "good", "bad", "safe", "pfz", "sst", "imd", "incois", "gps", "tide",
            "port", "sea", "wave", "wind", "rain"
        }
        if clean in valid_short_words or any(clean == w for w in valid_short_words):
            return False

        words = clean.split()
        if len(words) > 3:
            return False

        for w in words:
            # Common keyboard walk sequences
            if w in ["abcd", "abcde", "abcdef", "asdf", "asdfg", "asdfgh", "qwerty", "qwerty123", "zxcv", "zxcvb", "1234", "12345", "qwer", "lkjh", "poiuy", "aaaa", "bbbb", "cccc", "zzzz"]:
                return True
            # Latin string with no vowels and length >= 4 (e.g. "zxcvb", "asdfgh", "bcdfgh")
            if re.fullmatch(r'[a-z0-9]+', w):
                vowels = sum(1 for ch in w if ch in 'aeiou')
                if len(w) >= 4 and vowels == 0 and w not in ["pfz", "sst", "gps", "incois", "imd"]:
                    return True
                # Repeated characters >= 3 like "aaaa", "bbbb"
                if re.search(r'(.)\1{2,}', w):
                    return True

        return False

    def _rule_based_nlu(self, text: str, ref_time_str: str, prior_context: Optional[Dict[str, Any]]) -> NLUOutput:
        text_lower = text.lower()
        
        # 1. Strict Language Detection (Devanagari script detection for Hindi vs. Marathi)
        language = "en"
        devanagari_chars = re.findall(r'[\u0900-\u097F]', text)
        if devanagari_chars:
            mr_markers = [
                "उद्या", "समुद्रात", "आहे", "का", "सकाळी", "मच्छीमार", "मासेमारीसाठी",
                "मासेमारी", "मासे", "कसे", "करावे", "नाही", "होय", "सांगा", "माहिती",
                "वारा", "लाटा", "जाणे", "नमस्कार", "माझे", "आपण", "कधी", "बंदरावरून", "स्थान"
            ]
            hi_markers = [
                "क्या", "कल", "सुबह", "मछली", "पकड़ने", "के लिए", "समुद्र", "में",
                "जाना", "सुरक्षित", "है", "तूफान", "हवा", "लहरें", "मौसम", "बताएं",
                "जानकारी", "नमस्ते", "मेरा", "खतरा", "कब", "बंदरगाह", "स्थान"
            ]
            mr_score = sum(1 for w in mr_markers if w in text_lower)
            hi_score = sum(1 for w in hi_markers if w in text_lower)
            if mr_score > hi_score:
                language = "mr"
            elif hi_score > mr_score:
                language = "hi"
            elif any(w in text_lower for w in ["आहे", "का", "सकाळी", "उद्या", "मासेमारी", "जाणे"]):
                language = "mr"
            else:
                language = "hi"

        # 2. Gibberish / Typo Detection (Requirement for obvious meaningless text like 'abcd')
        is_conceptual = False
        if self._is_gibberish(text):
            intent = IntentEnum.GIBBERISH
        else:
            # Check conceptual / ocean science queries first (Requirement 10 & 16)
            is_conceptual = any(kw in text_lower for kw in [
                "what is chlorophyll", "define chlorophyll", "chlorophyll", "क्लोरोफिल",
                "what is sst", "sst", "surface temp", "productivity", "उत्पादकता",
                "upwelling", "thermal front", "plankton", "temperature gradient", "fish productivity"
            ]) and not any(kw in text_lower for kw in ["where to fish", "safe to go", "trip", "can i go", "route"])

            if is_conceptual:
                if any(kw in text_lower for kw in ["productivity", "decrease", "declined", "उत्पादकता"]):
                    intent = IntentEnum.PRODUCTIVITY_EXPLANATION
                else:
                    intent = IntentEnum.CHLOROPHYLL_SST_LOOKUP
            elif any(kw in text_lower for kw in [
                "check best fishing day", "which day is best", "best day", "best fishing day",
                "when will it be best", "when is it best", "compare next days", "next few days",
                "compare days", "कधी जावे", "कोणता दिवस चांगला", "कोणत्या दिवशी", "कब जाना अच्छा",
                "कौन सा दिन अच्छा", "कौन से दिन"
            ]):
                intent = IntentEnum.MULTI_DAY_COMPARISON
            elif any(kw in text_lower for kw in ["fish", "fishing", "trip", "मासे", "मासेमारी", "मछली", "पकड़ने", "पकडणे"]):
                intent = IntentEnum.FISHING_TRIP_PLANNING
            elif any(kw in text_lower for kw in ["hazard", "storm", "cyclone", "warning", "lightning", "alert", "धोका", "खतरा", "तूफान"]):
                intent = IntentEnum.HAZARD_ALERT_CHECK
            elif any(kw in text_lower for kw in ["safe", "safety", "सुरक्षित", "सुरक्षा", "leave", "can i go", "जाणे सुरक्षित"]):
                intent = IntentEnum.SAFETY_CHECK
            elif any(kw in text_lower for kw in ["pfz", "nearest zone", "fishing zone"]):
                intent = IntentEnum.PFZ_LOOKUP
            elif any(kw in text_lower for kw in ["what if", "instead"]):
                intent = IntentEnum.FOLLOWUP
            elif re.search(r'\b(hello|hi|hey|namaste|नमस्ते|नमस्कार|who are you|what can you do|talk to me|help me)\b', text_lower):
                intent = IntentEnum.OTHER
            else:
                intent = IntentEnum.OTHER

        # 3. Location Hierarchy Logic (Requirements 13, 14, 15, 16)
        location_text = None

        # PRIORITY 1: Explicit location mentioned in current user message
        for loc_key, loc_val in COASTAL_LOCATIONS.items():
            if loc_key in text_lower:
                location_text = loc_val
                break

        # If question is conceptual/science (e.g. "What is chlorophyll?"), or gibberish, DO NOT force location!
        if not is_conceptual and intent not in (IntentEnum.OTHER, IntentEnum.GIBBERISH):
            # PRIORITY 2: Selected Port from ORCA session (Req 14)
            if not location_text and prior_context:
                sel_port = prior_context.get("selected_port") or prior_context.get("port_id")
                if sel_port:
                    from app.database.indian_coastal_registry import get_port_by_id
                    p_obj = get_port_by_id(sel_port)
                    location_text = p_obj.get("name", sel_port)

            # PRIORITY 3: Device/User GPS Location from prior_context
            if not location_text and prior_context:
                u_loc = prior_context.get("user_location")
                if u_loc and isinstance(u_loc, dict):
                    location_text = u_loc.get("port_name") or u_loc.get("city") or u_loc.get("port_id")
                elif u_loc and isinstance(u_loc, str):
                    location_text = u_loc

            # PRIORITY 4: Previously established conversation context / memory
            if not location_text and prior_context:
                if prior_context.get("location"):
                    location_text = prior_context["location"]
                elif prior_context.get("session_memory", {}).get("location"):
                    location_text = prior_context["session_memory"]["location"]

        # Clean location name
        if location_text:
            location_text = location_text.replace("Harbour", "").replace("Fishery Port", "").replace("Port", "").strip()

        # 4. Time-Aware Context Extraction (Requirement 18)
        ref_dt = datetime.now()
        try:
            ref_dt = datetime.fromisoformat(ref_time_str)
        except Exception:
            pass

        target_date = ref_dt.strftime("%Y-%m-%d")
        if any(w in text_lower for w in ["tomorrow", "कल", "उद्या"]):
            target_date = (ref_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        elif any(w in text_lower for w in ["next week"]):
            target_date = (ref_dt + timedelta(days=7)).strftime("%Y-%m-%d")

        # Time window extraction (morning, afternoon, evening, night)
        time_window = TimeWindow(start="06:00", end="12:00")
        if any(w in text_lower for w in ["morning", "सकाळी", "सुबह"]):
            time_window = TimeWindow(start="05:00", end="11:00")
        elif any(w in text_lower for w in ["afternoon", "दुपारी", "दोपहर"]):
            time_window = TimeWindow(start="12:00", end="17:00")
        elif any(w in text_lower for w in ["evening", "tonight", "night", "संध्याकाळी", "शाम", "रात"]):
            time_window = TimeWindow(start="18:00", end="23:00")

        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text_lower)
        if time_match:
            hour = int(time_match.group(1))
            if time_match.group(3) == "pm" and hour < 12:
                hour += 12
            start_str = f"{hour:02d}:00"
            end_hour = min(hour + 6, 23)
            time_window = TimeWindow(start=start_str, end=f"{end_hour:02d}:00")

        # Duration extraction
        duration_hours = 6.0
        dur_match = re.search(r'(\d+)\s*(?:hrs?|hours?)', text_lower)
        if dur_match:
            duration_hours = float(dur_match.group(1))

        # Prior context merge & Multi-turn follow-up resolution
        if prior_context:
            if prior_context.get("date") and "tomorrow" not in text_lower and "कल" not in text_lower and "उद्या" not in text_lower:
                target_date = prior_context["date"]

            # If user just responded with a location (e.g. "ratnagiri") after a clarification
            if intent == IntentEnum.OTHER and location_text:
                if prior_context.get("pending_intent"):
                    try:
                        intent = IntentEnum(prior_context["pending_intent"])
                    except Exception:
                        intent = IntentEnum.FISHING_TRIP_PLANNING
                elif prior_context.get("history"):
                    hist = prior_context["history"]
                    for h in reversed(hist):
                        if h.get("role") == "user" and any(k in h.get("text", "").lower() for k in ["fish", "trip", "leave", "depart", "safe", "5am", "weather"]):
                            intent = IntentEnum.FISHING_TRIP_PLANNING
                            break

        entities = EntityBundle(
            location_text=location_text,
            date=target_date,
            time_window=time_window,
            duration_hours=duration_hours
        )

        # PRIORITY 4: Clarification check only if navigation/trip planning query lacks any location
        needs_clarification = False
        clarification_q = None
        if not location_text and intent in [IntentEnum.FISHING_TRIP_PLANNING, IntentEnum.PFZ_LOOKUP] and not is_conceptual:
            needs_clarification = True
            if language == "mr":
                clarification_q = "तुम्ही कोणत्या किनारी भागाची किंवा बंदराची माहिती तपासू इच्छिता? (उदा. मुंबई, रत्नागिरी, मालवण)"
            elif language == "hi":
                clarification_q = "आप किस तटीय क्षेत्र या बंदरगाह की जाँच करना चाहते हैं? (उदा. मुंबई, रत्नागिरी, मालवण)"
            else:
                clarification_q = "Which coastal area or port should I check? (e.g., Mumbai, Ratnagiri, Malvan)"

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
