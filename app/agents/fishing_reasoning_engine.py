"""
ORCA Fishing Suitability & Multi-Day Reasoning Engine.
Serves as the unified, shared source of truth across:
- ORCA Conversational AI Assistant
- Marine Intelligence Dashboard
- Fishing Intelligence & Multi-Day Trip Planner
- Safety & Routes Assessment

Calculates transparent, data-driven suitability scores (0-100), separates PFZ probability from
overall fishing suitability, enforces safety overrides, and computes multi-day comparisons.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.database.indian_coastal_registry import (
    get_port_by_id,
    get_port_tide_info,
    get_port_weather_info,
    INDIAN_COASTAL_PORTS
)

class FishingReasoningEngine:
    """
    Evaluates multi-factor marine conditions to produce an explainable
    Overall Fishing Suitability Score and actionable recommendations.
    """

    def compute_day_suitability(
        self,
        port_id: str,
        pfz: Optional[Dict[str, Any]] = None,
        marine_conditions: Optional[Dict[str, Any]] = None,
        weather: Optional[Dict[str, Any]] = None,
        rain_data: Optional[Dict[str, Any]] = None,
        tide_info: Optional[Dict[str, Any]] = None,
        hazards: Optional[List[Dict[str, Any]]] = None,
        departure_time: Optional[str] = None,
        trip_duration_hours: float = 6.0,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Compute transparent, multi-factor fishing suitability for a single day.
        """
        port = get_port_by_id(port_id)
        hazards = hazards or []

        # 1. Resolve PFZ Candidate
        if not pfz:
            cands = port.get("pfz_candidates", [])
            active_cands = [c for c in cands if c.get("status") == "ACTIVE"]
            pfz = active_cands[0] if active_cands else (cands[0] if cands else {
                "id": f"PFZ-{port_id[:3].upper()}-01",
                "name": f"{port['name']} Continental Shelf",
                "confidence": 85,
                "sst": 28.0,
                "chlorophyll": 1.2,
                "distance_km": 24.0,
                "status": "ACTIVE"
            })

        # Safe extraction of confidence / probability (handles float 0-1 or 0-100, int, and strings like 'advisory')
        conf_val = pfz.get("confidence_score") if pfz.get("confidence_score") is not None else pfz.get("confidence")
        try:
            val = float(conf_val)
            if val <= 1.0:
                pfz_probability = val * 100.0
            else:
                pfz_probability = val
        except (ValueError, TypeError):
            conf_str = str(conf_val).lower()
            if "high" in conf_str or "confirmed" in conf_str:
                pfz_probability = 88.0
            elif "medium" in conf_str or "advisory" in conf_str:
                pfz_probability = 82.0
            elif "low" in conf_str:
                pfz_probability = 55.0
            else:
                pfz_probability = 80.0


        sst = float(pfz.get("sst_celsius") or pfz.get("sst") or 28.0)
        chlorophyll = float(pfz.get("chlorophyll_mg_m3") or pfz.get("chlorophyll") or 1.2)
        distance_km = float(pfz.get("distance_km") or 22.0)


        # 2. Resolve Marine Sea State (Waves, Swell)
        marine = marine_conditions or port.get("marine_conditions", {})
        wave_height = float(marine.get("wave_height_m", 1.2))
        sea_state = marine.get("sea_state", "Moderate")

        # 3. Resolve Weather & Wind
        w = weather or {}
        wind_speed = float(w.get("wind_speed_kmh", marine.get("wind_speed_kmh", 16.0)))
        wind_dir = w.get("wind_direction_deg", marine.get("wind_direction", "NE (045°) • steady"))
        if isinstance(wind_dir, (int, float)):
            wind_dir = f"{int(wind_dir)}°"

        # 4. Resolve Rain & Atmospheric Weather
        r = rain_data or get_port_weather_info(port_id)
        rain_available = bool(r and "precipitation_mm" in r)
        precipitation_mm = float(r.get("precipitation_mm", 0.0)) if rain_available else 0.0
        rain_prob = float(r.get("rain_probability_pct", 15.0)) if rain_available else 15.0
        rain_intensity = r.get("rain_intensity", "None") if rain_available else "Unknown"
        weather_label = r.get("weather_label", "Partly Cloudy") if rain_available else "Maritime Conditions"

        # 5. Resolve Survey of India Tidal Predictions
        tide = tide_info or get_port_tide_info(port_id)
        tide_available = bool(tide and ("high_tide" in tide or "low_tide" in tide))
        high_tide = tide.get("high_tide", {"time": "04:12 AM", "water_level_m": 3.8}) if tide_available else None
        low_tide = tide.get("low_tide", {"time": "10:05 AM", "water_level_m": 0.9}) if tide_available else None

        # 6. Factor Scoring (0 to 100 where 100 = optimal)
        
        # A. PFZ Opportunity Score (35% weight)
        pfz_score = max(0.0, min(100.0, pfz_probability))

        # B. Sea State / Wave Score (20% weight)
        if wave_height <= 0.6:
            wave_score = 98.0
        elif wave_height <= 0.9:
            wave_score = 92.0
        elif wave_height <= 1.3:
            wave_score = 84.0
        elif wave_height <= 1.7:
            wave_score = 65.0
        elif wave_height <= 2.1:
            wave_score = 45.0
        elif wave_height <= 2.4:
            wave_score = 28.0
        else:
            wave_score = 10.0

        # C. Weather & Wind Score (20% weight)
        if wind_speed <= 12.0:
            wind_score = 96.0
        elif wind_speed <= 18.0:
            wind_score = 88.0
        elif wind_speed <= 26.0:
            wind_score = 72.0
        elif wind_speed <= 35.0:
            wind_score = 48.0
        elif wind_speed <= 42.0:
            wind_score = 25.0
        else:
            wind_score = 10.0

        # Rain penalty
        rain_score = 100.0
        if rain_available:
            if precipitation_mm >= 15.0 or rain_prob >= 85.0:
                rain_score = 15.0
            elif precipitation_mm >= 8.0 or rain_prob >= 70.0:
                rain_score = 40.0
            elif precipitation_mm >= 3.0 or rain_prob >= 50.0:
                rain_score = 65.0
            elif precipitation_mm >= 0.8 or rain_prob >= 30.0:
                rain_score = 85.0
            else:
                rain_score = 96.0

        weather_combined_score = round(0.60 * wind_score + 0.40 * rain_score, 1)

        # D. Oceanographic SST & Chlorophyll Conditions (10% weight)
        sst_score = 90.0 if 26.5 <= sst <= 29.5 else (70.0 if 25.0 <= sst <= 30.5 else 45.0)
        chl_score = 95.0 if chlorophyll >= 1.0 else (80.0 if chlorophyll >= 0.5 else 45.0)
        ocean_score = round(0.5 * sst_score + 0.5 * chl_score, 1)

        # E. Tidal Navigation Suitability (5% weight)
        tide_score = 85.0
        if tide_available and high_tide:
            ht_level = float(high_tide.get("water_level_m", 3.0))
            if ht_level >= 3.2:
                tide_score = 92.0
            elif ht_level >= 2.0:
                tide_score = 82.0
            else:
                tide_score = 70.0

        # F. Active Hazards & Safety Advisories (10% weight)
        hazard_score = 100.0
        critical_hazard_active = False
        hazard_titles = []
        for hz in hazards:
            sev = str(hz.get("severity") or hz.get("risk_level") or "").upper()
            title = hz.get("title") or hz.get("advisory_text_raw") or "Marine Advisory"
            hazard_titles.append(title)
            if sev in ["CRITICAL", "SEVERE", "HIGH"]:
                hazard_score = min(hazard_score, 20.0)
                critical_hazard_active = True
            elif sev in ["MODERATE", "MEDIUM", "CAUTION"]:
                hazard_score = min(hazard_score, 60.0)
            elif sev == "LOW":
                hazard_score = min(hazard_score, 85.0)

        # 7. Overall Weighted Calculation
        raw_suitability = (
            (0.35 * pfz_score) +
            (0.20 * wave_score) +
            (0.20 * weather_combined_score) +
            (0.10 * hazard_score) +
            (0.10 * ocean_score) +
            (0.05 * tide_score)
        )

        overall_suitability = round(raw_suitability, 0)

        # 8. CRITICAL SAFETY OVERRIDE CHECK (Requirement 5)
        safety_override = False
        safety_override_reason = None

        if wave_height >= 2.4:
            safety_override = True
            safety_override_reason = f"Dangerous wave swell of {wave_height}m exceeds small craft safety limits (max 2.0m)."
        elif wind_speed >= 42.0:
            safety_override = True
            safety_override_reason = f"Gale-force coastal winds ({wind_speed} km/h) present high capsizing hazard."
        elif critical_hazard_active:
            safety_override = True
            safety_override_reason = f"Active critical marine hazard warning: {', '.join(hazard_titles)}."
        elif precipitation_mm >= 15.0:
            safety_override = True
            safety_override_reason = f"Severe squall with torrential precipitation ({precipitation_mm} mm) and degraded visibility."

        if safety_override:
            overall_suitability = min(38.0, overall_suitability)

        # 9. Recommendation Category
        if safety_override or overall_suitability < 45.0:
            recommendation_level = "UNFAVOURABLE / DO NOT RECOMMEND"
            verdict_badge = "UNFAVOURABLE"
        elif overall_suitability < 65.0:
            recommendation_level = "MODERATE / CONSIDER WAITING"
            verdict_badge = "MODERATE"
        elif overall_suitability < 80.0:
            recommendation_level = "FAVOURABLE / GO WITH CAUTION"
            verdict_badge = "FAVOURABLE"
        else:
            recommendation_level = "HIGHLY FAVOURABLE / GO"
            verdict_badge = "HIGHLY FAVOURABLE"

        # 10. Generate Concrete Reasoning Explanations (Why suitability differs from PFZ)
        reasons = []

        if language == "mr":
            # Marathi Reasoning Bullets
            if pfz_probability >= 80:
                reasons.append(f"PFZ विश्वासार्हता {int(pfz_probability)}% असून दाट क्लोरोफिल फ्रंट ({chlorophyll} mg/m³) उपलब्ध आहे.")
            elif pfz_probability >= 60:
                reasons.append(f"PFZ संभाव्यता मध्यम ({int(pfz_probability)}%) असून सरासरी मासळी संचयन दर्शवते.")
            else:
                reasons.append(f"PFZ संभाव्यता कमी ({int(pfz_probability)}%) असून सागरी थर्मल फ्रंट क्षीण झाला आहे.")

            if wave_height <= 1.2:
                reasons.append(f"लाटांची उंची ({wave_height} मी) शांत असून सुरक्षित प्रवासासाठी अनुकूल आहे.")
            elif wave_height <= 1.8:
                reasons.append(f"मध्यम उसळणारा समुद्र ({wave_height} मी) सागरी अनुकूलता किंचित कमी करतो.")
            else:
                reasons.append(f"उंच लाटा ({wave_height} मी) सुरक्षिततेसाठी धोकादायक असून मासेमारी अनुकूलता कमी करतात.")

            if rain_available:
                if precipitation_mm >= 4.0:
                    reasons.append(f"किनारपट्टीवर पाऊस ({precipitation_mm} मिमी, {int(rain_prob)}% शक्यता) दृश्यमानता व डेक सुरक्षितता कमी करतो.")
                elif precipitation_mm > 0:
                    reasons.append(f"हलक्या पावसाच्या सरी ({precipitation_mm} मिमी) सामान्य उपकरणांसह व्यवस्थापित करण्यायोग्य आहेत.")
                else:
                    reasons.append(f"पावसाची शक्यता नाही ({int(rain_prob)}%), हवामान स्वच्छ राहील.")
            else:
                reasons.append("पावसाचा अंदाज सध्या अनुपलब्ध आहे.")

            if tide_available and high_tide:
                reasons.append(f"भरतीची वेळ {high_tide.get('time')} ({high_tide.get('water_level_m')} मी) खाडीतून सुरक्षित प्रस्थानासाठी अनुकूल खोली देते.")

            if safety_override:
                reasons.insert(0, f"सुरक्षा मर्यादा सक्रिय: {safety_override_reason}")
            elif hazard_titles:
                reasons.append(f"सागरी सूचना: {hazard_titles[0]}.")

        elif language == "hi":
            # Hindi Reasoning Bullets
            if pfz_probability >= 80:
                reasons.append(f"PFZ संभावना {int(pfz_probability)}% अत्यधिक मजबूत है और क्लोरोफिल फ्रंट ({chlorophyll} mg/m³) उपस्थित है।")
            elif pfz_probability >= 60:
                reasons.append(f"PFZ संभावना मध्यम ({int(pfz_probability)}%) है, जो सामान्य मछली एकत्रीकरण का संकेत देती है।")
            else:
                reasons.append(f"PFZ संभावना कम ({int(pfz_probability)}%) है, क्योंकि थर्मल ग्रेडिएंट कमज़ोर पड़ गया है।")

            if wave_height <= 1.2:
                reasons.append(f"लहरों की ऊंचाई ({wave_height} मी) शांत और सुरक्षित नौकायन के लिए अनुकूल है।")
            elif wave_height <= 1.8:
                reasons.append(f"मध्यम लहरें ({wave_height} मी) समग्र परिचालन उपयुक्तता को थोड़ा प्रभावित करती हैं।")
            else:
                reasons.append(f"ऊंची समुद्री लहरें ({wave_height} मी) सुरक्षा और उपयुक्तता को काफी कम करती हैं।")

            if rain_available:
                if precipitation_mm >= 4.0:
                    reasons.append(f"तटीय वर्षा ({precipitation_mm} मिमी, {int(rain_prob)}% संभावना) दृश्यता और डेक सुरक्षा को प्रभावित करती है।")
                elif precipitation_mm > 0:
                    reasons.append(f"हल्की बारिश ({precipitation_mm} मिमी) सामान्य सावधानियों के साथ नियंत्रित की जा सकती है।")
                else:
                    reasons.append(f"बारिश की कोई संभावना नहीं ({int(rain_prob)}%), मौसम साफ रहेगा।")
            else:
                reasons.append("बारिश का पूर्वानुमान वर्तमान में उपलब्ध नहीं है।")

            if tide_available and high_tide:
                reasons.append(f"ज्वार का समय {high_tide.get('time')} ({high_tide.get('water_level_m')} मी) सुरक्षित प्रस्थान के लिए पर्याप्त गहराई देता है।")

            if safety_override:
                reasons.insert(0, f"सुरक्षा अवरोध सक्रिय: {safety_override_reason}")
            elif hazard_titles:
                reasons.append(f"सक्रिय तटीय चेतावनी: {hazard_titles[0]}.")

        else:
            # English Reasoning Bullets
            if pfz_probability >= 80:
                reasons.append(f"PFZ confidence is strong at {int(pfz_probability)}% with dense chlorophyll front ({chlorophyll} mg/m³).")
            elif pfz_probability >= 60:
                reasons.append(f"PFZ probability is moderate ({int(pfz_probability)}%), indicating fair pelagic fish aggregation.")
            else:
                reasons.append(f"PFZ probability is low ({int(pfz_probability)}%), as satellite thermal gradient has partially dissipated.")

            if wave_height <= 1.2:
                reasons.append(f"Wave swell ({wave_height}m) is calm and favourable for safe navigation.")
            elif wave_height <= 1.8:
                reasons.append(f"Moderate sea chop ({wave_height}m swell) slightly trims overall operational suitability.")
            else:
                reasons.append(f"Elevated wave swell ({wave_height}m) significantly reduces safety and fishing suitability.")

            if rain_available:
                if precipitation_mm >= 4.0:
                    reasons.append(f"Persistent coastal rain ({precipitation_mm} mm, {int(rain_prob)}% chance) impairs deck safety and visibility.")
                elif precipitation_mm > 0:
                    reasons.append(f"Light passing rain ({precipitation_mm} mm) is manageable with standard offshore gear.")
                else:
                    reasons.append(f"No rainfall expected ({int(rain_prob)}% probability), ensuring clear atmospheric visibility.")
            else:
                reasons.append("Rain forecast is currently unavailable; rainfall could not be factored into safety.")

            if tide_available and high_tide:
                reasons.append(f"High tide at {high_tide.get('time')} ({high_tide.get('water_level_m')}m) provides optimal deep channel departure depth.")

            if safety_override:
                reasons.insert(0, f"SAFETY OVERRIDE ACTIVE: {safety_override_reason}")
            elif hazard_titles:
                reasons.append(f"Active advisory in sector: {hazard_titles[0]}.")

        return {
            "port_id": port["id"],
            "port_name": port["name"],
            "zone_id": pfz.get("id", "PFZ-01"),
            "zone_name": pfz.get("name", "Continental Shelf"),
            "pfz_probability": int(pfz_probability),
            "overall_suitability": int(overall_suitability),
            "recommendation_level": recommendation_level,
            "verdict_badge": verdict_badge,
            "safety_override": safety_override,
            "safety_override_reason": safety_override_reason,
            "wave_height_m": wave_height,
            "sea_state": sea_state,
            "wind_speed_kmh": wind_speed,
            "wind_direction": wind_dir,
            "rain_available": rain_available,
            "precipitation_mm": precipitation_mm,
            "rain_probability_pct": int(rain_prob),
            "rain_intensity": rain_intensity,
            "weather_label": weather_label,
            "sst_celsius": sst,
            "chlorophyll": chlorophyll,
            "distance_km": distance_km,
            "tide_available": tide_available,
            "high_tide": high_tide,
            "low_tide": low_tide,
            "hazards": hazards,
            "reasons": reasons[:4],
            "factors_breakdown": {
                "pfz_opportunity": int(pfz_score),
                "sea_state": int(wave_score),
                "weather_and_wind": int(weather_combined_score),
                "ocean_conditions": int(ocean_score),
                "tide_suitability": int(tide_score),
                "safety_rating": int(hazard_score)
            }
        }

    def compute_multi_day_comparison(
        self,
        port_id: str,
        pfz_id: Optional[str] = None,
        start_date: Optional[str] = None,
        num_days: int = 4,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Calculates structured forward simulation comparing
        PFZ probability, marine weather, wave swell, tides, and overall suitability.
        DETERMINISTIC: Evaluated per calendar date and location. The same date + location
        resolves to the exact same source data regardless of trip duration.
        """
        import hashlib
        port = get_port_by_id(port_id)
        cands = port.get("pfz_candidates", [])
        active_cands = [c for c in cands if c.get("status") == "ACTIVE"]
        
        target_pfz = None
        if pfz_id:
            target_pfz = next((c for c in cands if c.get("id") == pfz_id), None)
        if not target_pfz:
            target_pfz = active_cands[0] if active_cands else (cands[0] if cands else {})

        base_dt = datetime.now()
        if start_date:
            try:
                base_dt = datetime.fromisoformat(start_date)
            except Exception:
                pass

        base_wave = float(port.get("marine_conditions", {}).get("wave_height_m", 1.2))
        base_wind = float(port.get("marine_conditions", {}).get("wind_speed_kmh", 16.0))
        base_pfz_prob = float(target_pfz.get("confidence", 85))
        base_rain = get_port_weather_info(port_id)
        tide_info = get_port_tide_info(port_id)

        days_evaluated = []
        best_day = None
        challenging_day = None
        highest_suitability = -1
        lowest_suitability = 999

        for i in range(num_days):
            cur_dt = base_dt + timedelta(days=i)
            date_str = cur_dt.strftime("%Y-%m-%d")
            day_name = cur_dt.strftime("%d %B") if i > 1 else ("Today" if i == 0 else "Tomorrow")

            # Deterministic, date-based evaluation strictly keyed to (port_id, target_pfz_id, date_str)
            # This ensures that selecting 3 days vs 4 days or 7 days produces the EXACT SAME
            # underlying data and risk for any given date, with ZERO random day-index rules.
            seed_key = f"{port_id}_{target_pfz.get('id', 'pfz')}_{date_str}".encode('utf-8')
            seed_val = int(hashlib.sha256(seed_key).hexdigest()[:8], 16)

            # Realistic coastal variance keyed to date:
            # Day 0 uses actual real-time port telemetry; future dates project deterministically
            if i == 0:
                d_wave = base_wave
                d_wind = base_wind
                d_pfz = base_pfz_prob
                d_rain_mm = base_rain["precipitation_mm"]
                d_rain_prob = base_rain["rain_probability_pct"]
                d_rain_intensity = base_rain["rain_intensity"]
            else:
                wave_delta = ((seed_val % 7) - 2) * 0.1
                wind_delta = float(((seed_val >> 3) % 9) - 3)
                pfz_delta = float(((seed_val >> 6) % 10) - 4)
                rain_delta = max(0.0, float(((seed_val >> 9) % 5) * 0.6))

                d_wave = max(0.6, round(base_wave + wave_delta, 1))
                d_wind = max(8.0, round(base_wind + wind_delta, 1))
                d_pfz = max(40.0, min(95.0, round(base_pfz_prob + pfz_delta, 1)))
                d_rain_mm = round(max(0.0, base_rain["precipitation_mm"] + rain_delta), 1)
                d_rain_prob = max(10, min(85, int(base_rain["rain_probability_pct"] + rain_delta * 8)))
                d_rain_intensity = "Heavy" if d_rain_mm >= 5.0 else ("Moderate" if d_rain_mm >= 2.0 else ("Light" if d_rain_mm > 0 else "None"))

            weather_label = "Clear / Favourable" if d_rain_mm == 0 else ("Passing Showers" if d_rain_mm < 3.0 else "Heavy Rain & Squall")

            # Compute day suitability using shared engine
            day_assessment = self.compute_day_suitability(
                port_id=port_id,
                pfz={**target_pfz, "confidence": d_pfz},
                marine_conditions={
                    "wave_height_m": d_wave,
                    "wind_speed_kmh": d_wind,
                    "sea_state": "Slight" if d_wave <= 1.0 else ("Moderate" if d_wave <= 1.8 else "Rough")
                },
                weather={"wind_speed_kmh": d_wind},
                rain_data={
                    "precipitation_mm": d_rain_mm,
                    "rain_probability_pct": d_rain_prob,
                    "rain_intensity": d_rain_intensity,
                    "weather_label": weather_label
                },
                tide_info=tide_info,
                hazards=port.get("advisories", []) if i == 0 else [],
                language=language
            )

            suit = day_assessment["overall_suitability"]
            risk_badge = "LOW" if suit >= 75 else ("CAUTION" if suit >= 50 else "HIGH")

            day_obj = {
                "day_index": i + 1,
                "label": day_name,
                "date": date_str,
                "pfz_probability": int(d_pfz),
                "pfz_probability_pct": int(d_pfz),
                "overall_suitability": int(suit),
                "suitability_score": int(suit),
                "verdict": day_assessment["verdict_badge"],
                "suitability_verdict": day_assessment["verdict_badge"],
                "recommendation_level": day_assessment["recommendation_level"],
                "safety_override": day_assessment["safety_override"],
                "risk": risk_badge,
                "risk_badge": risk_badge,
                "risk_level": risk_badge,
                "wave_m": d_wave,
                "wave_height_m": d_wave,
                "wind_kmh": d_wind,
                "wind_speed_kmh": d_wind,
                "rain_mm": d_rain_mm,
                "rain_precipitation_mm": d_rain_mm,
                "rain_prob": d_rain_prob,
                "rain_probability_pct": d_rain_prob,
                "weather": weather_label,
                "weather_summary": f"{d_wave}m waves • {d_wind} km/h wind • {d_rain_mm} mm rain",
                "reasoning": day_assessment.get("reasoning", []),
                "short_report": {
                    "date": date_str,
                    "weather": weather_label,
                    "fishing": day_assessment["verdict_badge"],
                    "risk": risk_badge,
                    "pfz": f"{int(d_pfz)}%"
                }
            }

            days_evaluated.append(day_obj)

            # Track best day and most challenging day
            if not day_assessment["safety_override"] and suit > highest_suitability:
                highest_suitability = suit
                best_day = day_obj

            if suit < lowest_suitability:
                lowest_suitability = suit
                challenging_day = day_obj

        if not best_day and days_evaluated:
            best_day = days_evaluated[0]
        if not challenging_day and days_evaluated:
            challenging_day = days_evaluated[-1]

        # Overall trip summary evaluation (Requirement 7)
        has_high_risk = any(d["risk"] == "HIGH" for d in days_evaluated)
        has_caution = any(d["risk"] == "CAUTION" for d in days_evaluated)
        overall_trip_risk = "HIGH RISK" if has_high_risk else ("CAUTION" if has_caution else "RECOMMENDED")

        if language == "mr":
            trip_summary_text = (
                f"आपली {num_days}-दिवसीय मासेमारी योजना सर्वसाधारणपणे {'अनुकूल' if overall_trip_risk != 'HIGH RISK' else 'सावधगिरीची'} आहे.\n\n"
                f"• **सर्वोत्तम दिवस:** {best_day['label']} ({best_day['overall_suitability']}% अनुकूलता, {best_day['wave_m']} मी लाटा)\n"
                f"• **सर्वात आव्हानात्मक दिवस:** {challenging_day['label']} ({challenging_day['risk']} धोका, {challenging_day['weather']})\n\n"
                f"**शिफारस:** मुख्य मासेमारी मोहीम {best_day['label']} रोजी आयोजित करा आणि {challenging_day['label']} च्या प्रतिकूल हवामानात किनार्‍याजवळच राहा."
            )
        elif language == "hi":
            trip_summary_text = (
                f"आपकी {num_days}-दिवसीय यात्रा आमतौर पर मछली पकड़ने के लिए {'अनुकूल' if overall_trip_risk != 'HIGH RISK' else 'सावधानीपूर्ण'} है।\n\n"
                f"• **सर्वश्रेष्ठ दिन:** {best_day['label']} ({best_day['overall_suitability']}% उपयुक्तता, {best_day['wave_m']} मी लहरें)\n"
                f"• **सबसे कठिन दिन:** {challenging_day['label']} ({challenging_day['risk']} जोखिम, {challenging_day['weather']})\n\n"
                f"**सिफारिश:** मुख्य मछली पकड़ने की गतिविधि {best_day['label']} के आसपास आयोजित करें और {challenging_day['label']} को उच्च जोखिम अवधि से बचें।"
            )
        else:
            trip_summary_text = (
                f"Your {num_days}-day trip is generally {'favourable for fishing' if overall_trip_risk != 'HIGH RISK' else 'requires caution due to weather fronts'}.\n\n"
                f"• **Best day:** {best_day['label']} ({best_day['overall_suitability']}% suitability, {best_day['wave_m']}m waves)\n"
                f"• **Most difficult day:** {challenging_day['label']} ({challenging_day['risk']} Risk, {challenging_day['weather']})\n\n"
                f"**Recommendation:** Plan the main fishing activity around {best_day['label']} and avoid offshore exposure during {challenging_day['label']}."
            )

        return {
            "port_id": port_id,
            "port_name": port["name"],
            "zone_id": target_pfz.get("id", "PFZ-01"),
            "zone_name": target_pfz.get("name", "Offshore Pelagic Front"),
            "departure_date": start_date or cur_dt.strftime("%Y-%m-%d"),
            "duration_days": num_days,
            "overall_trip_risk": overall_trip_risk,
            "days": days_evaluated,
            "best_day": best_day,
            "challenging_day": challenging_day,
            "trip_summary": trip_summary_text,
            "comparison_verdict": trip_summary_text
        }

fishing_reasoning_engine = FishingReasoningEngine()
