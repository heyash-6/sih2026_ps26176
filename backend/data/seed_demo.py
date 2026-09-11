import os
import sys
from datetime import date, datetime, timedelta, timezone
from shapely.geometry import Polygon, Point
from geoalchemy2.shape import from_shape

# Ensure backend root is on sys.path for database imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.connection import SessionLocal, engine, Base
from database.models import PFZZone, HazardZone, RestrictedZone, MarineCondition

DEMO_SOURCE = "SYNTHETIC DEMO DATA"


def seed_demo_data():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # Prevent duplicates: remove previous synthetic demo records if they exist
        session.query(PFZZone).filter(PFZZone.source == DEMO_SOURCE).delete()
        session.query(HazardZone).filter(HazardZone.source == DEMO_SOURCE).delete()
        session.query(RestrictedZone).filter(RestrictedZone.source == DEMO_SOURCE).delete()
        session.query(MarineCondition).delete()
        session.commit()

        today = date.today()
        now = datetime.now(timezone.utc)

        # 1. PFZ Zones (8 zones along the Western Coast of India / Arabian Sea)
        # Note: Coordinates are in [longitude, latitude] order for EPSG:4326
        pfz_data = [
            {
                "name": "PFZ Alpha - Mumbai Offshore",
                "coords": [(71.6, 18.8), (72.2, 18.8), (72.2, 19.3), (71.6, 19.3), (71.6, 18.8)],
                "sst": 28.4,
                "chlorophyll": 1.85,
                "suitability_score": 0.88,
            },
            {
                "name": "PFZ Beta - Ratnagiri Shelf",
                "coords": [(72.2, 16.6), (72.8, 16.6), (72.8, 17.1), (72.2, 17.1), (72.2, 16.6)],
                "sst": 28.1,
                "chlorophyll": 2.10,
                "suitability_score": 0.92,
            },
            {
                "name": "PFZ Gamma - Goa Deep Waters",
                "coords": [(72.5, 15.1), (73.1, 15.1), (73.1, 15.6), (72.5, 15.6), (72.5, 15.1)],
                "sst": 28.6,
                "chlorophyll": 1.60,
                "suitability_score": 0.82,
            },
            {
                "name": "PFZ Delta - Karwar Bank",
                "coords": [(73.0, 14.3), (73.6, 14.3), (73.6, 14.8), (73.0, 14.8), (73.0, 14.3)],
                "sst": 28.2,
                "chlorophyll": 1.95,
                "suitability_score": 0.86,
            },
            {
                "name": "PFZ Epsilon - Mangalore Offshore",
                "coords": [(73.5, 12.6), (74.1, 12.6), (74.1, 13.1), (73.5, 13.1), (73.5, 12.6)],
                "sst": 28.7,
                "chlorophyll": 2.30,
                "suitability_score": 0.91,
            },
            {
                "name": "PFZ Zeta - Malabar Coast",
                "coords": [(74.4, 10.2), (75.1, 10.2), (75.1, 10.8), (74.4, 10.8), (74.4, 10.2)],
                "sst": 29.0,
                "chlorophyll": 2.45,
                "suitability_score": 0.94,
            },
            {
                "name": "PFZ Eta - Saurashtra South",
                "coords": [(69.9, 20.3), (70.6, 20.3), (70.6, 20.9), (69.9, 20.9), (69.9, 20.3)],
                "sst": 27.9,
                "chlorophyll": 1.40,
                "suitability_score": 0.79,
            },
            {
                "name": "PFZ Theta - Porbandar Outer Shelf",
                "coords": [(68.9, 21.1), (69.6, 21.1), (69.6, 21.7), (68.9, 21.7), (68.9, 21.1)],
                "sst": 27.6,
                "chlorophyll": 1.55,
                "suitability_score": 0.84,
            },
        ]

        pfz_records = [
            PFZZone(
                name=item["name"],
                geometry=from_shape(Polygon(item["coords"]), srid=4326),
                observation_date=today,
                sst=item["sst"],
                chlorophyll=item["chlorophyll"],
                suitability_score=item["suitability_score"],
                source=DEMO_SOURCE,
            )
            for item in pfz_data
        ]
        session.add_all(pfz_records)

        # 2. Hazard Zones (5 polygon zones)
        hazard_data = [
            {
                "hazard_type": "Rough Sea / High Swell",
                "severity": 4,
                "coords": [(71.0, 17.5), (71.8, 17.5), (71.8, 18.2), (71.0, 18.2), (71.0, 17.5)],
                "valid_from": now,
                "valid_until": now + timedelta(days=2),
            },
            {
                "hazard_type": "Cyclonic Eddy Warning",
                "severity": 3,
                "coords": [(69.5, 19.5), (70.5, 19.5), (70.5, 20.2), (69.5, 20.2), (69.5, 19.5)],
                "valid_from": now,
                "valid_until": now + timedelta(days=3),
            },
            {
                "hazard_type": "Submerged Shoal / Shallow Reef",
                "severity": 5,
                "coords": [(72.7, 15.8), (73.0, 15.8), (73.0, 16.1), (72.7, 16.1), (72.7, 15.8)],
                "valid_from": now - timedelta(days=30),
                "valid_until": now + timedelta(days=365),
            },
            {
                "hazard_type": "Dense Fog & Low Visibility",
                "severity": 2,
                "coords": [(68.5, 21.8), (69.4, 21.8), (69.4, 22.4), (68.5, 22.4), (68.5, 21.8)],
                "valid_from": now,
                "valid_until": now + timedelta(days=1),
            },
            {
                "hazard_type": "Strong Tidal Currents",
                "severity": 3,
                "coords": [(72.1, 19.8), (72.6, 19.8), (72.6, 20.3), (72.1, 20.3), (72.1, 19.8)],
                "valid_from": now,
                "valid_until": now + timedelta(days=2),
            },
        ]

        hazard_records = [
            HazardZone(
                hazard_type=item["hazard_type"],
                severity=item["severity"],
                geometry=from_shape(Polygon(item["coords"]), srid=4326),
                valid_from=item["valid_from"],
                valid_until=item["valid_until"],
                source=DEMO_SOURCE,
            )
            for item in hazard_data
        ]
        session.add_all(hazard_records)

        # 3. Restricted Zones (3 polygon zones)
        restricted_data = [
            {
                "name": "Malvan Marine Sanctuary Buffer",
                "zone_type": "Marine Protected Area",
                "coords": [(73.35, 15.95), (73.55, 15.95), (73.55, 16.15), (73.35, 16.15), (73.35, 15.95)],
            },
            {
                "name": "Western Naval Exercise Corridor",
                "zone_type": "Military Exclusion",
                "coords": [(70.5, 14.5), (71.8, 14.5), (71.8, 15.5), (70.5, 15.5), (70.5, 14.5)],
            },
            {
                "name": "Mumbai High Rig Safety Perimeter",
                "zone_type": "Safety Exclusion",
                "coords": [(71.2, 19.2), (71.5, 19.2), (71.5, 19.6), (71.2, 19.6), (71.2, 19.2)],
            },
        ]

        restricted_records = [
            RestrictedZone(
                name=item["name"],
                zone_type=item["zone_type"],
                geometry=from_shape(Polygon(item["coords"]), srid=4326),
                source=DEMO_SOURCE,
            )
            for item in restricted_data
        ]
        session.add_all(restricted_records)

        # 4. Marine Conditions (7 point observations across Arabian Sea)
        condition_data = [
            {"point": (72.0, 19.0), "wind_speed": 18.5, "wave_height": 2.1, "rainfall": 4.2, "risk_score": 0.42},
            {"point": (72.5, 17.0), "wind_speed": 24.0, "wave_height": 3.2, "rainfall": 12.0, "risk_score": 0.68},
            {"point": (73.0, 15.5), "wind_speed": 14.0, "wave_height": 1.5, "rainfall": 0.0, "risk_score": 0.25},
            {"point": (73.5, 13.5), "wind_speed": 16.2, "wave_height": 1.8, "rainfall": 2.5, "risk_score": 0.32},
            {"point": (74.5, 10.5), "wind_speed": 28.5, "wave_height": 3.8, "rainfall": 18.5, "risk_score": 0.85},
            {"point": (70.2, 20.5), "wind_speed": 12.0, "wave_height": 1.2, "rainfall": 0.0, "risk_score": 0.18},
            {"point": (69.2, 21.5), "wind_speed": 21.0, "wave_height": 2.6, "rainfall": 6.0, "risk_score": 0.55},
        ]

        condition_records = [
            MarineCondition(
                timestamp=now,
                geometry=from_shape(Point(item["point"]), srid=4326),
                wind_speed=item["wind_speed"],
                wave_height=item["wave_height"],
                rainfall=item["rainfall"],
                risk_score=item["risk_score"],
            )
            for item in condition_data
        ]
        session.add_all(condition_records)

        session.commit()

        # Print record counts
        print("=== Database Seeding Complete ===")
        print(f"PFZ Zones inserted: {len(pfz_records)}")
        print(f"Hazard Zones inserted: {len(hazard_records)}")
        print(f"Restricted Zones inserted: {len(restricted_records)}")
        print(f"Marine Conditions inserted: {len(condition_records)}")

    except Exception as e:
        session.rollback()
        print(f"Error seeding demo data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_demo_data()
