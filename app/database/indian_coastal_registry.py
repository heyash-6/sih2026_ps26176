"""
Indian Coastal Ports and Offshore Potential Fishing Zones (PFZ) Registry.
Covers both West and East coasts: Gujarat, Maharashtra, Goa, Karnataka, Kerala, Tamil Nadu, Andhra Pradesh, Odisha, West Bengal.
Includes port-specific marine conditions, localized advisories, and active/inactive PFZ candidates.
"""
from typing import List, Dict, Any

INDIAN_COASTAL_PORTS: List[Dict[str, Any]] = [
    {
        "id": "veraval",
        "name": "Veraval Fishery Port",
        "state": "Gujarat",
        "sector": "North-West (Gujarat)",
        "lat": 20.9,
        "lon": 70.3667,
        "pfz_candidates": [
            {
                "id": "PFZ-VER-01",
                "zone_code": "VER-01",
                "name": "Veraval Southwest Shelf Break",
                "lat": 20.72,
                "lon": 70.15,
                "bearing_deg": 230.0,
                "distance_km": 28.4,
                "depth_m": 45.0,
                "target_species": "Silver Pomfret, Ribbonfish, Croakers",
                "description": "High thermal gradient along the 50m isobath shelf break.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.2,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-VER-02",
                "zone_code": "VER-02",
                "name": "Saurashtra Offshore Pelagic Front",
                "lat": 20.81,
                "lon": 69.98,
                "bearing_deg": 250.0,
                "distance_km": 41.5,
                "depth_m": 68.0,
                "target_species": "Indian Mackerel, Seer Fish, Squid",
                "description": "Chlorophyll-a aggregation zone driven by coastal upwelling.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.2,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-VER-03",
                "zone_code": "VER-03",
                "name": "Somnath Outer Shoal (Inactive)",
                "lat": 20.65,
                "lon": 70.42,
                "bearing_deg": 195.0,
                "distance_km": 31.0,
                "depth_m": 42.0,
                "target_species": "Croakers",
                "description": "Thermal boundary dissipated; temperature gradient dropped below 0.3\u00b0C threshold.",
                "status": "INACTIVE",
                "inactive_reason": "Thermal boundary dissipated; temperature gradient <0.3\u00b0C",
                "sst": 27.1,
                "chlorophyll": 0.31,
                "confidence": 38
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.7,
            "wind_speed_kmh": 22.0,
            "wind_direction": "NW (310\u00b0) \u2022 brisk wind",
            "sst_celsius": 27.2,
            "confidence_pct": 91,
            "departure_recommendation": "04:30\u201307:30 \u2022 Morning ebb tide window",
            "best_fishing_summary": "High thermal gradient along 50m isobath shelf break (PFZ-VER-01)"
        },
        "advisories": [
            {
                "id": "adv-ver-1",
                "type": "Weather",
                "severity": "Caution",
                "risk_level": "CAUTION",
                "title": "Brisk Wind Advisory",
                "description": "Sustained NW winds 22 km/h; small craft exercise caution beyond 20 nm."
            }
        ]
    },
    {
        "id": "porbandar",
        "name": "Porbandar Marine Port",
        "state": "Gujarat",
        "sector": "North-West (Gujarat)",
        "lat": 21.6417,
        "lon": 69.6293,
        "pfz_candidates": [
            {
                "id": "PFZ-POR-01",
                "zone_code": "POR-01",
                "name": "Porbandar Offshore Front",
                "lat": 21.48,
                "lon": 69.41,
                "bearing_deg": 232.0,
                "distance_km": 28.5,
                "depth_m": 52.0,
                "target_species": "Hilsa, Black Pomfret, Ribbonfish",
                "description": "Strong thermal front observed between 26\u00b0C coastal and 28\u00b0C open sea waters.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 26.8,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-POR-02",
                "zone_code": "POR-02",
                "name": "Dwarka-Porbandar Deep Trench",
                "lat": 21.36,
                "lon": 69.24,
                "bearing_deg": 240.0,
                "distance_km": 50.5,
                "depth_m": 85.0,
                "target_species": "Yellowfin Tuna, Skipjack, Barracuda",
                "description": "Deep pelagic chlorophyll eddy.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 26.8,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-POR-03",
                "zone_code": "POR-03",
                "name": "Miyani Creek Marine Outflow (Inactive)",
                "lat": 21.72,
                "lon": 69.45,
                "bearing_deg": 315.0,
                "distance_km": 24.0,
                "depth_m": 35.0,
                "target_species": "Hilsa, Ribbonfish",
                "description": "High coastal turbidity reducing satellite optical penetration.",
                "status": "INACTIVE",
                "inactive_reason": "High coastal sediment resuspension masking chlorophyll signals",
                "sst": 26.4,
                "chlorophyll": 0.28,
                "confidence": 41
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate to Rough",
            "wave_height_m": 1.9,
            "wind_speed_kmh": 24.5,
            "wind_direction": "WNW (290\u00b0) \u2022 active swell",
            "sst_celsius": 26.8,
            "confidence_pct": 89,
            "departure_recommendation": "05:00\u201308:00 \u2022 Pre-afternoon gust window",
            "best_fishing_summary": "Strong thermal front between 26\u00b0C coastal and 28\u00b0C open sea waters"
        },
        "advisories": [
            {
                "id": "adv-por-1",
                "type": "Caution",
                "severity": "Caution",
                "risk_level": "CAUTION",
                "title": "Rough Outer Swell",
                "description": "Wave crests approaching 2.0m near deep trench boundary."
            }
        ]
    },
    {
        "id": "okha",
        "name": "Okha Fishery Port",
        "state": "Gujarat",
        "sector": "North-West (Gujarat)",
        "lat": 22.4667,
        "lon": 69.0667,
        "pfz_candidates": [
            {
                "id": "PFZ-OKH-01",
                "zone_code": "OKH-01",
                "name": "Gulf of Kutch Outer Mouth",
                "lat": 22.38,
                "lon": 68.79,
                "bearing_deg": 255.0,
                "distance_km": 30.1,
                "depth_m": 42.0,
                "target_species": "Jewfish, Threadfin, Prawns",
                "description": "Tidal convergence and nutrient-rich estuarine plume.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 26.5,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-OKH-02",
                "zone_code": "OKH-02",
                "name": "Bet Dwarka Reef Edge (Inactive)",
                "lat": 22.45,
                "lon": 69.21,
                "bearing_deg": 75.0,
                "distance_km": 16.5,
                "depth_m": 22.0,
                "target_species": "Threadfin",
                "description": "Marine National Park conservation boundary and low pelagic aggregation index.",
                "status": "INACTIVE",
                "inactive_reason": "Ecological conservation boundary in effect; low offshore pelagic gradient",
                "sst": 26.7,
                "chlorophyll": 0.4,
                "confidence": 35
            }
        ],
        "marine_conditions": {
            "sea_state": "Rough",
            "wave_height_m": 2.1,
            "wind_speed_kmh": 26.0,
            "wind_direction": "W (270\u00b0) \u2022 strong breeze",
            "sst_celsius": 26.5,
            "confidence_pct": 88,
            "departure_recommendation": "06:00\u201308:30 \u2022 High-tide slack passage",
            "best_fishing_summary": "Tidal convergence and estuarine plume at Gulf of Kutch outer mouth"
        },
        "advisories": [
            {
                "id": "adv-okh-1",
                "type": "Warning",
                "severity": "Warning",
                "risk_level": "HIGH",
                "title": "Tidal Rip & High Waves",
                "description": "Strong 2.1m waves and rip currents at Kutch entrance. Monitor VHF channel 16."
            }
        ]
    },
    {
        "id": "mumbai",
        "name": "Mumbai Harbour (Sassoon Docks)",
        "state": "Maharashtra",
        "sector": "West Coast (Maharashtra)",
        "lat": 18.94,
        "lon": 72.83,
        "pfz_candidates": [
            {
                "id": "PFZ-MUM-01",
                "zone_code": "MUM-01",
                "name": "Mumbai Continental Shelf Edge",
                "lat": 18.98,
                "lon": 72.58,
                "bearing_deg": 280.0,
                "distance_km": 26.7,
                "depth_m": 38.0,
                "target_species": "Bombay Duck, Mackerel, Pomfret",
                "description": "Persistent thermal boundary with high chlorophyll density.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.8,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-MUM-02",
                "zone_code": "MUM-02",
                "name": "Alibaug-Mumbai South Bank",
                "lat": 18.82,
                "lon": 72.62,
                "bearing_deg": 235.0,
                "distance_km": 25.8,
                "depth_m": 44.0,
                "target_species": "Seer Fish, Croakers, Squid",
                "description": "Meandering SST filament indicating productive feeding zone.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.8,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-MUM-03",
                "zone_code": "MUM-03",
                "name": "Thane Creek Outer Eddy (Inactive)",
                "lat": 18.88,
                "lon": 72.71,
                "bearing_deg": 245.0,
                "distance_km": 21.5,
                "depth_m": 28.0,
                "target_species": "Mullet, Perches",
                "description": "Thermal boundary dissipated; temperature gradient dropped below 0.35\u00b0C threshold.",
                "status": "INACTIVE",
                "inactive_reason": "Thermal front dissipated; temperature gradient <0.35\u00b0C",
                "sst": 28.5,
                "chlorophyll": 0.32,
                "confidence": 42
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.2,
            "wind_speed_kmh": 16.0,
            "wind_direction": "NE (045\u00b0) \u2022 steady",
            "sst_celsius": 27.8,
            "confidence_pct": 94,
            "departure_recommendation": "05:00\u201308:30 \u2022 Favourable low-swell window",
            "best_fishing_summary": "Continental shelf edge with high chlorophyll density (PFZ-MUM-01)"
        },
        "advisories": [
            {
                "id": "adv-mum-1",
                "type": "Safety",
                "severity": "Moderate",
                "risk_level": "MODERATE",
                "title": "Moderate Sea State",
                "description": "Waves around 1.2 m expected along Mumbai outer shelf. Favourable for mechanised craft."
            }
        ]
    },
    {
        "id": "alibaug",
        "name": "Alibaug Port (Revdanda)",
        "state": "Maharashtra",
        "sector": "West Coast (Maharashtra)",
        "lat": 18.6414,
        "lon": 72.8722,
        "pfz_candidates": [
            {
                "id": "PFZ-ALI-01",
                "zone_code": "ALI-01",
                "name": "Kundalika Estuary Outflow PFZ",
                "lat": 18.58,
                "lon": 72.64,
                "bearing_deg": 255.0,
                "distance_km": 25.5,
                "depth_m": 35.0,
                "target_species": "Ribbonfish, White Prawns, Sardines",
                "description": "Plankton bloom supported by estuarine nutrient runoff.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.6,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-ALI-02",
                "zone_code": "ALI-02",
                "name": "Chaul Pelagic Bank (Inactive)",
                "lat": 18.52,
                "lon": 72.78,
                "bearing_deg": 210.0,
                "distance_km": 18.0,
                "depth_m": 24.0,
                "target_species": "Anchovies, Small Prawns",
                "description": "Front moved into nearshore shoal; inadequate vessel keel clearance.",
                "status": "INACTIVE",
                "inactive_reason": "Nearshore shoal shift; inadequate vessel clearance",
                "sst": 27.4,
                "chlorophyll": 0.35,
                "confidence": 43
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.1,
            "wind_speed_kmh": 15.0,
            "wind_direction": "NE (050\u00b0) \u2022 gentle",
            "sst_celsius": 27.6,
            "confidence_pct": 93,
            "departure_recommendation": "05:00\u201308:30 \u2022 Morning slack tide",
            "best_fishing_summary": "Kundalika estuary nutrient outflow with rich white prawn and ribbonfish"
        },
        "advisories": [
            {
                "id": "adv-ali-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "INFO",
                "title": "Manageable Swell Conditions",
                "description": "Manageable sea conditions across Alibaug coastal corridor."
            }
        ]
    },
    {
        "id": "ratnagiri",
        "name": "Ratnagiri Fishery Port (Mirkarwada)",
        "state": "Maharashtra",
        "sector": "West Coast (Maharashtra)",
        "lat": 16.9902,
        "lon": 73.312,
        "pfz_candidates": [
            {
                "id": "PFZ-RAT-01",
                "zone_code": "RAT-01",
                "name": "Mirkarwada West Pelagic Belt",
                "lat": 16.92,
                "lon": 73.08,
                "bearing_deg": 252.0,
                "distance_km": 26.0,
                "depth_m": 48.0,
                "target_species": "Kingfish, Horse Mackerel, Squid",
                "description": "Well-defined cyclonic eddy with optimal 28.1\u00b0C surface temperature.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.1,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-RAT-02",
                "zone_code": "RAT-02",
                "name": "Jaigad Deep Slope PFZ",
                "lat": 17.1,
                "lon": 73.02,
                "bearing_deg": 295.0,
                "distance_km": 33.4,
                "depth_m": 72.0,
                "target_species": "Tuna, Seer Fish, Barracuda",
                "description": "Sharp boundary of oceanic chlorophyll-a front.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.1,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-RAT-03",
                "zone_code": "RAT-03",
                "name": "Rajapur Bay Shelf Margin (Inactive)",
                "lat": 16.65,
                "lon": 73.12,
                "bearing_deg": 230.0,
                "distance_km": 38.0,
                "depth_m": 58.0,
                "target_species": "Carangids, Anchovies",
                "description": "Seasonal thermocline deepening; pelagic schools shifted into deeper waters (>90m).",
                "status": "INACTIVE",
                "inactive_reason": "Seasonal thermocline deepening; schools shifted to deep water",
                "sst": 27.9,
                "chlorophyll": 0.38,
                "confidence": 45
            }
        ],
        "marine_conditions": {
            "sea_state": "Slight to Moderate",
            "wave_height_m": 1.4,
            "wind_speed_kmh": 14.5,
            "wind_direction": "NW (315\u00b0) \u2022 steady breeze",
            "sst_celsius": 28.1,
            "confidence_pct": 92,
            "departure_recommendation": "05:30\u201309:00 \u2022 Clear coastal passage",
            "best_fishing_summary": "Mirkarwada pelagic belt with optimal 28.1\u00b0C surface thermal boundary"
        },
        "advisories": [
            {
                "id": "adv-rat-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "INFO",
                "title": "Favourable Pelagic Window",
                "description": "Stable sea conditions with high mackerel and kingfish signals."
            }
        ]
    },
    {
        "id": "malvan",
        "name": "Malvan Fishery Port",
        "state": "Maharashtra",
        "sector": "West Coast (Maharashtra)",
        "lat": 16.0594,
        "lon": 73.4686,
        "pfz_candidates": [
            {
                "id": "PFZ-MAL-01",
                "zone_code": "MAL-01",
                "name": "Sindhudurg Outer Reef Shelf",
                "lat": 15.98,
                "lon": 73.28,
                "bearing_deg": 246.0,
                "distance_km": 22.0,
                "depth_m": 50.0,
                "target_species": "Indian Mackerel, Rock Cod, Reef Snappers",
                "description": "Clear water convergence zone adjacent to coral shelf.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.3,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-MAL-02",
                "zone_code": "MAL-02",
                "name": "Tarkarli Deep Ridge (Inactive)",
                "lat": 15.98,
                "lon": 73.32,
                "bearing_deg": 220.0,
                "distance_km": 25.0,
                "depth_m": 48.0,
                "target_species": "Squid, Pomfret",
                "description": "SST gradient flattened following uniform surface solar warming.",
                "status": "INACTIVE",
                "inactive_reason": "SST gradient flattened following uniform solar warming",
                "sst": 28.8,
                "chlorophyll": 0.39,
                "confidence": 44
            }
        ],
        "marine_conditions": {
            "sea_state": "Calm to Slight",
            "wave_height_m": 0.9,
            "wind_speed_kmh": 12.0,
            "wind_direction": "NW (315\u00b0) \u2022 light breeze",
            "sst_celsius": 28.3,
            "confidence_pct": 95,
            "departure_recommendation": "05:15\u201309:00 \u2022 Clear sunrise departure",
            "best_fishing_summary": "Sindhudurg rock shelf upwelling with rich seer fish and squids"
        },
        "advisories": [
            {
                "id": "adv-mal-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "INFO",
                "title": "Clear Sea Conditions",
                "description": "Under 1.0 m waves; optimal coastal fishing environment."
            }
        ]
    },
    {
        "id": "goa",
        "name": "Goa Mormugao Port",
        "state": "Goa",
        "sector": "South-West (Goa)",
        "lat": 15.4989,
        "lon": 73.8278,
        "pfz_candidates": [
            {
                "id": "PFZ-GOA-01",
                "zone_code": "GOA-01",
                "name": "Zuari Offshore Upwelling Zone",
                "lat": 15.42,
                "lon": 73.56,
                "bearing_deg": 252.0,
                "distance_km": 30.0,
                "depth_m": 54.0,
                "target_species": "Oil Sardine, Mackerel, Squid",
                "description": "High chlorophyll density from sustained seasonal upwelling.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.6,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-GOA-02",
                "zone_code": "GOA-02",
                "name": "Aguada-Anjuna Deep Slope",
                "lat": 15.61,
                "lon": 73.51,
                "bearing_deg": 291.0,
                "distance_km": 36.2,
                "depth_m": 65.0,
                "target_species": "Tuna, Seer Fish, Solenocera Prawns",
                "description": "Distinct thermal divergence supporting pelagic schools.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.6,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-GOA-03",
                "zone_code": "GOA-03",
                "name": "Cabo de Rama Trench (Inactive)",
                "lat": 15.15,
                "lon": 73.68,
                "bearing_deg": 215.0,
                "distance_km": 42.0,
                "depth_m": 62.0,
                "target_species": "Ribbonfish, Sole",
                "description": "Plankton plume dispersed by offshore subsurface counter-current.",
                "status": "INACTIVE",
                "inactive_reason": "Plankton plume dispersed by offshore counter-current",
                "sst": 29.0,
                "chlorophyll": 0.35,
                "confidence": 40
            }
        ],
        "marine_conditions": {
            "sea_state": "Calm",
            "wave_height_m": 0.8,
            "wind_speed_kmh": 11.0,
            "wind_direction": "W (260\u00b0) \u2022 gentle breeze",
            "sst_celsius": 28.6,
            "confidence_pct": 96,
            "departure_recommendation": "05:00\u201309:30 \u2022 Calm sea state & high visibility",
            "best_fishing_summary": "Aguada outer thermal gradient with high sardine & mackerel aggregation"
        },
        "advisories": [
            {
                "id": "adv-goa-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "INFO",
                "title": "Optimal Operating Conditions",
                "description": "Calm inshore waters under 1.0 m waves across Mormugao approaches."
            }
        ]
    },
    {
        "id": "karwar",
        "name": "Karwar Fishery Port (Baithkol)",
        "state": "Karnataka",
        "sector": "South-West (Karnataka)",
        "lat": 14.805,
        "lon": 74.124,
        "pfz_candidates": [
            {
                "id": "PFZ-KAR-01",
                "zone_code": "KAR-01",
                "name": "Kali Estuary Convergence PFZ",
                "lat": 14.72,
                "lon": 73.91,
                "bearing_deg": 246.0,
                "distance_km": 25.0,
                "depth_m": 42.0,
                "target_species": "Oil Sardine, Silver Belly, Cuttlefish",
                "description": "Sub-surface cold tongue with rich zooplankton abundance.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.4,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-KAR-02",
                "zone_code": "KAR-02",
                "name": "Anjadip Island Shoal (Inactive)",
                "lat": 14.72,
                "lon": 74.02,
                "bearing_deg": 215.0,
                "distance_km": 15.0,
                "depth_m": 30.0,
                "target_species": "Sardines",
                "description": "Naval boundary security exclusion zone in effect.",
                "status": "INACTIVE",
                "inactive_reason": "Security corridor exclusion in effect",
                "sst": 28.1,
                "chlorophyll": 0.45,
                "confidence": 36
            }
        ],
        "marine_conditions": {
            "sea_state": "Slight",
            "wave_height_m": 1.0,
            "wind_speed_kmh": 13.5,
            "wind_direction": "W (265\u00b0) \u2022 steady",
            "sst_celsius": 28.4,
            "confidence_pct": 94,
            "departure_recommendation": "05:00\u201308:45 \u2022 Early morning calm",
            "best_fishing_summary": "Kali River confluence front with abundant mackerel and oil sardines"
        },
        "advisories": [
            {
                "id": "adv-kar-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "INFO",
                "title": "Steady Marine State",
                "description": "Waves around 1.0m, good visibility along Baithkol fairway."
            }
        ]
    },
    {
        "id": "mangalore",
        "name": "Mangalore Fishery Port (Old Port / Bunder)",
        "state": "Karnataka",
        "sector": "South-West (Karnataka)",
        "lat": 12.858,
        "lon": 74.836,
        "pfz_candidates": [
            {
                "id": "PFZ-MNG-01",
                "zone_code": "MNG-01",
                "name": "Netravati Offshore Shelf PFZ",
                "lat": 12.78,
                "lon": 74.58,
                "bearing_deg": 252.0,
                "distance_km": 29.2,
                "depth_m": 50.0,
                "target_species": "Indian Mackerel, Ribbonfish, Sole Fish",
                "description": "Sustained high primary productivity along 40-50m depth contour.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.5,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-MNG-02",
                "zone_code": "MNG-02",
                "name": "Malpe-Mangalore Outer Trench",
                "lat": 12.96,
                "lon": 74.52,
                "bearing_deg": 290.0,
                "distance_km": 36.1,
                "depth_m": 78.0,
                "target_species": "Yellowfin Tuna, Bonito, Queenfish",
                "description": "Deep-water thermal front with active baitfish aggregations.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.5,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-MAN-03",
                "zone_code": "MAN-03",
                "name": "Surathkal Outer Trench (Inactive)",
                "lat": 12.98,
                "lon": 74.62,
                "bearing_deg": 310.0,
                "distance_km": 28.0,
                "depth_m": 52.0,
                "target_species": "Horse Mackerel",
                "description": "Thermal boundary shifted northwards beyond single-day voyage radius.",
                "status": "INACTIVE",
                "inactive_reason": "Thermal boundary shifted northwards beyond single-day range",
                "sst": 28.7,
                "chlorophyll": 0.35,
                "confidence": 42
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.3,
            "wind_speed_kmh": 17.0,
            "wind_direction": "NW (305\u00b0) \u2022 moderate",
            "sst_celsius": 28.5,
            "confidence_pct": 93,
            "departure_recommendation": "05:00\u201308:30 \u2022 Low-swell fairway passage",
            "best_fishing_summary": "Netravati estuary plume meeting Arabian Sea pelagic current"
        },
        "advisories": [
            {
                "id": "adv-man-1",
                "type": "Caution",
                "severity": "Caution",
                "risk_level": "CAUTION",
                "title": "Bar Mouth Swell",
                "description": "Breaking swells up to 1.4m across Netravati river mouth."
            }
        ]
    },
    {
        "id": "kochi",
        "name": "Cochin Fishery Harbour (Thoppumpady)",
        "state": "Kerala",
        "sector": "South-West (Kerala)",
        "lat": 9.965,
        "lon": 76.262,
        "pfz_candidates": [
            {
                "id": "PFZ-KCH-01",
                "zone_code": "KCH-01",
                "name": "Cochin Mud Bank Outer Fringe",
                "lat": 9.88,
                "lon": 76.01,
                "bearing_deg": 252.0,
                "distance_km": 29.2,
                "depth_m": 36.0,
                "target_species": "Oil Sardine, Indian Mackerel, Karikkadi Prawns",
                "description": "Traditional high-yield mud bank zone with massive plankton density.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.9,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-KCH-02",
                "zone_code": "KCH-02",
                "name": "Vypin Deep Continental Slope",
                "lat": 10.08,
                "lon": 75.98,
                "bearing_deg": 293.0,
                "distance_km": 33.4,
                "depth_m": 70.0,
                "target_species": "Yellowfin Tuna, Skipjack, Threadfin Bream",
                "description": "Clear thermal gradient with high chlorophyll-a concentration.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.9,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-KOC-03",
                "zone_code": "KOC-03",
                "name": "Vypin Nearshore Bank (Inactive)",
                "lat": 10.05,
                "lon": 76.12,
                "bearing_deg": 320.0,
                "distance_km": 18.0,
                "depth_m": 22.0,
                "target_species": "Anchovy, Mullet",
                "description": "Salinity drop due to heavy monsoonal sluice discharge.",
                "status": "INACTIVE",
                "inactive_reason": "Salinity drop due to monsoonal sluice outflow",
                "sst": 27.6,
                "chlorophyll": 0.3,
                "confidence": 40
            }
        ],
        "marine_conditions": {
            "sea_state": "Slight",
            "wave_height_m": 1.1,
            "wind_speed_kmh": 15.2,
            "wind_direction": "WNW (295\u00b0) \u2022 favourable",
            "sst_celsius": 28.9,
            "confidence_pct": 95,
            "departure_recommendation": "04:45\u201308:15 \u2022 Favourable low-swell window",
            "best_fishing_summary": "Intense coastal upwelling and mud-bank nutrient enrichment zone"
        },
        "advisories": [
            {
                "id": "adv-koc-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "FAVOURABLE",
                "title": "Favourable Upwelling Window",
                "description": "High biological productivity across Cochin approaches."
            }
        ]
    },
    {
        "id": "kollam",
        "name": "Kollam Neendakara Harbour",
        "state": "Kerala",
        "sector": "South-West (Kerala)",
        "lat": 8.944,
        "lon": 76.536,
        "pfz_candidates": [
            {
                "id": "PFZ-KLM-01",
                "zone_code": "KLM-01",
                "name": "Ashtamudi Deep Offshore PFZ",
                "lat": 8.86,
                "lon": 76.32,
                "bearing_deg": 247.0,
                "distance_km": 25.5,
                "depth_m": 45.0,
                "target_species": "Deep-sea Prawns, Cephalopods, Anchovies",
                "description": "Nutrient plume converging with coastal south-flowing current.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.8,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-KOL-02",
                "zone_code": "KOL-02",
                "name": "Tangasseri Reef Ridge (Inactive)",
                "lat": 8.85,
                "lon": 76.42,
                "bearing_deg": 235.0,
                "distance_km": 20.0,
                "depth_m": 35.0,
                "target_species": "Deep-sea shrimp",
                "description": "Thermal gradient dissipated below 0.35\u00b0C threshold.",
                "status": "INACTIVE",
                "inactive_reason": "Thermal gradient dissipated below threshold",
                "sst": 29.0,
                "chlorophyll": 0.33,
                "confidence": 43
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.3,
            "wind_speed_kmh": 16.5,
            "wind_direction": "NW (310\u00b0) \u2022 brisk",
            "sst_celsius": 28.8,
            "confidence_pct": 92,
            "departure_recommendation": "05:00\u201308:30 \u2022 Morning harbour clearing",
            "best_fishing_summary": "Ashtamudi estuary outflow front with prime deep-sea shrimp & squid"
        },
        "advisories": [
            {
                "id": "adv-kol-1",
                "type": "Caution",
                "severity": "Caution",
                "risk_level": "CAUTION",
                "title": "Moderate Coastal Swell",
                "description": "1.3m swells around Neendakara entrance."
            }
        ]
    },
    {
        "id": "kanyakumari",
        "name": "Kanyakumari Cape Port",
        "state": "Tamil Nadu",
        "sector": "South Coast (Tamil Nadu)",
        "lat": 8.0883,
        "lon": 77.5385,
        "pfz_candidates": [
            {
                "id": "PFZ-KAN-01",
                "zone_code": "KAN-01",
                "name": "Wadge Bank Oceanic Upwelling",
                "lat": 7.92,
                "lon": 77.42,
                "bearing_deg": 215.0,
                "distance_km": 22.8,
                "depth_m": 55.0,
                "target_species": "Skipjack Tuna, Perches, Rock Cod",
                "description": "Tri-sea confluence zone creating one of India's richest fishing grounds.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.5,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-KAN-02",
                "zone_code": "KAN-02",
                "name": "Cape Comorin East Ledge",
                "lat": 8.01,
                "lon": 77.72,
                "bearing_deg": 115.0,
                "distance_km": 22.1,
                "depth_m": 48.0,
                "target_species": "Seer Fish, Carangids, Flying Fish",
                "description": "SST frontal zone between Arabian Sea and Gulf of Mannar.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.5,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-KAN-03",
                "zone_code": "KAN-03",
                "name": "Wadge Bank Outer Shelf (Inactive)",
                "lat": 7.82,
                "lon": 77.38,
                "bearing_deg": 205.0,
                "distance_km": 35.0,
                "depth_m": 60.0,
                "target_species": "Reef Cod, Perches",
                "description": "High wave turbulence disrupting surface drift nets.",
                "status": "INACTIVE",
                "inactive_reason": "High sea turbulence disrupting operational safety",
                "sst": 27.2,
                "chlorophyll": 0.41,
                "confidence": 45
            }
        ],
        "marine_conditions": {
            "sea_state": "Rough",
            "wave_height_m": 2.0,
            "wind_speed_kmh": 27.0,
            "wind_direction": "SW (220\u00b0) \u2022 strong cross-current",
            "sst_celsius": 27.5,
            "confidence_pct": 90,
            "departure_recommendation": "04:30\u201307:00 \u2022 Pre-wind surge window",
            "best_fishing_summary": "Tri-sea convergence (Arabian Sea, Bay of Bengal, Indian Ocean)"
        },
        "advisories": [
            {
                "id": "adv-kan-1",
                "type": "Warning",
                "severity": "Warning",
                "risk_level": "HIGH",
                "title": "Tri-Sea Cross-Swell Warning",
                "description": "Strong 2.0m cross-swells and 27 km/h winds off Cape Comorin."
            }
        ]
    },
    {
        "id": "tuticorin",
        "name": "Tuticorin (V.O.C.) Port",
        "state": "Tamil Nadu",
        "sector": "South-East (Gulf of Mannar)",
        "lat": 8.7642,
        "lon": 78.1348,
        "pfz_candidates": [
            {
                "id": "PFZ-TUT-01",
                "zone_code": "TUT-01",
                "name": "Gulf of Mannar Deep Basin PFZ",
                "lat": 8.71,
                "lon": 78.36,
                "bearing_deg": 105.0,
                "distance_km": 25.6,
                "depth_m": 52.0,
                "target_species": "Lethrinids (Pig-face Bream), Barracuda, Prawns",
                "description": "Biosphere-fringe oceanic trench with rich phytoplankton density.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.2,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-TUT-02",
                "zone_code": "TUT-02",
                "name": "Pearl Bank Offshore Ridge",
                "lat": 8.89,
                "lon": 78.42,
                "bearing_deg": 65.0,
                "distance_km": 34.3,
                "depth_m": 64.0,
                "target_species": "Seer Fish, Tuna, Snappers",
                "description": "Reef-edge convergence front.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.2,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-TUT-03",
                "zone_code": "TUT-03",
                "name": "Hare Island Outer Shoal (Inactive)",
                "lat": 8.78,
                "lon": 78.25,
                "bearing_deg": 70.0,
                "distance_km": 14.0,
                "depth_m": 22.0,
                "target_species": "Crabs, Mullet",
                "description": "Marine biosphere reserve boundary restriction.",
                "status": "INACTIVE",
                "inactive_reason": "Marine biosphere reserve conservation boundary",
                "sst": 28.5,
                "chlorophyll": 0.38,
                "confidence": 35
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.2,
            "wind_speed_kmh": 18.0,
            "wind_direction": "NE (040\u00b0) \u2022 steady",
            "sst_celsius": 28.2,
            "confidence_pct": 92,
            "departure_recommendation": "05:30\u201309:00 \u2022 Morning calm sea state",
            "best_fishing_summary": "Gulf of Mannar protected reef-adjacent biological corridor"
        },
        "advisories": [
            {
                "id": "adv-tut-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "INFO",
                "title": "Gulf of Mannar Advisory",
                "description": "Sheltered waters with steady 1.2m wave regime."
            }
        ]
    },
    {
        "id": "nagapattinam",
        "name": "Nagapattinam Fishery Harbour",
        "state": "Tamil Nadu",
        "sector": "South-East (Coromandel)",
        "lat": 10.7656,
        "lon": 79.8424,
        "pfz_candidates": [
            {
                "id": "PFZ-NAG-01",
                "zone_code": "NAG-01",
                "name": "Cauvery Delta Marine Outflow PFZ",
                "lat": 10.72,
                "lon": 80.12,
                "bearing_deg": 99.0,
                "distance_km": 30.8,
                "depth_m": 42.0,
                "target_species": "Hilsa, Pomfret, Tiger Prawns",
                "description": "Chlorophyll plume generated by Cauvery river basin discharge.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.6,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-NAG-02",
                "zone_code": "NAG-02",
                "name": "Point Calimere Shoal (Inactive)",
                "lat": 10.35,
                "lon": 80.02,
                "bearing_deg": 155.0,
                "distance_km": 32.0,
                "depth_m": 25.0,
                "target_species": "Prawns, Whiting",
                "description": "Shallow bank sediment resuspension masking optical signals.",
                "status": "INACTIVE",
                "inactive_reason": "Sediment resuspension masking optical signals",
                "sst": 28.3,
                "chlorophyll": 0.26,
                "confidence": 39
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.4,
            "wind_speed_kmh": 19.5,
            "wind_direction": "ENE (065\u00b0) \u2022 moderate",
            "sst_celsius": 28.6,
            "confidence_pct": 91,
            "departure_recommendation": "05:00\u201308:30 \u2022 Low-swell window",
            "best_fishing_summary": "Cauvery delta shelf front with prime pomfret and mackerel"
        },
        "advisories": [
            {
                "id": "adv-nag-1",
                "type": "Caution",
                "severity": "Caution",
                "risk_level": "CAUTION",
                "title": "Coromandel Coastal Swell",
                "description": "1.4m waves from east-northeast."
            }
        ]
    },
    {
        "id": "chennai",
        "name": "Chennai Kasimedu Fishery Harbour",
        "state": "Tamil Nadu",
        "sector": "South-East (Coromandel)",
        "lat": 13.125,
        "lon": 80.298,
        "pfz_candidates": [
            {
                "id": "PFZ-CHN-01",
                "zone_code": "CHN-01",
                "name": "Kasimedu Offshore Pelagic Front",
                "lat": 13.18,
                "lon": 80.56,
                "bearing_deg": 76.0,
                "distance_km": 29.0,
                "depth_m": 48.0,
                "target_species": "Seer Fish, Ribbonfish, Trevally",
                "description": "Pronounced thermal boundary between nearshore and Bay of Bengal shelf.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.8,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-CHN-02",
                "zone_code": "CHN-02",
                "name": "Coromandel Deep Continental Slope",
                "lat": 13.01,
                "lon": 80.59,
                "bearing_deg": 113.0,
                "distance_km": 34.2,
                "depth_m": 85.0,
                "target_species": "Yellowfin Tuna, Sailfish, Barracuda",
                "description": "Deep blue water thermal front with high chlorophyll boundary.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.8,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-CHE-03",
                "zone_code": "CHE-03",
                "name": "Pulicat Lake Outflow Zone (Inactive)",
                "lat": 13.45,
                "lon": 80.45,
                "bearing_deg": 25.0,
                "distance_km": 36.0,
                "depth_m": 35.0,
                "target_species": "Pomfret, Croakers",
                "description": "Thermal contrast subsided; temperature gradient dropped under 0.3\u00b0C.",
                "status": "INACTIVE",
                "inactive_reason": "Thermal contrast subsided; gradient <0.3\u00b0C",
                "sst": 29.1,
                "chlorophyll": 0.31,
                "confidence": 43
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate to Rough",
            "wave_height_m": 1.5,
            "wind_speed_kmh": 21.0,
            "wind_direction": "E (090\u00b0) \u2022 easterly swell",
            "sst_celsius": 28.8,
            "confidence_pct": 91,
            "departure_recommendation": "04:30\u201308:00 \u2022 Early morning departure",
            "best_fishing_summary": "Kasimedu offshore submarine canyon and thermal filament"
        },
        "advisories": [
            {
                "id": "adv-che-1",
                "type": "Caution",
                "severity": "Caution",
                "risk_level": "CAUTION",
                "title": "Easterly Swell Caution",
                "description": "Long-period easterly swells 1.5m. Keep clear of harbor shipping channel."
            }
        ]
    },
    {
        "id": "kakinada",
        "name": "Kakinada Deepwater Port",
        "state": "Andhra Pradesh",
        "sector": "East Coast (Andhra Pradesh)",
        "lat": 16.9891,
        "lon": 82.2475,
        "pfz_candidates": [
            {
                "id": "PFZ-KAK-01",
                "zone_code": "KAK-01",
                "name": "Godavari Estuary Marine Front",
                "lat": 16.89,
                "lon": 82.52,
                "bearing_deg": 112.0,
                "distance_km": 31.1,
                "depth_m": 46.0,
                "target_species": "Croakers, Ribbonfish, Tiger Prawns",
                "description": "Rich nutrient confluence from Godavari river delta.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.7,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-KAK-02",
                "zone_code": "KAK-02",
                "name": "Hope Island Pelagic Bank (Inactive)",
                "lat": 16.92,
                "lon": 82.42,
                "bearing_deg": 120.0,
                "distance_km": 21.0,
                "depth_m": 32.0,
                "target_species": "Tiger Prawns, Sole",
                "description": "Current vector shifted sedimentation plume away from shelf edge.",
                "status": "INACTIVE",
                "inactive_reason": "Current shifted sedimentation plume away from shelf",
                "sst": 28.5,
                "chlorophyll": 0.36,
                "confidence": 41
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.3,
            "wind_speed_kmh": 17.5,
            "wind_direction": "ESE (110\u00b0) \u2022 steady",
            "sst_celsius": 28.7,
            "confidence_pct": 93,
            "departure_recommendation": "05:00\u201308:30 \u2022 Favourable tide passage",
            "best_fishing_summary": "Godavari river delta plume confluence with rich tiger prawns"
        },
        "advisories": [
            {
                "id": "adv-kak-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "INFO",
                "title": "Delta Estuary Confluence",
                "description": "Moderate wave activity under 1.4m across Godavari coastal basin."
            }
        ]
    },
    {
        "id": "visakhapatnam",
        "name": "Visakhapatnam Fishing Harbour",
        "state": "Andhra Pradesh",
        "sector": "East Coast (Andhra Pradesh)",
        "lat": 17.6868,
        "lon": 83.2185,
        "pfz_candidates": [
            {
                "id": "PFZ-VIZ-01",
                "zone_code": "VIZ-01",
                "name": "Vizag Submarine Canyon Front",
                "lat": 17.62,
                "lon": 83.49,
                "bearing_deg": 105.0,
                "distance_km": 29.8,
                "depth_m": 60.0,
                "target_species": "Yellowfin Tuna, Skipjack, Threadfin Bream",
                "description": "Submarine canyon upwelling bringing nutrient-rich deep water to surface.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.4,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-VIZ-02",
                "zone_code": "VIZ-02",
                "name": "Bheemunipatnam Offshore Ridge",
                "lat": 17.81,
                "lon": 83.52,
                "bearing_deg": 61.0,
                "distance_km": 35.0,
                "depth_m": 92.0,
                "target_species": "Seer Fish, Billfish, Carangids",
                "description": "Persistent chlorophyll front along the 100m contour line.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.4,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-VIZ-03",
                "zone_code": "VIZ-03",
                "name": "Gangavaram Deep Trench (Inactive)",
                "lat": 17.55,
                "lon": 83.38,
                "bearing_deg": 140.0,
                "distance_km": 26.0,
                "depth_m": 75.0,
                "target_species": "Skipjack Tuna",
                "description": "Thermal front dissipated below threshold following local wind shift.",
                "status": "INACTIVE",
                "inactive_reason": "Thermal front dissipated below threshold following wind shift",
                "sst": 28.7,
                "chlorophyll": 0.34,
                "confidence": 44
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.4,
            "wind_speed_kmh": 18.5,
            "wind_direction": "E (085\u00b0) \u2022 steady",
            "sst_celsius": 28.4,
            "confidence_pct": 94,
            "departure_recommendation": "05:15\u201308:45 \u2022 Morning offshore window",
            "best_fishing_summary": "Submarine canyon upwelling bringing yellowfin tuna & seer fish"
        },
        "advisories": [
            {
                "id": "adv-viz-1",
                "type": "Info",
                "severity": "Favourable",
                "risk_level": "INFO",
                "title": "Canyon Upwelling Favourable",
                "description": "High yellowfin tuna pelagic activity along 100m contour."
            }
        ]
    },
    {
        "id": "paradip",
        "name": "Paradip Fishery Port",
        "state": "Odisha",
        "sector": "East Coast (Odisha)",
        "lat": 20.2644,
        "lon": 86.6715,
        "pfz_candidates": [
            {
                "id": "PFZ-PAR-01",
                "zone_code": "PAR-01",
                "name": "Mahanadi Plume Convergence PFZ",
                "lat": 20.12,
                "lon": 86.94,
                "bearing_deg": 116.0,
                "distance_km": 32.8,
                "depth_m": 38.0,
                "target_species": "Hilsa, Silver Pomfret, Catfish",
                "description": "Mahanadi estuarine discharge meeting coastal current creating massive plankton bloom.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.9,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-PAR-02",
                "zone_code": "PAR-02",
                "name": "Wheeler-Paradip Continental Edge",
                "lat": 20.38,
                "lon": 87.01,
                "bearing_deg": 70.0,
                "distance_km": 38.1,
                "depth_m": 65.0,
                "target_species": "Tuna, Ribbonfish, Horse Mackerel",
                "description": "Deep shelf thermal boundary in Northern Bay of Bengal.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 27.9,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-PAR-03",
                "zone_code": "PAR-03",
                "name": "Dhamra Estuary Outer Spit (Inactive)",
                "lat": 20.45,
                "lon": 87.12,
                "bearing_deg": 65.0,
                "distance_km": 34.0,
                "depth_m": 28.0,
                "target_species": "Hilsa, Pomfret",
                "description": "Monsoon freshwater dilution temporarily lowered salinity below pelagic tolerance.",
                "status": "INACTIVE",
                "inactive_reason": "Freshwater dilution lowered salinity below pelagic tolerance",
                "sst": 27.4,
                "chlorophyll": 0.31,
                "confidence": 39
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate to Rough",
            "wave_height_m": 1.8,
            "wind_speed_kmh": 23.0,
            "wind_direction": "NE (045\u00b0) \u2022 brisk",
            "sst_celsius": 27.9,
            "confidence_pct": 90,
            "departure_recommendation": "05:00\u201308:00 \u2022 Morning tidal window",
            "best_fishing_summary": "Mahanadi estuarine discharge meeting coastal current creating massive bloom"
        },
        "advisories": [
            {
                "id": "adv-par-1",
                "type": "Caution",
                "severity": "Caution",
                "risk_level": "CAUTION",
                "title": "Brisk North-Easterly Sea",
                "description": "1.8m waves across northern Bay of Bengal shelf. Exercise caution."
            }
        ]
    },
    {
        "id": "haldia",
        "name": "Haldia / Diamond Harbour",
        "state": "West Bengal",
        "sector": "North-East (Bengal Bay)",
        "lat": 22.0667,
        "lon": 88.0667,
        "pfz_candidates": [
            {
                "id": "PFZ-HAL-01",
                "zone_code": "HAL-01",
                "name": "Sandheads Oceanic Estuarine Front",
                "lat": 21.65,
                "lon": 88.25,
                "bearing_deg": 157.0,
                "distance_km": 50.1,
                "depth_m": 32.0,
                "target_species": "Tenualosa ilisha (Hilsa), Seabass (Bhetki), Prawns",
                "description": "Famous Sandheads fishing corridor where Hooghly freshwater mixes with Bay of Bengal.",
                "status": "ACTIVE",
                "confidence": 92,
                "sst": 28.0,
                "chlorophyll": 1.4
            },
            {
                "id": "PFZ-HAL-02",
                "zone_code": "HAL-02",
                "name": "Sagar Island South Channel (Inactive)",
                "lat": 21.75,
                "lon": 88.1,
                "bearing_deg": 185.0,
                "distance_km": 28.0,
                "depth_m": 24.0,
                "target_species": "Hilsa, Bhetki",
                "description": "High silt turbidity obstructing plankton photosynthesis.",
                "status": "INACTIVE",
                "inactive_reason": "High silt turbidity obstructing photosynthesis",
                "sst": 28.2,
                "chlorophyll": 0.25,
                "confidence": 37
            }
        ],
        "marine_conditions": {
            "sea_state": "Moderate",
            "wave_height_m": 1.5,
            "wind_speed_kmh": 20.0,
            "wind_direction": "ENE (070\u00b0) \u2022 steady",
            "sst_celsius": 28.0,
            "confidence_pct": 89,
            "departure_recommendation": "05:30\u201309:00 \u2022 High-water navigation window",
            "best_fishing_summary": "Famous Sandheads fishing corridor where Hooghly mixes with Bay of Bengal"
        },
        "advisories": [
            {
                "id": "adv-hal-1",
                "type": "Caution",
                "severity": "Caution",
                "risk_level": "CAUTION",
                "title": "Sandheads Shallow Swell",
                "description": "Shifting sandbars and 1.5m swells along navigation fairway."
            }
        ]
    }
]

PORT_TIDE_PREDICTIONS: Dict[str, Dict[str, Any]] = {
    "veraval": {
        "port_name": "Veraval Fishery Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "03:45", "water_level_m": 4.2, "type": "HIGH TIDE"},
        "low_tide": {"time": "09:30", "water_level_m": 1.1, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "03:45", "water_level_m": 4.2, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "09:30", "water_level_m": 1.1, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "16:05", "water_level_m": 4.4, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "22:15", "water_level_m": 0.9, "date": "11 Sep 2026"}
        ]
    },
    "porbandar": {
        "port_name": "Porbandar Marine Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "03:30", "water_level_m": 3.9, "type": "HIGH TIDE"},
        "low_tide": {"time": "09:15", "water_level_m": 0.9, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "03:30", "water_level_m": 3.9, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "09:15", "water_level_m": 0.9, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "15:50", "water_level_m": 4.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "22:00", "water_level_m": 0.8, "date": "11 Sep 2026"}
        ]
    },
    "okha": {
        "port_name": "Okha Deepsea Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "03:15", "water_level_m": 4.5, "type": "HIGH TIDE"},
        "low_tide": {"time": "09:00", "water_level_m": 1.2, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "03:15", "water_level_m": 4.5, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "09:00", "water_level_m": 1.2, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "15:35", "water_level_m": 4.7, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "21:45", "water_level_m": 1.0, "date": "11 Sep 2026"}
        ]
    },
    "mumbai": {
        "port_name": "Mumbai Harbour (Sassoon Dock)",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "04:12", "water_level_m": 3.8, "type": "HIGH TIDE"},
        "low_tide": {"time": "10:05", "water_level_m": 0.9, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "04:12", "water_level_m": 3.8, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "10:05", "water_level_m": 0.9, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "16:30", "water_level_m": 4.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "22:45", "water_level_m": 0.7, "date": "11 Sep 2026"}
        ]
    },
    "alibaug": {
        "port_name": "Alibaug Fishery Wharf",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "04:20", "water_level_m": 3.7, "type": "HIGH TIDE"},
        "low_tide": {"time": "10:15", "water_level_m": 0.8, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "04:20", "water_level_m": 3.7, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "10:15", "water_level_m": 0.8, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "16:40", "water_level_m": 3.9, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "22:55", "water_level_m": 0.7, "date": "11 Sep 2026"}
        ]
    },
    "ratnagiri": {
        "port_name": "Mirkarwada Port, Ratnagiri",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "04:25", "water_level_m": 2.7, "type": "HIGH TIDE"},
        "low_tide": {"time": "10:35", "water_level_m": 0.8, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "04:25", "water_level_m": 2.7, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "10:35", "water_level_m": 0.8, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "16:45", "water_level_m": 2.9, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "23:05", "water_level_m": 0.6, "date": "11 Sep 2026"}
        ]
    },
    "malvan": {
        "port_name": "Malvan Fishery Harbour",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "04:28", "water_level_m": 2.4, "type": "HIGH TIDE"},
        "low_tide": {"time": "10:40", "water_level_m": 0.7, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "04:28", "water_level_m": 2.4, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "10:40", "water_level_m": 0.7, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "16:50", "water_level_m": 2.6, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "23:10", "water_level_m": 0.5, "date": "11 Sep 2026"}
        ]
    },
    "panaji": {
        "port_name": "Panaji Fishery Port, Goa",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "04:30", "water_level_m": 2.1, "type": "HIGH TIDE"},
        "low_tide": {"time": "10:45", "water_level_m": 0.6, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "04:30", "water_level_m": 2.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "10:45", "water_level_m": 0.6, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "16:55", "water_level_m": 2.3, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "23:15", "water_level_m": 0.5, "date": "11 Sep 2026"}
        ]
    },
    "karwar": {
        "port_name": "Karwar Fishery Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "04:45", "water_level_m": 1.9, "type": "HIGH TIDE"},
        "low_tide": {"time": "11:00", "water_level_m": 0.6, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "04:45", "water_level_m": 1.9, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "11:00", "water_level_m": 0.6, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "17:10", "water_level_m": 2.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "23:30", "water_level_m": 0.5, "date": "11 Sep 2026"}
        ]
    },
    "mangalore": {
        "port_name": "Mangalore Old Fishery Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "05:00", "water_level_m": 1.6, "type": "HIGH TIDE"},
        "low_tide": {"time": "11:15", "water_level_m": 0.5, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "05:00", "water_level_m": 1.6, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "11:15", "water_level_m": 0.5, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "17:25", "water_level_m": 1.8, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "23:45", "water_level_m": 0.4, "date": "11 Sep 2026"}
        ]
    },
    "kochi": {
        "port_name": "Kochi Fishery Harbour",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "05:10", "water_level_m": 1.1, "type": "HIGH TIDE"},
        "low_tide": {"time": "11:20", "water_level_m": 0.4, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "05:10", "water_level_m": 1.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "11:20", "water_level_m": 0.4, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "17:40", "water_level_m": 1.2, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "23:55", "water_level_m": 0.3, "date": "11 Sep 2026"}
        ]
    },
    "kollam": {
        "port_name": "Kollam Port (Thangassery)",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "05:25", "water_level_m": 1.0, "type": "HIGH TIDE"},
        "low_tide": {"time": "11:35", "water_level_m": 0.3, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "05:25", "water_level_m": 1.0, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "11:35", "water_level_m": 0.3, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "17:55", "water_level_m": 1.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "00:10", "water_level_m": 0.3, "date": "12 Sep 2026"}
        ]
    },
    "tuticorin": {
        "port_name": "Thoothukudi (Tuticorin) Fishery Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "05:45", "water_level_m": 1.1, "type": "HIGH TIDE"},
        "low_tide": {"time": "12:00", "water_level_m": 0.4, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "05:45", "water_level_m": 1.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "12:00", "water_level_m": 0.4, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "18:15", "water_level_m": 1.2, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "00:30", "water_level_m": 0.3, "date": "12 Sep 2026"}
        ]
    },
    "chennai": {
        "port_name": "Chennai Fishing Harbour (Kasimedu)",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "06:00", "water_level_m": 1.2, "type": "HIGH TIDE"},
        "low_tide": {"time": "12:15", "water_level_m": 0.4, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "06:00", "water_level_m": 1.2, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "12:15", "water_level_m": 0.4, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "18:30", "water_level_m": 1.3, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "00:45", "water_level_m": 0.3, "date": "12 Sep 2026"}
        ]
    },
    "krishnapatnam": {
        "port_name": "Krishnapatnam Deep Sea Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "05:50", "water_level_m": 1.3, "type": "HIGH TIDE"},
        "low_tide": {"time": "12:05", "water_level_m": 0.5, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "05:50", "water_level_m": 1.3, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "12:05", "water_level_m": 0.5, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "18:20", "water_level_m": 1.4, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "00:35", "water_level_m": 0.4, "date": "12 Sep 2026"}
        ]
    },
    "kakinada": {
        "port_name": "Kakinada Fishery Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "05:45", "water_level_m": 1.4, "type": "HIGH TIDE"},
        "low_tide": {"time": "11:55", "water_level_m": 0.5, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "05:45", "water_level_m": 1.4, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "11:55", "water_level_m": 0.5, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "18:10", "water_level_m": 1.5, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "00:25", "water_level_m": 0.4, "date": "12 Sep 2026"}
        ]
    },
    "visakhapatnam": {
        "port_name": "Visakhapatnam Fishery Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "05:40", "water_level_m": 1.5, "type": "HIGH TIDE"},
        "low_tide": {"time": "11:50", "water_level_m": 0.5, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "05:40", "water_level_m": 1.5, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "11:50", "water_level_m": 0.5, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "18:05", "water_level_m": 1.6, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "00:20", "water_level_m": 0.4, "date": "12 Sep 2026"}
        ]
    },
    "paradip": {
        "port_name": "Paradip Fishery Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "06:25", "water_level_m": 2.4, "type": "HIGH TIDE"},
        "low_tide": {"time": "12:40", "water_level_m": 0.8, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "06:25", "water_level_m": 2.4, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "12:40", "water_level_m": 0.8, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "18:50", "water_level_m": 2.6, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "01:05", "water_level_m": 0.6, "date": "12 Sep 2026"}
        ]
    },
    "dhamra": {
        "port_name": "Dhamra Marine Port",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "06:40", "water_level_m": 3.1, "type": "HIGH TIDE"},
        "low_tide": {"time": "12:55", "water_level_m": 1.0, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "06:40", "water_level_m": 3.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "12:55", "water_level_m": 1.0, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "19:05", "water_level_m": 3.3, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "01:20", "water_level_m": 0.8, "date": "12 Sep 2026"}
        ]
    },
    "haldia": {
        "port_name": "Haldia & Diamond Harbour, West Bengal",
        "source": "Survey of India Tide Gauge & Harmonic Model",
        "status": "prediction",
        "high_tide": {"time": "07:15", "water_level_m": 4.8, "type": "HIGH TIDE"},
        "low_tide": {"time": "13:30", "water_level_m": 1.4, "type": "LOW TIDE"},
        "events": [
            {"type": "HIGH TIDE", "time": "07:15", "water_level_m": 4.8, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "13:30", "water_level_m": 1.4, "date": "11 Sep 2026"},
            {"type": "HIGH TIDE", "time": "19:40", "water_level_m": 5.1, "date": "11 Sep 2026"},
            {"type": "LOW TIDE", "time": "01:55", "water_level_m": 1.1, "date": "12 Sep 2026"}
        ]
    }
}

