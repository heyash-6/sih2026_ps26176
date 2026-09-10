-- ==============================================================================
-- SIH 2026: ORCA Marine Ecosystem Reasoning Platform
-- Supabase Database Seed Data Script
-- Populates all tables with real coastal Indian marine observations, alerts, and analyses.
-- Run this in your Supabase SQL Editor: https://supabase.com/dashboard/project/byikekhtwiewlpxbuwgo/sql/new
-- ==============================================================================

-- 1. Insert Sample Hazard Alerts
INSERT INTO public.alerts (id, latitude, longitude, issued_at, title, description, risk_level, source, is_active)
VALUES
(
    'a1b2c3d4-0001-4000-8000-000000000001',
    18.9400, 72.7800,
    NOW() - INTERVAL '2 hours',
    'High Swell Wave Alert — Mumbai Offshore',
    'Rough sea conditions with swell waves between 2.1m and 2.6m expected along Maharashtra offshore waters. Small fishing vessels advised to exercise extreme caution.',
    'HIGH',
    'INCOIS / IMD',
    true
),
(
    'a1b2c3d4-0002-4000-8000-000000000002',
    15.4989, 73.7200,
    NOW() - INTERVAL '5 hours',
    'Squally Wind Advisory — Goa Coastal Waters',
    'North-westerly winds gusting up to 28 knots (52 km/h). Occasional rain showers with localized choppy seas.',
    'MODERATE',
    'IMD Coastal Bulletin',
    true
),
(
    'a1b2c3d4-0003-4000-8000-000000000003',
    16.9902, 73.2500,
    NOW() - INTERVAL '1 hour',
    'Clear Operational Corridor — Ratnagiri South',
    'Favourable marine parameters with wave heights below 1.2m and gentle breeze. High chlorophyll-a aggregation observed 22 km offshore.',
    'LOW',
    'INCOIS Advisory',
    true
),
(
    'a1b2c3d4-0004-4000-8000-000000000004',
    18.6500, 72.8200,
    NOW() - INTERVAL '3 hours',
    'Restricted Marine Border Warning — Navigational Caution',
    'Approaching designated commercial shipping lane and naval operational corridor. Keep minimum 2 nautical miles clearance.',
    'MODERATE',
    'Indian Coast Guard',
    true
)
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    risk_level = EXCLUDED.risk_level,
    is_active = EXCLUDED.is_active;

-- 2. Insert Weather Observations (Mumbai, Ratnagiri, Goa, Alibaug)
INSERT INTO public.weather_observations 
(id, latitude, longitude, observed_at, source, status, temperature, temperature_unit, wind_speed, wind_speed_unit, wind_direction, precipitation, precipitation_unit, pressure, pressure_unit)
VALUES
('b1b2c3d4-0001-4000-8000-000000000001', 18.9400, 72.8300, NOW() - INTERVAL '30 minutes', 'Open-Meteo Marine', 'observation', 28.6, '°C', 18.2, 'km/h', 310.0, 0.0, 'mm', 1012.4, 'hPa'),
('b1b2c3d4-0002-4000-8000-000000000002', 18.9400, 72.8300, NOW() - INTERVAL '3 hours', 'Open-Meteo Marine', 'observation', 28.2, '°C', 16.5, 'km/h', 305.0, 0.0, 'mm', 1013.1, 'hPa'),
('b1b2c3d4-0003-4000-8000-000000000003', 18.9400, 72.8300, NOW() - INTERVAL '6 hours', 'Open-Meteo Marine', 'observation', 27.9, '°C', 14.0, 'km/h', 290.0, 0.2, 'mm', 1011.8, 'hPa'),
('b1b2c3d4-0004-4000-8000-000000000004', 16.9902, 73.3120, NOW() - INTERVAL '1 hour', 'Open-Meteo Marine', 'observation', 27.8, '°C', 15.1, 'km/h', 295.0, 0.0, 'mm', 1012.8, 'hPa'),
('b1b2c3d4-0005-4000-8000-000000000005', 16.9902, 73.3120, NOW() - INTERVAL '4 hours', 'Open-Meteo Marine', 'observation', 27.4, '°C', 13.8, 'km/h', 285.0, 0.0, 'mm', 1013.5, 'hPa'),
('b1b2c3d4-0006-4000-8000-000000000006', 15.4989, 73.8278, NOW() - INTERVAL '1 hour', 'Open-Meteo Marine', 'observation', 29.1, '°C', 21.4, 'km/h', 325.0, 1.2, 'mm', 1011.2, 'hPa'),
('b1b2c3d4-0007-4000-8000-000000000007', 15.4989, 73.8278, NOW() - INTERVAL '5 hours', 'Open-Meteo Marine', 'observation', 28.5, '°C', 19.8, 'km/h', 315.0, 0.5, 'mm', 1012.0, 'hPa'),
('b1b2c3d4-0008-4000-8000-000000000008', 18.6414, 72.8722, NOW() - INTERVAL '2 hours', 'Open-Meteo Marine', 'observation', 28.3, '°C', 17.0, 'km/h', 300.0, 0.0, 'mm', 1012.6, 'hPa')
ON CONFLICT (id) DO UPDATE SET
    temperature = EXCLUDED.temperature,
    wind_speed = EXCLUDED.wind_speed,
    wind_direction = EXCLUDED.wind_direction;

