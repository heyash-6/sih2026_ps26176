"""Deterministic marine risk assessment engine."""


def calculate_risk(
    wave_height: float,
    wind_speed: float,
    rainfall: float,
    hazard_severity: float,
) -> dict:
    """Calculate a deterministic marine risk score and category based on ocean conditions.

    Parameters:
    - wave_height: Wave height in meters (0 m to 5+ m)
    - wind_speed: Wind speed in km/h (0 km/h to 80+ km/h)
    - rainfall: Rainfall in mm/h (0 mm/h to 50+ mm/h)
    - hazard_severity: Hazard severity (0 to 5)

    Returns:
    Dictionary with risk_score, risk_level, and components.
    """
    # 1. Wave risk: normalize wave height to 0–100 (0 m = 0, 5+ m = 100)
    wave_risk = min(max((wave_height / 5.0) * 100.0, 0.0), 100.0)

    # 2. Wind risk: normalize wind speed to 0–100 (0 km/h = 0, 80+ km/h = 100)
    wind_risk = min(max((wind_speed / 80.0) * 100.0, 0.0), 100.0)

    # 3. Weather risk: normalize rainfall to 0–100 (0 mm/h = 0, 50+ mm/h = 100)
    weather_risk = min(max((rainfall / 50.0) * 100.0, 0.0), 100.0)

    # 4. Hazard risk: hazard_severity (0 to 5) scaled to 0–100
    hazard_risk = min(max(float(hazard_severity) * 20.0, 0.0), 100.0)

    # Final weighted risk score
    raw_risk_score = (
        0.35 * wave_risk
        + 0.25 * wind_risk
        + 0.20 * weather_risk
        + 0.20 * hazard_risk
    )
    risk_score = round(raw_risk_score, 2)

    # Determine risk level category
    if risk_score <= 25.0:
        risk_level = "LOW"
    elif risk_score <= 50.0:
        risk_level = "MEDIUM"
    elif risk_score <= 75.0:
        risk_level = "HIGH"
    else:
        risk_level = "EXTREME"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "components": {
            "wave_risk": round(wave_risk, 2),
            "wind_risk": round(wind_risk, 2),
            "weather_risk": round(weather_risk, 2),
            "hazard_risk": round(hazard_risk, 2),
        },
    }