PORT_WEATHER_CONDITIONS: Dict[str, Dict[str, Any]] = {
    "veraval": {"weather_label": "Partly Cloudy", "precipitation_mm": 0.0, "rain_probability_pct": 10, "rain_intensity": "None", "air_temp_c": 28.5},
    "porbandar": {"weather_label": "Breezy & Fair", "precipitation_mm": 0.0, "rain_probability_pct": 15, "rain_intensity": "None", "air_temp_c": 28.2},
    "okha": {"weather_label": "Clear Coastal Horizon", "precipitation_mm": 0.0, "rain_probability_pct": 5, "rain_intensity": "None", "air_temp_c": 28.0},
    "mumbai": {"weather_label": "Passing Marine Showers", "precipitation_mm": 0.8, "rain_probability_pct": 35, "rain_intensity": "Light", "air_temp_c": 28.6},
    "alibaug": {"weather_label": "Scattered Clouds", "precipitation_mm": 0.2, "rain_probability_pct": 25, "rain_intensity": "Light", "air_temp_c": 28.3},
    "ratnagiri": {"weather_label": "Sunny & Calm", "precipitation_mm": 0.0, "rain_probability_pct": 10, "rain_intensity": "None", "air_temp_c": 27.8},
    "malvan": {"weather_label": "Clear Coastline", "precipitation_mm": 0.0, "rain_probability_pct": 10, "rain_intensity": "None", "air_temp_c": 28.1},
    "panaji": {"weather_label": "Squally Rain Showers", "precipitation_mm": 4.5, "rain_probability_pct": 65, "rain_intensity": "Moderate", "air_temp_c": 29.1},
    "karwar": {"weather_label": "Overcast", "precipitation_mm": 1.2, "rain_probability_pct": 40, "rain_intensity": "Light", "air_temp_c": 28.4},
    "mangalore": {"weather_label": "Passing Showers", "precipitation_mm": 2.0, "rain_probability_pct": 50, "rain_intensity": "Light", "air_temp_c": 28.7},
    "kochi": {"weather_label": "Tropical Marine Rain", "precipitation_mm": 5.8, "rain_probability_pct": 75, "rain_intensity": "Moderate", "air_temp_c": 28.9},
    "kollam": {"weather_label": "Scattered Drizzle", "precipitation_mm": 1.5, "rain_probability_pct": 45, "rain_intensity": "Light", "air_temp_c": 28.5},
    "tuticorin": {"weather_label": "Fair & Windy", "precipitation_mm": 0.0, "rain_probability_pct": 15, "rain_intensity": "None", "air_temp_c": 29.8},
    "chennai": {"weather_label": "Coastal Haze & Fair", "precipitation_mm": 0.0, "rain_probability_pct": 20, "rain_intensity": "None", "air_temp_c": 30.2},
    "krishnapatnam": {"weather_label": "Clear Skies", "precipitation_mm": 0.0, "rain_probability_pct": 10, "rain_intensity": "None", "air_temp_c": 29.9},
    "kakinada": {"weather_label": "Partly Overcast", "precipitation_mm": 0.5, "rain_probability_pct": 30, "rain_intensity": "Light", "air_temp_c": 29.5},
    "visakhapatnam": {"weather_label": "Passing Marine Clouds", "precipitation_mm": 0.0, "rain_probability_pct": 20, "rain_intensity": "None", "air_temp_c": 29.3},
    "paradip": {"weather_label": "Squall Alert & Rain", "precipitation_mm": 7.2, "rain_probability_pct": 80, "rain_intensity": "Heavy Squall", "air_temp_c": 28.2},
    "dhamra": {"weather_label": "Overcast & Drizzle", "precipitation_mm": 3.1, "rain_probability_pct": 60, "rain_intensity": "Moderate", "air_temp_c": 28.0},
    "haldia": {"weather_label": "Monsoon Front & Choppy", "precipitation_mm": 6.4, "rain_probability_pct": 75, "rain_intensity": "Moderate", "air_temp_c": 28.4}
}