-- 3. Insert Wave & Sea State Observations
INSERT INTO public.wave_observations
(id, latitude, longitude, observed_at, source, status, height, height_unit, direction, period, swell_height, swell_height_unit)
VALUES
('c1b2c3d4-0001-4000-8000-000000000001', 18.9400, 72.8300, NOW() - INTERVAL '30 minutes', 'INCOIS Wave Watch', 'observation', 1.35, 'm', 280.0, 7.5, 1.10, 'm'),
('c1b2c3d4-0002-4000-8000-000000000002', 18.9400, 72.8300, NOW() - INTERVAL '3 hours', 'INCOIS Wave Watch', 'observation', 1.20, 'm', 275.0, 7.2, 0.95, 'm'),
('c1b2c3d4-0003-4000-8000-000000000003', 18.9400, 72.8300, NOW() - INTERVAL '6 hours', 'INCOIS Wave Watch', 'observation', 1.10, 'm', 270.0, 6.8, 0.85, 'm'),
('c1b2c3d4-0004-4000-8000-000000000004', 16.9902, 73.3120, NOW() - INTERVAL '1 hour', 'INCOIS Wave Watch', 'observation', 0.95, 'm', 265.0, 6.5, 0.75, 'm'),
('c1b2c3d4-0005-4000-8000-000000000005', 16.9902, 73.3120, NOW() - INTERVAL '4 hours', 'INCOIS Wave Watch', 'observation', 0.88, 'm', 260.0, 6.2, 0.70, 'm'),
('c1b2c3d4-0006-4000-8000-000000000006', 15.4989, 73.8278, NOW() - INTERVAL '1 hour', 'INCOIS Wave Watch', 'observation', 1.80, 'm', 290.0, 8.4, 1.55, 'm'),
('c1b2c3d4-0007-4000-8000-000000000007', 15.4989, 73.8278, NOW() - INTERVAL '5 hours', 'INCOIS Wave Watch', 'observation', 1.65, 'm', 285.0, 8.0, 1.40, 'm')
ON CONFLICT (id) DO UPDATE SET
    height = EXCLUDED.height,
    direction = EXCLUDED.direction,
    period = EXCLUDED.period,
    swell_height = EXCLUDED.swell_height;

