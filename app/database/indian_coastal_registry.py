"""
Indian Coastal Ports and Offshore Potential Fishing Zones (PFZ) Registry.
Covers both West and East coasts: Gujarat, Maharashtra, Goa, Karnataka, Kerala, Tamil Nadu, Andhra Pradesh, Odisha, West Bengal.
"""
from typing import List, Dict, Any

INDIAN_COASTAL_PORTS: List[Dict[str, Any]] = [
    # --- GUJARAT (North-West) ---
    {
        "id": "veraval",
        "name": "Veraval Fishery Port",
        "state": "Gujarat",
        "sector": "North-West (Gujarat)",
        "lat": 20.9000,
        "lon": 70.3667,
        "pfz_candidates": [
            {
                "id": "PFZ-VER-01",
                "zone_code": "VER-01",
                "name": "Veraval Southwest Shelf Break",
                "lat": 20.7200,
                "lon": 70.1500,
                "bearing_deg": 230.0,
                "distance_km": 28.4,
                "depth_m": 45.0,
                "target_species": "Silver Pomfret, Ribbonfish, Croakers",
                "description": "High thermal gradient along the 50m isobath shelf break."
            },
            {
                "id": "PFZ-VER-02",
                "zone_code": "VER-02",
                "name": "Saurashtra Offshore Pelagic Front",
                "lat": 20.8100,
                "lon": 69.9800,
                "bearing_deg": 250.0,
                "distance_km": 41.5,
                "depth_m": 68.0,
                "target_species": "Indian Mackerel, Seer Fish, Squid",
                "description": "Chlorophyll-a aggregation zone driven by coastal upwelling."
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
                "lat": 21.4800,
                "lon": 69.4100,
                "bearing_deg": 232.0,
                "distance_km": 28.5,
                "depth_m": 52.0,
                "target_species": "Hilsa, Black Pomfret, Ribbonfish",
                "description": "Strong thermal front observed between 26°C coastal and 28°C open sea waters."
            },
            {
                "id": "PFZ-POR-02",
                "zone_code": "POR-02",
                "name": "Dwarka-Porbandar Deep Trench",
                "lat": 21.3600,
                "lon": 69.2400,
                "bearing_deg": 240.0,
                "distance_km": 50.5,
                "depth_m": 85.0,
                "target_species": "Yellowfin Tuna, Skipjack, Barracuda",
                "description": "Deep pelagic chlorophyll eddy."
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
                "lat": 22.3800,
                "lon": 68.7900,
                "bearing_deg": 255.0,
                "distance_km": 30.1,
                "depth_m": 42.0,
                "target_species": "Jewfish, Threadfin, Prawns",
                "description": "Tidal convergence and nutrient-rich estuarine plume."
            }
        ]
    },

    # --- MAHARASHTRA (West Coast) ---
    {
        "id": "mumbai",
        "name": "Mumbai Harbour (Sassoon Docks)",
        "state": "Maharashtra",
        "sector": "West Coast (Maharashtra)",
        "lat": 18.9400,
        "lon": 72.8300,
        "pfz_candidates": [
            {
                "id": "PFZ-MUM-01",
                "zone_code": "MUM-01",
                "name": "Mumbai Continental Shelf Edge",
                "lat": 18.9800,
                "lon": 72.5800,
                "bearing_deg": 280.0,
                "distance_km": 26.7,
                "depth_m": 38.0,
                "target_species": "Bombay Duck, Mackerel, Pomfret",
                "description": "Persistent thermal boundary with high chlorophyll density."
            },
            {
                "id": "PFZ-MUM-02",
                "zone_code": "MUM-02",
                "name": "Alibaug-Mumbai South Bank",
                "lat": 18.8200,
                "lon": 72.6200,
                "bearing_deg": 235.0,
                "distance_km": 25.8,
                "depth_m": 44.0,
                "target_species": "Seer Fish, Croakers, Squid",
                "description": "Meandering SST filament indicating productive feeding zone."
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
                "lat": 18.5800,
                "lon": 72.6400,
                "bearing_deg": 255.0,
                "distance_km": 25.5,
                "depth_m": 35.0,
                "target_species": "Ribbonfish, White Prawns, Sardines",
                "description": "Plankton bloom supported by estuarine nutrient runoff."
            }
        ]
    },
    {
        "id": "ratnagiri",
        "name": "Ratnagiri Fishery Port (Mirkarwada)",
        "state": "Maharashtra",
        "sector": "West Coast (Maharashtra)",
        "lat": 16.9902,
        "lon": 73.3120,
        "pfz_candidates": [
            {
                "id": "PFZ-RAT-01",
                "zone_code": "RAT-01",
                "name": "Mirkarwada West Pelagic Belt",
                "lat": 16.9200,
                "lon": 73.0800,
                "bearing_deg": 252.0,
                "distance_km": 26.0,
                "depth_m": 48.0,
                "target_species": "Kingfish, Horse Mackerel, Squid",
                "description": "Well-defined cyclonic eddy with optimal 28.1°C surface temperature."
            },
            {
                "id": "PFZ-RAT-02",
                "zone_code": "RAT-02",
                "name": "Jaigad Deep Slope PFZ",
                "lat": 17.1000,
                "lon": 73.0200,
                "bearing_deg": 295.0,
                "distance_km": 33.4,
                "depth_m": 72.0,
                "target_species": "Tuna, Seer Fish, Barracuda",
                "description": "Sharp boundary of oceanic chlorophyll-a front."
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
                "lat": 15.9800,
                "lon": 73.2800,
                "bearing_deg": 246.0,
                "distance_km": 22.0,
                "depth_m": 50.0,
                "target_species": "Indian Mackerel, Rock Cod, Reef Snappers",
                "description": "Clear water convergence zone adjacent to coral shelf."
            }
        ]
    },

    # --- GOA (South-West) ---
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
                "lat": 15.4200,
                "lon": 73.5600,
                "bearing_deg": 252.0,
                "distance_km": 30.0,
                "depth_m": 54.0,
                "target_species": "Oil Sardine, Mackerel, Squid",
                "description": "High chlorophyll density from sustained seasonal upwelling."
            },
            {
                "id": "PFZ-GOA-02",
                "zone_code": "GOA-02",
                "name": "Aguada-Anjuna Deep Slope",
                "lat": 15.6100,
                "lon": 73.5100,
                "bearing_deg": 291.0,
                "distance_km": 36.2,
                "depth_m": 65.0,
                "target_species": "Tuna, Seer Fish, Solenocera Prawns",
                "description": "Distinct thermal divergence supporting pelagic schools."
            }
        ]
    },

    # --- KARNATAKA (South-West) ---
    {
        "id": "karwar",
        "name": "Karwar Fishery Port (Baithkol)",
        "state": "Karnataka",
        "sector": "South-West (Karnataka)",
        "lat": 14.8050,
        "lon": 74.1240,
        "pfz_candidates": [
            {
                "id": "PFZ-KAR-01",
                "zone_code": "KAR-01",
                "name": "Kali Estuary Convergence PFZ",
                "lat": 14.7200,
                "lon": 73.9100,
                "bearing_deg": 246.0,
                "distance_km": 25.0,
                "depth_m": 42.0,
                "target_species": "Oil Sardine, Silver Belly, Cuttlefish",
                "description": "Sub-surface cold tongue with rich zooplankton abundance."
            }
        ]
    },
    {
        "id": "mangalore",
        "name": "Mangalore Fishery Port (Old Port / Bunder)",
        "state": "Karnataka",
        "sector": "South-West (Karnataka)",
        "lat": 12.8580,
        "lon": 74.8360,
        "pfz_candidates": [
            {
                "id": "PFZ-MNG-01",
                "zone_code": "MNG-01",
                "name": "Netravati Offshore Shelf PFZ",
                "lat": 12.7800,
                "lon": 74.5800,
                "bearing_deg": 252.0,
                "distance_km": 29.2,
                "depth_m": 50.0,
                "target_species": "Indian Mackerel, Ribbonfish, Sole Fish",
                "description": "Sustained high primary productivity along 40-50m depth contour."
            },
            {
                "id": "PFZ-MNG-02",
                "zone_code": "MNG-02",
                "name": "Malpe-Mangalore Outer Trench",
                "lat": 12.9600,
                "lon": 74.5200,
                "bearing_deg": 290.0,
                "distance_km": 36.1,
                "depth_m": 78.0,
                "target_species": "Yellowfin Tuna, Bonito, Queenfish",
                "description": "Deep-water thermal front with active baitfish aggregations."
            }
        ]
    },

    # --- KERALA (South-West) ---
    {
        "id": "kochi",
        "name": "Cochin Fishery Harbour (Thoppumpady)",
        "state": "Kerala",
        "sector": "South-West (Kerala)",
        "lat": 9.9650,
        "lon": 76.2620,
        "pfz_candidates": [
            {
                "id": "PFZ-KCH-01",
                "zone_code": "KCH-01",
                "name": "Cochin Mud Bank Outer Fringe",
                "lat": 9.8800,
                "lon": 76.0100,
                "bearing_deg": 252.0,
                "distance_km": 29.2,
                "depth_m": 36.0,
                "target_species": "Oil Sardine, Indian Mackerel, Karikkadi Prawns",
                "description": "Traditional high-yield mud bank zone with massive plankton density."
            },
            {
                "id": "PFZ-KCH-02",
                "zone_code": "KCH-02",
                "name": "Vypin Deep Continental Slope",
                "lat": 10.0800,
                "lon": 75.9800,
                "bearing_deg": 293.0,
                "distance_km": 33.4,
                "depth_m": 70.0,
                "target_species": "Yellowfin Tuna, Skipjack, Threadfin Bream",
                "description": "Clear thermal gradient with high chlorophyll-a concentration."
            }
        ]
    },
    {
        "id": "kollam",
        "name": "Kollam Neendakara Harbour",
        "state": "Kerala",
        "sector": "South-West (Kerala)",
        "lat": 8.9440,
        "lon": 76.5360,
        "pfz_candidates": [
            {
                "id": "PFZ-KLM-01",
                "zone_code": "KLM-01",
                "name": "Ashtamudi Deep Offshore PFZ",
                "lat": 8.8600,
                "lon": 76.3200,
                "bearing_deg": 247.0,
                "distance_km": 25.5,
                "depth_m": 45.0,
                "target_species": "Deep-sea Prawns, Cephalopods, Anchovies",
                "description": "Nutrient plume converging with coastal south-flowing current."
            }
        ]
    },

    # --- TAMIL NADU (South Coast & Coromandel) ---
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
                "lat": 7.9200,
                "lon": 77.4200,
                "bearing_deg": 215.0,
                "distance_km": 22.8,
                "depth_m": 55.0,
                "target_species": "Skipjack Tuna, Perches, Rock Cod",
                "description": "Tri-sea confluence zone creating one of India's richest fishing grounds."
            },
            {
                "id": "PFZ-KAN-02",
                "zone_code": "KAN-02",
                "name": "Cape Comorin East Ledge",
                "lat": 8.0100,
                "lon": 77.7200,
                "bearing_deg": 115.0,
                "distance_km": 22.1,
                "depth_m": 48.0,
                "target_species": "Seer Fish, Carangids, Flying Fish",
                "description": "SST frontal zone between Arabian Sea and Gulf of Mannar."
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
                "lat": 8.7100,
                "lon": 78.3600,
                "bearing_deg": 105.0,
                "distance_km": 25.6,
                "depth_m": 52.0,
                "target_species": "Lethrinids (Pig-face Bream), Barracuda, Prawns",
                "description": "Biosphere-fringe oceanic trench with rich phytoplankton density."
            },
            {
                "id": "PFZ-TUT-02",
                "zone_code": "TUT-02",
                "name": "Pearl Bank Offshore Ridge",
                "lat": 8.8900,
                "lon": 78.4200,
                "bearing_deg": 65.0,
                "distance_km": 34.3,
                "depth_m": 64.0,
                "target_species": "Seer Fish, Tuna, Snappers",
                "description": "Reef-edge convergence front."
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
                "lat": 10.7200,
                "lon": 80.1200,
                "bearing_deg": 99.0,
                "distance_km": 30.8,
                "depth_m": 42.0,
                "target_species": "Hilsa, Pomfret, Tiger Prawns",
                "description": "Chlorophyll plume generated by Cauvery river basin discharge."
            }
        ]
    },
    {
        "id": "chennai",
        "name": "Chennai Kasimedu Fishery Harbour",
        "state": "Tamil Nadu",
        "sector": "South-East (Coromandel)",
        "lat": 13.1250,
        "lon": 80.2980,
        "pfz_candidates": [
            {
                "id": "PFZ-CHN-01",
                "zone_code": "CHN-01",
                "name": "Kasimedu Offshore Pelagic Front",
                "lat": 13.1800,
                "lon": 80.5600,
                "bearing_deg": 76.0,
                "distance_km": 29.0,
                "depth_m": 48.0,
                "target_species": "Seer Fish, Ribbonfish, Trevally",
                "description": "Pronounced thermal boundary between nearshore and Bay of Bengal shelf."
            },
            {
                "id": "PFZ-CHN-02",
                "zone_code": "CHN-02",
                "name": "Coromandel Deep Continental Slope",
                "lat": 13.0100,
                "lon": 80.5900,
                "bearing_deg": 113.0,
                "distance_km": 34.2,
                "depth_m": 85.0,
                "target_species": "Yellowfin Tuna, Sailfish, Barracuda",
                "description": "Deep blue water thermal front with high chlorophyll boundary."
            }
        ]
    },

    # --- ANDHRA PRADESH (East Coast) ---
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
                "lat": 16.8900,
                "lon": 82.5200,
                "bearing_deg": 112.0,
                "distance_km": 31.1,
                "depth_m": 46.0,
                "target_species": "Croakers, Ribbonfish, Tiger Prawns",
                "description": "Rich nutrient confluence from Godavari river delta."
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
                "lat": 17.6200,
                "lon": 83.4900,
                "bearing_deg": 105.0,
                "distance_km": 29.8,
                "depth_m": 60.0,
                "target_species": "Yellowfin Tuna, Skipjack, Threadfin Bream",
                "description": "Submarine canyon upwelling bringing nutrient-rich deep water to surface."
            },
            {
                "id": "PFZ-VIZ-02",
                "zone_code": "VIZ-02",
                "name": "Bheemunipatnam Offshore Ridge",
                "lat": 17.8100,
                "lon": 83.5200,
                "bearing_deg": 61.0,
                "distance_km": 35.0,
                "depth_m": 92.0,
                "target_species": "Seer Fish, Billfish, Carangids",
                "description": "Persistent chlorophyll front along the 100m contour line."
            }
        ]
    },

    # --- ODISHA (East Coast) ---
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
                "lat": 20.1200,
                "lon": 86.9400,
                "bearing_deg": 116.0,
                "distance_km": 32.8,
                "depth_m": 38.0,
                "target_species": "Hilsa, Silver Pomfret, Catfish",
                "description": "Mahanadi estuarine discharge meeting coastal current creating massive plankton bloom."
            },
            {
                "id": "PFZ-PAR-02",
                "zone_code": "PAR-02",
                "name": "Wheeler-Paradip Continental Edge",
                "lat": 20.3800,
                "lon": 87.0100,
                "bearing_deg": 70.0,
                "distance_km": 38.1,
                "depth_m": 65.0,
                "target_species": "Tuna, Ribbonfish, Horse Mackerel",
                "description": "Deep shelf thermal boundary in Northern Bay of Bengal."
            }
        ]
    },

    # --- WEST BENGAL (North-East) ---
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
                "lat": 21.6500,
                "lon": 88.2500,
                "bearing_deg": 157.0,
                "distance_km": 50.1,
                "depth_m": 32.0,
                "target_species": "Tenualosa ilisha (Hilsa), Seabass (Bhetki), Prawns",
                "description": "Famous Sandheads fishing corridor where Hooghly freshwater mixes with Bay of Bengal."
            }
        ]
    }
]

def get_port_by_id(port_id: str) -> Dict[str, Any]:
    """Retrieve port dictionary by ID, defaulting to Mumbai if not found."""
    clean_id = (port_id or "mumbai").lower().strip()
    for port in INDIAN_COASTAL_PORTS:
        if port["id"] == clean_id:
            return port
    return INDIAN_COASTAL_PORTS[3]  # default to Mumbai

def get_all_pfz_candidates() -> List[Dict[str, Any]]:
    """Flatten all PFZ candidates across all ports with parent port metadata."""
    all_pfzs = []
    for port in INDIAN_COASTAL_PORTS:
        for pfz in port["pfz_candidates"]:
            entry = dict(pfz)
            entry["port_id"] = port["id"]
            entry["port_name"] = port["name"]
            entry["sector"] = port["sector"]
            entry["state"] = port["state"]
            all_pfzs.append(entry)
    return all_pfzs
