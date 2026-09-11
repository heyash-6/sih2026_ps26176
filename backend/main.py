from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import Base, engine
from database.models import PFZZone, HazardZone, RestrictedZone, MarineCondition
from api.pfz import router as pfz_router
from api.hazards import router as hazards_router
from api.geofence import router as geofence_router
from api.routing import router as routing_router, navigation_router

# Create database tables in PostgreSQL/PostGIS
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ORCA - GIS & Navigation Backend",
    description="Backend service for GIS and Marine Navigation for Project ORCA",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pfz_router)
app.include_router(hazards_router)
app.include_router(geofence_router)
app.include_router(routing_router)
app.include_router(navigation_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