def get_port_by_id(port_id: str) -> Dict[str, Any]:
    """Retrieve port dictionary by ID, defaulting to Mumbai if not found."""
    clean_id = (port_id or "mumbai").lower().strip()
    for port in INDIAN_COASTAL_PORTS:
        if port["id"] == clean_id:
            return port
    return INDIAN_COASTAL_PORTS[3]  # default to Mumbai

def get_port_tide_info(port_id: str) -> Dict[str, Any]:
    """Retrieve authentic tide gauge predictions for a given port."""
    clean_id = (port_id or "mumbai").lower().strip()
    if clean_id in PORT_TIDE_PREDICTIONS:
        return PORT_TIDE_PREDICTIONS[clean_id]
    return PORT_TIDE_PREDICTIONS["mumbai"]

def get_port_weather_info(port_id: str) -> Dict[str, Any]:
    """Retrieve localized meteorological and rain telemetry for a given port."""
    clean_id = (port_id or "mumbai").lower().strip()
    if clean_id in PORT_WEATHER_CONDITIONS:
        return PORT_WEATHER_CONDITIONS[clean_id]
    return PORT_WEATHER_CONDITIONS["mumbai"]

def get_port_dashboard_context(port_id: str) -> Dict[str, Any]:
    """Retrieve comprehensive port-specific dashboard context, conditions, advisories, PFZs, tide, and rain."""
    port = get_port_by_id(port_id)
    cands = port.get("pfz_candidates", [])
    active = [c for c in cands if c.get("status") == "ACTIVE"]
    inactive = [c for c in cands if c.get("status") == "INACTIVE"]
    tide = get_port_tide_info(port["id"])
    rain = get_port_weather_info(port["id"])
    
    # Merge rain and tide into marine_conditions
    marine_conds = dict(port.get("marine_conditions", {}))
    marine_conds["precipitation_mm"] = rain["precipitation_mm"]
    marine_conds["rain_probability_pct"] = rain["rain_probability_pct"]
    marine_conds["rain_intensity"] = rain["rain_intensity"]
    marine_conds["weather_label"] = rain["weather_label"]

    return {
        "port_id": port["id"],
        "name": port["name"],
        "state": port["state"],
        "sector": port["sector"],
        "lat": port["lat"],
        "lon": port["lon"],
        "marine_conditions": marine_conds,
        "advisories": port.get("advisories", []),
        "pfz_candidates": cands,
        "active_pfzs": active,
        "inactive_pfzs": inactive,
        "tide_information": tide,
        "rain_data": rain
    }

def get_all_pfz_candidates() -> List[Dict[str, Any]]:
    """Flatten all PFZ candidates across all ports with parent port metadata."""
    all_pfzs = []
    for port in INDIAN_COASTAL_PORTS:
        for pfz in port.get("pfz_candidates", []):
            entry = dict(pfz)
            entry["port_id"] = port["id"]
            entry["port_name"] = port["name"]
            entry["sector"] = port["sector"]
            entry["state"] = port["state"]
            all_pfzs.append(entry)
    return all_pfzs

