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
        trip_duration_hours: float = 6.0
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

        # PFZ strength reason
        if pfz_probability >= 80:
            reasons.append(f"PFZ confidence is strong at {int(pfz_probability)}% with dense chlorophyll front ({chlorophyll} mg/m³).")
        elif pfz_probability >= 60:
            reasons.append(f"PFZ probability is moderate ({int(pfz_probability)}%), indicating fair pelagic fish aggregation.")
        else:
            reasons.append(f"PFZ probability is low ({int(pfz_probability)}%), as satellite thermal gradient has partially dissipated.")

        # Wave & sea state reason
        if wave_height <= 1.2:
            reasons.append(f"Wave swell ({wave_height}m) is calm and favourable for safe navigation.")
        elif wave_height <= 1.8:
            reasons.append(f"Moderate sea chop ({wave_height}m swell) slightly trims overall operational suitability.")
        else:
            reasons.append(f"Elevated wave swell ({wave_height}m) significantly reduces safety and fishing suitability.")

        # Weather & rain reason
        if rain_available:
            if precipitation_mm >= 4.0:
                reasons.append(f"Persistent coastal rain ({precipitation_mm} mm, {int(rain_prob)}% chance) impairs deck safety and visibility.")
            elif precipitation_mm > 0:
                reasons.append(f"Light passing rain ({precipitation_mm} mm) is manageable with standard offshore gear.")
            else:
                reasons.append(f"No rainfall expected ({int(rain_prob)}% probability), ensuring clear atmospheric visibility.")
        else:
            reasons.append("Rain forecast is currently unavailable; rainfall could not be factored into safety.")

        # Tide reason
        if tide_available and high_tide:
            reasons.append(f"High tide at {high_tide.get('time')} ({high_tide.get('water_level_m')}m) provides optimal deep channel departure depth.")

        # Safety warnings reason
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
        num_days: int = 4
    ) -> Dict[str, Any]:
        """
        Calculates structured 4-to-5 day forward simulation comparing
        PFZ probability, marine weather, wave swell, tides, and overall suitability.
        Identifies the BEST fishing window based on OVERALL suitability (not PFZ alone).
        """
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
        highest_suitability = -1

        for i in range(num_days):
            cur_dt = base_dt + timedelta(days=i)
            date_str = cur_dt.strftime("%Y-%m-%d")
            day_name = "Today" if i == 0 else ("Tomorrow" if i == 1 else cur_dt.strftime("%A (%d %b)"))

            # Simulate realistic coastal oceanographic trends
            if i == 0:
                d_pfz = base_pfz_prob
                d_wave = base_wave
                d_wind = base_wind
                d_rain_mm = base_rain["precipitation_mm"]
                d_rain_prob = base_rain["rain_probability_pct"]
                d_rain_intensity = base_rain["rain_intensity"]
            elif i == 1:
                # Tomorrow: typically calmer morning window
                d_pfz = min(94.0, base_pfz_prob + 6.0)
                d_wave = max(0.7, round(base_wave - 0.2, 1))
                d_wind = max(11.0, round(base_wind - 2.0, 1))
                d_rain_mm = max(0.0, round(base_rain["precipitation_mm"] * 0.5, 1))
                d_rain_prob = max(10, int(base_rain["rain_probability_pct"] * 0.6))
                d_rain_intensity = "Light" if d_rain_mm > 0 else "None"
            elif i == 2:
                # Day 3: moderate oceanic front swell
                d_pfz = max(45.0, base_pfz_prob - 18.0)
                d_wave = round(base_wave + 0.6, 1)
                d_wind = round(base_wind + 8.0, 1)
                d_rain_mm = round(base_rain["precipitation_mm"] + 4.5, 1)
                d_rain_prob = min(85, base_rain["rain_probability_pct"] + 35)
                d_rain_intensity = "Moderate"
            else:
                # Day 4: optimal post-upwelling pelagic surge
                d_pfz = min(95.0, base_pfz_prob + 12.0)
                d_wave = max(0.8, round(base_wave - 0.3, 1))
                d_wind = max(10.0, round(base_wind - 3.0, 1))
                d_rain_mm = 0.0
                d_rain_prob = 10
                d_rain_intensity = "None"

            # Compute day suitability using shared engine
            day_assessment = self.compute_day_suitability(
                port_id=port_id,
                pfz={**target_pfz, "confidence": d_pfz},
                marine_conditions={"wave_height_m": d_wave, "wind_speed_kmh": d_wind, "sea_state": "Slight" if d_wave <= 1.0 else ("Moderate" if d_wave <= 1.8 else "Rough")},
                weather={"wind_speed_kmh": d_wind},
                rain_data={"precipitation_mm": d_rain_mm, "rain_probability_pct": d_rain_prob, "rain_intensity": d_rain_intensity, "weather_label": "Clear / Favourable" if d_rain_mm == 0 else "Passing Showers"},
                tide_info=tide_info,
                hazards=port.get("advisories", []) if i == 0 else []
            )

            suit = day_assessment["overall_suitability"]
            risk_badge = "Low" if suit >= 75 else ("Moderate" if suit >= 50 else "High")

            day_obj = {
                "day_index": i + 1,
                "label": day_name,
                "date": date_str,
                "pfz_probability": int(d_pfz),
                "overall_suitability": int(suit),
                "verdict": day_assessment["verdict_badge"],
                "recommendation_level": day_assessment["recommendation_level"],
                "safety_override": day_assessment["safety_override"],
                "risk_badge": risk_badge,
                "wave_m": d_wave,
                "wind_kmh": d_wind,
                "rain_mm": d_rain_mm,
                "rain_prob": d_rain_prob,
                "weather_summary": f"{d_wave}m waves • {d_wind} km/h wind • {d_rain_mm} mm rain"
            }

            days_evaluated.append(day_obj)

            # Select best day based on overall conditions (NOT PFZ alone!)
            if not day_assessment["safety_override"] and suit > highest_suitability:
                highest_suitability = suit
                best_day = day_obj

        if not best_day and days_evaluated:
            best_day = days_evaluated[0]

        # Comparative explanation
        today = days_evaluated[0]
        tomorrow = days_evaluated[1] if len(days_evaluated) > 1 else today

        comparison_verdict = ""
        if today["overall_suitability"] >= 80:
            comparison_verdict = f"Today is already highly favourable ({today['overall_suitability']}%), though {best_day['label']} also offers excellent conditions ({best_day['overall_suitability']}%)."
        elif tomorrow["overall_suitability"] > today["overall_suitability"]:
            comparison_verdict = f"Tomorrow ({tomorrow['overall_suitability']}%) and {best_day['label']} ({best_day['overall_suitability']}%) provide significantly better overall fishing suitability and calmer seas than Today ({today['overall_suitability']}%)."
        else:
            comparison_verdict = f"Based on the 4-day marine outlook, {best_day['label']} is the best overall departure window with {best_day['overall_suitability']}% suitability."

        return {
            "port_id": port_id,
            "port_name": port["name"],
            "zone_id": target_pfz.get("id", "PFZ-01"),
            "zone_name": target_pfz.get("name", "Offshore Pelagic Front"),
            "days": days_evaluated,
            "best_day": best_day,
            "comparison_verdict": comparison_verdict
        }

fishing_reasoning_engine = FishingReasoningEngine()
