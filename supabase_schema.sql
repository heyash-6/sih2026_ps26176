-- ==============================================================================
-- SIH 2026: ORCA Marine Ecosystem Reasoning Platform
-- Supabase Schema & Authentication Integration
-- ==============================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Custom Enum Types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('user', 'researcher', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE risk_level AS ENUM ('LOW', 'MODERATE', 'HIGH', 'CRITICAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Helper function for updating updated_at timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ==============================================================================
-- 3. Users Table (Integrated with Supabase Auth)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT true,
    full_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trigger to sync auth.users inserts into public.users automatically on Signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, role, is_active, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE((NEW.raw_user_meta_data->>'role')::user_role, 'user'::user_role),
        true,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Bind trigger to Supabase auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT OR UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

DROP TRIGGER IF EXISTS tr_users_updated_at ON public.users;
CREATE TRIGGER tr_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ==============================================================================
-- 4. Marine Analyses Table
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.marine_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    summary TEXT,
    risk_level risk_level,
    observations JSONB,
    risks JSONB,
    recommendations JSONB,
    data_sources JSONB,
    confidence DOUBLE PRECISION,
    requested_by_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_marine_analysis_location_time 
    ON public.marine_analyses(latitude, longitude, analyzed_at);

DROP TRIGGER IF EXISTS tr_marine_analyses_updated_at ON public.marine_analyses;
CREATE TRIGGER tr_marine_analyses_updated_at
    BEFORE UPDATE ON public.marine_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ==============================================================================
-- 5. Alerts Table
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    risk_level risk_level NOT NULL DEFAULT 'MODERATE',
    source VARCHAR(128),
    is_active BOOLEAN NOT NULL DEFAULT true,
    resolved_at TIMESTAMPTZ,
    marine_analysis_id UUID REFERENCES public.marine_analyses(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_alert_location_time 
    ON public.alerts(latitude, longitude, issued_at);

DROP TRIGGER IF EXISTS tr_alerts_updated_at ON public.alerts;
CREATE TRIGGER tr_alerts_updated_at
    BEFORE UPDATE ON public.alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ==============================================================================
-- 6. Weather Observations Table (IMD, NOAA, Open-Meteo)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.weather_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    source VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'observation',
    temperature DOUBLE PRECISION,
    temperature_unit VARCHAR(16) DEFAULT '°C',
    wind_speed DOUBLE PRECISION,
    wind_speed_unit VARCHAR(16) DEFAULT 'm/s',
    wind_direction DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    precipitation_unit VARCHAR(16) DEFAULT 'mm',
    pressure DOUBLE PRECISION,
    pressure_unit VARCHAR(16) DEFAULT 'hPa',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_weather_obs_location_time 
    ON public.weather_observations(latitude, longitude, observed_at);
CREATE INDEX IF NOT EXISTS ix_weather_obs_source 
    ON public.weather_observations(source);

DROP TRIGGER IF EXISTS tr_weather_obs_updated_at ON public.weather_observations;
CREATE TRIGGER tr_weather_obs_updated_at
    BEFORE UPDATE ON public.weather_observations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ==============================================================================
-- 7. Wave Observations Table (Open-Meteo, NOAA/NDBC, TidesAtlas)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.wave_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    source VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'observation',
    height DOUBLE PRECISION,
    height_unit VARCHAR(16) DEFAULT 'm',
    direction DOUBLE PRECISION,
    period DOUBLE PRECISION,
    swell_height DOUBLE PRECISION,
    swell_height_unit VARCHAR(16) DEFAULT 'm',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_wave_obs_location_time 
    ON public.wave_observations(latitude, longitude, observed_at);
CREATE INDEX IF NOT EXISTS ix_wave_obs_source 
    ON public.wave_observations(source);

DROP TRIGGER IF EXISTS tr_wave_obs_updated_at ON public.wave_observations;
CREATE TRIGGER tr_wave_obs_updated_at
    BEFORE UPDATE ON public.wave_observations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ==============================================================================
-- 8. Ocean Observations Table (NASA Ocean Color, Chlorophyll, SST)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.ocean_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    source VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'observation',
    sea_surface_temperature DOUBLE PRECISION,
    sst_unit VARCHAR(16) DEFAULT '°C',
    chlorophyll_a DOUBLE PRECISION,
    chlorophyll_a_unit VARCHAR(16) DEFAULT 'mg/m³',
    salinity DOUBLE PRECISION,
    salinity_unit VARCHAR(16) DEFAULT 'PSU',
    product VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ocean_obs_location_time 
    ON public.ocean_observations(latitude, longitude, observed_at);
CREATE INDEX IF NOT EXISTS ix_ocean_obs_source 
    ON public.ocean_observations(source);

DROP TRIGGER IF EXISTS tr_ocean_obs_updated_at ON public.ocean_observations;
CREATE TRIGGER tr_ocean_obs_updated_at
    BEFORE UPDATE ON public.ocean_observations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ==============================================================================
-- 9. Tide Observations Table (NOAA CO-OPS, TidesAtlas)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.tide_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    source VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'observation',
    water_level DOUBLE PRECISION,
    water_level_unit VARCHAR(16) DEFAULT 'm',
    prediction VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_tide_obs_location_time 
    ON public.tide_observations(latitude, longitude, observed_at);
CREATE INDEX IF NOT EXISTS ix_tide_obs_source 
    ON public.tide_observations(source);

DROP TRIGGER IF EXISTS tr_tide_obs_updated_at ON public.tide_observations;
CREATE TRIGGER tr_tide_obs_updated_at
    BEFORE UPDATE ON public.tide_observations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ==============================================================================
-- 10. Current Observations Table (Surface Ocean Currents)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.current_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    source VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'observation',
    speed DOUBLE PRECISION,
    speed_unit VARCHAR(16) DEFAULT 'm/s',
    direction DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_current_obs_location_time 
    ON public.current_observations(latitude, longitude, observed_at);
CREATE INDEX IF NOT EXISTS ix_current_obs_source 
    ON public.current_observations(source);

DROP TRIGGER IF EXISTS tr_current_obs_updated_at ON public.current_observations;
CREATE TRIGGER tr_current_obs_updated_at
    BEFORE UPDATE ON public.current_observations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ==============================================================================
-- 11. Row Level Security (RLS) Policies
-- ==============================================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marine_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weather_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wave_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ocean_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tide_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.current_observations ENABLE ROW LEVEL SECURITY;

-- Users policies
DROP POLICY IF EXISTS "Users can read own profile" ON public.users;
CREATE POLICY "Users can read own profile" 
    ON public.users FOR SELECT 
    TO authenticated 
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
CREATE POLICY "Users can update own profile" 
    ON public.users FOR UPDATE 
    TO authenticated 
    USING (auth.uid() = id);

-- Public / Authenticated read policies for Marine Observations & Alerts
DROP POLICY IF EXISTS "Public read active alerts" ON public.alerts;
CREATE POLICY "Public read active alerts" 
    ON public.alerts FOR SELECT 
    USING (is_active = true);

DROP POLICY IF EXISTS "Authenticated read all alerts" ON public.alerts;
CREATE POLICY "Authenticated read all alerts" 
    ON public.alerts FOR SELECT 
    TO authenticated 
    USING (true);

DROP POLICY IF EXISTS "Public read observations" ON public.weather_observations;
CREATE POLICY "Public read observations" 
    ON public.weather_observations FOR SELECT 
    USING (true);

DROP POLICY IF EXISTS "Public read wave observations" ON public.wave_observations;
CREATE POLICY "Public read wave observations" 
    ON public.wave_observations FOR SELECT 
    USING (true);

DROP POLICY IF EXISTS "Public read ocean observations" ON public.ocean_observations;
CREATE POLICY "Public read ocean observations" 
    ON public.ocean_observations FOR SELECT 
    USING (true);

DROP POLICY IF EXISTS "Public read tide observations" ON public.tide_observations;
CREATE POLICY "Public read tide observations" 
    ON public.tide_observations FOR SELECT 
    USING (true);

DROP POLICY IF EXISTS "Public read current observations" ON public.current_observations;
CREATE POLICY "Public read current observations" 
    ON public.current_observations FOR SELECT 
    USING (true);

DROP POLICY IF EXISTS "Users read own or public analyses" ON public.marine_analyses;
CREATE POLICY "Users read own or public analyses" 
    ON public.marine_analyses FOR SELECT 
    TO authenticated 
    USING (requested_by_user_id = auth.uid() OR requested_by_user_id IS NULL);

-- Service Role write policies
DROP POLICY IF EXISTS "Service role full access analyses" ON public.marine_analyses;
CREATE POLICY "Service role full access analyses" 
    ON public.marine_analyses FOR ALL 
    TO service_role 
    USING (true);

DROP POLICY IF EXISTS "Service role full access alerts" ON public.alerts;
CREATE POLICY "Service role full access alerts" 
    ON public.alerts FOR ALL 
    TO service_role 
    USING (true);
