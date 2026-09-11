from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from geoalchemy2 import Geometry
from database.connection import Base


class PFZZone(Base):
    __tablename__ = "pfz_zones"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    geometry = Column(Geometry("POLYGON", srid=4326))
    observation_date = Column(Date)
    sst = Column(Float)
    chlorophyll = Column(Float)
    suitability_score = Column(Float)
    source = Column(String)


class HazardZone(Base):
    __tablename__ = "hazard_zones"

    id = Column(Integer, primary_key=True)
    hazard_type = Column(String)
    severity = Column(Integer)
    geometry = Column(Geometry("POLYGON", srid=4326))
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    source = Column(String)


class RestrictedZone(Base):
    __tablename__ = "restricted_zones"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    zone_type = Column(String)
    geometry = Column(Geometry("POLYGON", srid=4326))
    source = Column(String)


class MarineCondition(Base):
    __tablename__ = "marine_conditions"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    geometry = Column(Geometry("POINT", srid=4326))
    wind_speed = Column(Float)
    wave_height = Column(Float)
    rainfall = Column(Float)
    risk_score = Column(Float)
