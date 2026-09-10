# 🗄️ Database & Authentication Architecture (SIH 2026 — ORCA)

This branch (`database_auth`) contains the complete PostgreSQL database schema, Supabase Auth integration, triggers, and Row Level Security (RLS) policies for the **ORCA Marine Ecosystem Reasoning Platform (Problem Statement PS26176)**.

---

## 📌 Overview

* **Database Engine**: PostgreSQL 15+ (Hosted on Supabase)
* **Project URL**: `https://byikekhtwiewlpxbuwgo.supabase.co`
* **Schema File**: [`supabase_schema.sql`](./supabase_schema.sql)
* **Authentication**: Supabase Auth (`auth.users`) with automated sync to `public.users`

---

## 🏛️ Schema Architecture

### 1. User & Authentication Layer
* **`public.users`**: Extends Supabase Auth profiles.
  * `id` (UUID, Primary Key → `auth.users(id)` ON DELETE CASCADE)
  * `email` (TEXT, UNIQUE)
  * `role` (`user_role`: `'user'`, `'researcher'`, `'admin'`)
  * `is_active` (BOOLEAN)
  * `full_name` (TEXT)
  * `created_at`, `updated_at` (TIMESTAMPTZ)

#### ⚡ Automated Sync Trigger (`handle_new_user`):
When a user signs up via Supabase Auth (email/password or OAuth), PostgreSQL automatically inserts a matching profile in `public.users`:
```sql
CREATE TRIGGER on_auth_user_created
    AFTER INSERT OR UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

---

### 2. Decision & AI Analysis Layer
* **`public.marine_analyses`**:
  * Stores multi-agent decision outputs, spatial evaluations, and recommendations.
  * Fields: `id`, `latitude`, `longitude`, `analyzed_at`, `summary`, `risk_level` (`LOW`/`MODERATE`/`HIGH`/`CRITICAL`), `observations` (JSONB), `risks` (JSONB), `recommendations` (JSONB), `data_sources` (JSONB), `confidence`, `requested_by_user_id`.

---

### 3. Hazard & Safety Alerts Layer
* **`public.alerts`**:
  * Active marine hazard warnings, cyclone/storm alerts, and high-wave advisories.
  * Fields: `id`, `latitude`, `longitude`, `issued_at`, `title`, `description`, `risk_level`, `source`, `is_active`, `resolved_at`, `marine_analysis_id`.

---

### 4. Environmental Observations Layer (Normalized Time-Series)
Every observation table includes geospatial coordinates (`latitude`, `longitude`), timestamp (`observed_at`), data origin (`source`), and measurement status (`observation` vs `forecast`):

1. **`weather_observations`**: Air temperature, wind speed, wind direction, precipitation, pressure (IMD / NOAA / Open-Meteo).
2. **`wave_observations`**: Significant wave height, wave direction, wave period, swell height (Open-Meteo / NOAA NDBC / TidesAtlas).
3. **`ocean_observations`**: Sea Surface Temperature (SST), Chlorophyll-a, Salinity, satellite dataset product (NASA Ocean Color).
4. **`tide_observations`**: Water level, tidal prediction label (`high`/`low`) (NOAA CO-OPS / TidesAtlas).
5. **`current_observations`**: Surface water speed, flow direction (NOAA CO-OPS / NDBC).

---

## 🔒 Row Level Security (RLS) Policies

All tables have RLS enabled with granular permissions:
* **Profiles**: Authenticated users can read and update their own profile (`auth.uid() = id`).
* **Active Alerts & Environmental Observations**: Publicly readable by all users and frontend maps.
* **Analyses**: Authenticated users can view their own analyses.
* **Backend Services**: Service Role key has full read/write access.

---

## 🚀 How to Apply Migrations

1. Open your [Supabase SQL Editor](https://supabase.com/dashboard/project/byikekhtwiewlpxbuwgo/sql/new).
2. Copy the entire contents of [`supabase_schema.sql`](./supabase_schema.sql).
3. Paste and click **Run**.
4. All tables, functions, triggers, and RLS policies will be applied idempotently.
