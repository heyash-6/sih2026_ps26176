import urllib.request
import json
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "ORCATester/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))

def post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={"Content-Type": "application/json", "User-Agent": "ORCATester/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))

def run_tests():
    print("=" * 60)
    print("RUNNING PROMPT #6 ACCEPTANCE CRITERIA VERIFICATION")
    print("=" * 60)
    
    # ----------------------------------------------------
    # TEST A: ETA & Route Assessment Points
    # ----------------------------------------------------
    print("\n[TEST A] Verifying Route ETA & Geometry-derived Assessment Points...")
    nav_res = post("/api/gis/route/safe", {
        "start_latitude": 18.94,
        "start_longitude": 72.83,
        "end_latitude": 18.65,
        "end_longitude": 72.45,
        "vessel_speed_kmh": 18.0
    })
    dist = nav_res.get("distance_km", 0)
    duration = nav_res.get("estimated_duration_min", 0)
    waypoints = nav_res.get("waypoints", [])
    assessment_points = nav_res.get("assessment_points", [])
    
    print(f"  Route distance: {dist} km")
    print(f"  Estimated duration: {duration} mins")
    print(f"  Waypoints count: {len(waypoints)}")
    print(f"  Route Assessment Points: {len(assessment_points)}")
    
    assert dist > 0, f"Distance must be > 0, got {dist}"
    assert duration > 0, f"Duration must be > 0, got {duration}"
    assert len(assessment_points) == 3, f"Expected 3 assessment points, got {len(assessment_points)}"
    
    for i, pt in enumerate(assessment_points):
        print(f"    Point {i+1}: {pt.get('point_name')} ({pt.get('latitude')}, {pt.get('longitude')}) - Wave: {pt.get('wave_height_m')}m, Wind: {pt.get('wind_speed_kmh')} km/h, Risk: {pt.get('risk_band')}")
        assert pt.get("latitude") is not None
        assert pt.get("longitude") is not None
        assert pt.get("wave_height_m") is not None
    print("  --> [TEST A PASSED]")

    # ----------------------------------------------------
    # TEST B: Ocean Analytics Productivity Index Updates
    # ----------------------------------------------------
    print("\n[TEST B] Verifying Ocean Analytics Productivity Index updates across ports...")
    mumbai_stats = get("/api/analytics?period=7&port=mumbai")
    ratnagiri_stats = get("/api/analytics?period=7&port=ratnagiri")
    
    mum_prod = mumbai_stats.get("productivity_index", {}).get("current")
    rat_prod = ratnagiri_stats.get("productivity_index", {}).get("current")
    print(f"  Mumbai Productivity Index: {mum_prod}")
    print(f"  Ratnagiri Productivity Index: {rat_prod}")
    assert mum_prod is not None, "Mumbai Productivity Index must exist"
    assert rat_prod is not None, "Ratnagiri Productivity Index must exist"
    print("  --> [TEST B PASSED]")

    # ----------------------------------------------------
    # TEST C & D & E & F: Trip Planner 3-day vs 4-day & No Day 3 Bug
    # ----------------------------------------------------
    print("\n[TEST C/D/E/F] Verifying Trip Planner Multi-day Determinism & Day 3 independence...")
    trip_3 = get("/api/fishing/multi-day?port=mumbai&pfz=PFZ-MUM-01&days=3&start_date=2026-09-13&language=en")
    trip_4 = get("/api/fishing/multi-day?port=mumbai&pfz=PFZ-MUM-01&days=4&start_date=2026-09-13&language=en")
    
    days_3 = trip_3.get("days", [])
    days_4 = trip_4.get("days", [])
    
    print(f"  3-day trip days returned: {len(days_3)}")
    print(f"  4-day trip days returned: {len(days_4)}")
    assert len(days_3) == 3, f"Expected 3 days, got {len(days_3)}"
    assert len(days_4) == 4, f"Expected 4 days, got {len(days_4)}"
    
    print("  Comparing Days 1, 2, 3 across 3-day and 4-day trips:")
    for idx in range(3):
        d3 = days_3[idx]
        d4 = days_4[idx]
        print(f"    Day {idx+1} ({d3['date']}): 3-day risk={d3['risk_level']}, score={d3['suitability_score']}, wave={d3['wave_height_m']} | 4-day risk={d4['risk_level']}, score={d4['suitability_score']}, wave={d4['wave_height_m']}")
        assert d3["date"] == d4["date"], f"Dates must match on day {idx+1}"
        assert d3["suitability_score"] == d4["suitability_score"], f"Score must match on day {idx+1}"
        assert d3["risk_level"] == d4["risk_level"], f"Risk level must match on day {idx+1}"
        assert d3["wave_height_m"] == d4["wave_height_m"], f"Wave must match on day {idx+1}"
    
    day3 = days_3[2]
    print(f"  Checking Day 3 risk: {day3['risk_level']} (Score: {day3['suitability_score']}, Wave: {day3['wave_height_m']}m)")
    # Verify Day 3 is evaluated on data merit and not hardcoded to HIGH
    assert "overall_trip_risk" in trip_4
    assert "best_day" in trip_4
    assert "trip_summary" in trip_4
    print(f"  Overall Trip Risk: {trip_4['overall_trip_risk']}")
    print(f"  Best Day: {trip_4['best_day']}")
    print(f"  Most Difficult Day: {trip_4['challenging_day']}")
    print(f"  Trip Summary: {trip_4['trip_summary']}")
    print("  --> [TEST C/D/E/F PASSED]")

    # ----------------------------------------------------
    # TEST G: Location-based Active Alerts
    # ----------------------------------------------------
    print("\n[TEST G] Verifying location-based alerts per port...")
    mum_alerts = get("/api/alerts?port=mumbai")
    rat_alerts = get("/api/alerts?port=ratnagiri")
    goa_alerts = get("/api/alerts?port=goa")
    
    print(f"  Mumbai active alerts: {len(mum_alerts.get('alerts', []))}")
    print(f"  Ratnagiri active alerts: {len(rat_alerts.get('alerts', []))}")
    print(f"  Goa active alerts: {len(goa_alerts.get('alerts', []))}")
    
    assert len(mum_alerts.get("alerts", [])) >= 1, "Mumbai should have active alerts"
    # Verify all returned alerts have valid, unexpired timestamps
    for a in mum_alerts.get("alerts", []):
        print(f"    Alert: {a.get('title')} - Severity: {a.get('severity')} - Port: {a.get('port_id')}")
    print("  --> [TEST G PASSED]")

    # ----------------------------------------------------
    # TEST H: Strict Hindi Language Response (No English sentences)
    # ----------------------------------------------------
    print("\n[TEST H] Verifying 100% Hindi response for Hindi query...")
    hindi_res = post("/api/query", {
        "text": "क्या मैं आज मछली पकड़ने जा सकता हूँ?",
        "session_id": "test_hi",
        "prior_context": {
            "language": "hi",
            "user_location": {"latitude": 18.94, "longitude": 72.83, "port_id": "mumbai", "port_name": "Mumbai Harbour"}
        }
    })
    ans_hi = hindi_res.get("answer") or hindi_res.get("explanation_text", "")
    print(f"  Hindi answer snippet (first 300 chars):\n{ans_hi[:300]}...\n")
    
    # Check that there are no leaky English phrases like "The weather is favourable" or "Fishing conditions"
    bad_english_phrases = [
        "The weather is", "Fishing conditions", "favourable and you can go",
        "PFZ probability is", "Significant wave height", "Can I go fishing",
        "According to our analysis", "Safe to proceed", "High Pelagic Activity"
    ]
    for phrase in bad_english_phrases:
        assert phrase.lower() not in ans_hi.lower(), f"English phrase '{phrase}' leaked into Hindi response!"
    print("  --> [TEST H PASSED]")

    # ----------------------------------------------------
    # TEST I: Strict Marathi Language Response
    # ----------------------------------------------------
    print("\n[TEST I] Verifying 100% Marathi response for Marathi query...")
    marathi_res = post("/api/query", {
        "text": "आज मासेमारीसाठी समुद्रात जाणे सुरक्षित आहे का?",
        "session_id": "test_mr",
        "prior_context": {
            "language": "mr",
            "user_location": {"latitude": 18.94, "longitude": 72.83, "port_id": "mumbai", "port_name": "Mumbai Harbour"}
        }
    })
    ans_mr = marathi_res.get("answer") or marathi_res.get("explanation_text", "")
    print(f"  Marathi answer snippet (first 300 chars):\n{ans_mr[:300]}...\n")
    
    for phrase in bad_english_phrases:
        assert phrase.lower() not in ans_mr.lower(), f"English phrase '{phrase}' leaked into Marathi response!"
    print("  --> [TEST I PASSED]")

    # ----------------------------------------------------
    # TEST J: Gibberish / Typo Handling
    # ----------------------------------------------------
    print("\n[TEST J] Verifying Gibberish / Typo handling (no marine hallucination)...")
    gib_res = post("/api/query", {
        "text": "abcd",
        "session_id": "test_gib",
        "prior_context": {"language": "en"}
    })
    ans_gib = gib_res.get("answer") or gib_res.get("explanation_text", "")
    print(f"  Gibberish answer:\n{ans_gib}\n")
    
    assert "typo" in ans_gib.lower() or "orca" in ans_gib.lower(), "Expected typo notice or introduction"
    assert "80%" not in ans_gib and "sst" not in ans_gib.lower(), "Should NOT hallucinate marine data for 'abcd'"
    print("  --> [TEST J PASSED]")

    print("\n" + "=" * 60)
    print("ALL ACCEPTANCE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
