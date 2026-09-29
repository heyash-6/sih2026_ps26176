import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class RiskWeights(BaseModel):
    wave: float = 0.30
    wind: float = 0.20
    hazard: float = 0.30
    distance_duration: float = 0.10
    geofence: float = 0.10

class Settings(BaseModel):
    orca_mode: str = os.getenv("ORCA_MODE", "live")
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")  # gemini, openai, or mock
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    max_candidates: int = int(os.getenv("ORCA_MAX_CANDIDATES", "5"))
    default_vessel_speed_kmh: float = float(os.getenv("ORCA_DEFAULT_VESSEL_SPEED_KMH", "15.0"))
    
    # Supabase Database & Auth Settings
    supabase_url: str = os.getenv("SUPABASE_URL", "https://byikekhtwiewlpxbuwgo.supabase.co")
    supabase_anon_key: str = os.getenv(
        "SUPABASE_ANON_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5aWtla2h0d2lld2xweGJ1d2dvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwMzM2OTksImV4cCI6MjEwNDYwOTY5OX0.R3OLDUPuPgWHHAGJsWMbgqM8vSDfjUltGeQzwyR_BAE"
    )
    supabase_service_role_key: str = os.getenv(
        "SUPABASE_SERVICE_ROLE_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5aWtla2h0d2lld2xweGJ1d2dvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4OTAzMzY5OSwiZXhwIjoyMTA0NjA5Njk5fQ.Z0caNRJw8dPkUfiSaYahVDBD_89JKkui5AhaYhs2jzM"
    )

    # Risk weights
    risk_weights: RiskWeights = RiskWeights()
    
    # Disclaimers
    disclaimer_text: str = (
        "This is a prototype decision-support assessment for demonstration purposes. "
        "Always verify current official marine advisories (IMD/INCOIS/Coast Guard) before departure."
    )

settings = Settings()