-- 4. Insert Ocean Observations (SST & Chlorophyll)
INSERT INTO public.ocean_observations
(id, latitude, longitude, observed_at, source, status, sea_surface_temperature, sst_unit, chlorophyll_a, chlorophyll_a_unit, salinity, salinity_unit, product)
VALUES
('d1b2c3d4-0001-4000-8000-000000000001', 18.9400, 72.8300, NOW() - INTERVAL '2 hours', 'NASA MODIS-Aqua / INCOIS', 'observation', 27.8, '°C', 0.62, 'mg/m³', 35.2, 'PSU', 'GHRSST_L4_OSTIA'),
('d1b2c3d4-0002-4000-8000-000000000002', 18.9400, 72.8300, NOW() - INTERVAL '1 day', 'NASA MODIS-Aqua / INCOIS', 'observation', 27.6, '°C', 0.59, 'mg/m³', 35.1, 'PSU', 'GHRSST_L4_OSTIA'),
('d1b2c3d4-0003-4000-8000-000000000003', 18.9400, 72.8300, NOW() - INTERVAL '2 days', 'NASA MODIS-Aqua / INCOIS', 'observation', 27.4, '°C', 0.55, 'mg/m³', 35.0, 'PSU', 'GHRSST_L4_OSTIA'),
('d1b2c3d4-0004-4000-8000-000000000004', 16.9902, 73.3120, NOW() - INTERVAL '2 hours', 'NASA MODIS-Aqua / INCOIS', 'observation', 27.2, '°C', 0.74, 'mg/m³', 35.4, 'PSU', 'GHRSST_L4_OSTIA'),
('d1b2c3d4-0005-4000-8000-000000000005', 16.9902, 73.3120, NOW() - INTERVAL '1 day', 'NASA MODIS-Aqua / INCOIS', 'observation', 27.1, '°C', 0.68, 'mg/m³', 35.3, 'PSU', 'GHRSST_L4_OSTIA'),
('d1b2c3d4-0006-4000-8000-000000000006', 15.4989, 73.8278, NOW() - INTERVAL '2 hours', 'NASA MODIS-Aqua / INCOIS', 'observation', 28.4, '°C', 0.48, 'mg/m³', 35.0, 'PSU', 'GHRSST_L4_OSTIA'),
('d1b2c3d4-0007-4000-8000-000000000007', 15.4989, 73.8278, NOW() - INTERVAL '1 day', 'NASA MODIS-Aqua / INCOIS', 'observation', 28.2, '°C', 0.45, 'mg/m³', 34.9, 'PSU', 'GHRSST_L4_OSTIA')
ON CONFLICT (id) DO UPDATE SET
    sea_surface_temperature = EXCLUDED.sea_surface_temperature,
    chlorophyll_a = EXCLUDED.chlorophyll_a,
    salinity = EXCLUDED.salinity;

-- 5. Insert Sample Marine Analyses (Agent Decisions)
INSERT INTO public.marine_analyses
(id, latitude, longitude, analyzed_at, summary, risk_level, observations, risks, recommendations, data_sources, confidence)
VALUES
(
    'e1b2c3d4-0001-4000-8000-000000000001',
    18.9400, 72.8300,
    NOW() - INTERVAL '1 hour',
    'Favourable pelagic fishing window identified at PFZ-MUM-01 (42 km WNW of Mumbai). Wave height 1.2m with steady breeze.',
    'LOW',
    '{"sea_surface_temp_c": 27.8, "chlorophyll_mg_m3": 0.62, "wave_height_m": 1.2, "wind_speed_kmh": 16.5}',
    '{"weather_risk": 18.0, "wave_risk": 22.0, "geofence_risk": 0.0, "total_risk": 20.0, "band": "LOW"}',
    '{"zone_id": "PFZ-MUM-01", "status": "RECOMMENDED", "recommended_departure": "05:30", "return_by": "12:00", "distance_km": 42.5}',
    '["INCOIS PFZ", "Open-Meteo Marine", "IMD Coastal", "NASA MODIS"]',
    0.92
),
(
    'e1b2c3d4-0002-4000-8000-000000000002',
    16.9902, 73.3120,
    NOW() - INTERVAL '4 hours',
    'Excellent coastal chlorophyll front detected near Ratnagiri Shelf. Calm seas (0.9m) and optimal surface water clarity.',
    'LOW',
    '{"sea_surface_temp_c": 27.2, "chlorophyll_mg_m3": 0.74, "wave_height_m": 0.9, "wind_speed_kmh": 14.0}',
    '{"weather_risk": 12.0, "wave_risk": 15.0, "geofence_risk": 0.0, "total_risk": 14.0, "band": "LOW"}',
    '{"zone_id": "PFZ-01", "status": "RECOMMENDED", "recommended_departure": "06:00", "return_by": "14:00", "distance_km": 28.0}',
    '["INCOIS PFZ", "Open-Meteo Marine", "ISRO Oceansat-3"]',
    0.95
)
ON CONFLICT (id) DO UPDATE SET
    summary = EXCLUDED.summary,
    risk_level = EXCLUDED.risk_level,
    observations = EXCLUDED.observations,
    risks = EXCLUDED.risks,
    recommendations = EXCLUDED.recommendations;
