/**
 * ORCA Full-Stack Integration Client
 * Connects the React 19 Frontend with the FastAPI Multi-Agent AI Backend (:8000).
 */

const API_BASE_URL = typeof window !== 'undefined' && window.__ORCA_API_URL__
  ? window.__ORCA_API_URL__
  : 'http://localhost:8000';

/**
 * Check if the FastAPI backend is running and healthy.
 */
export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`, { method: 'GET' });
    if (!res.ok) return { online: false };
    const data = await res.json();
    return { online: true, ...data };
  } catch (err) {
    return { online: false, error: err.message };
  }
}

/**
 * Primary Conversational Agent Pipeline
 * Calls FastAPI POST /api/query (NLU -> Planner -> Specialist Execution -> Risk Scoring -> Decision Explanation).
 */
export async function askOrca(queryText, sessionId = 'web_session_' + Date.now(), priorContext = null) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        text: queryText,
        prior_context: priorContext
      })
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    }
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] askOrca backend request failed, falling back to local reasoning:', err);
    return null;
  }
}

/**
 * Direct Potential Fishing Zone (PFZ) Lookup
 */
export async function getPfzCandidates(lat = 16.99, lon = 73.31, date = '2026-09-09') {
  try {
    const res = await fetch(`${API_BASE_URL}/api/pfz?lat=${lat}&lon=${lon}&date=${date}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getPfzCandidates failed:', err);
    return null;
  }
}

/**
 * Weather & Marine Sea State Lookup
 */
export async function getMarineData(lat = 16.99, lon = 73.31, datetime = '2026-09-09T05:00:00+05:30') {
  try {
    const res = await fetch(`${API_BASE_URL}/api/weather?lat=${lat}&lon=${lon}&datetime=${encodeURIComponent(datetime)}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getMarineData failed:', err);
    return null;
  }
}

/**
 * Hazard Bulletins Lookup
 */
export async function getHazards(lat = 16.99, lon = 73.31, datetime = '2026-09-09T05:00:00+05:30') {
  try {
    const res = await fetch(`${API_BASE_URL}/api/hazards?lat=${lat}&lon=${lon}&datetime=${encodeURIComponent(datetime)}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getHazards failed:', err);
    return null;
  }
}

/**
 * Coastal Navigation Route & Geofence Evaluation
 */
export async function getRouteAndGeofence(origin, destination) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ origin, destination })
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getRouteAndGeofence failed:', err);
    return null;
  }
}

/**
 * Deterministic Risk Engine Evaluation
 */
export async function evaluateRisk(riskInput) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/risk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(riskInput)
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] evaluateRisk failed:', err);
    return null;
  }
}

/**
 * Ocean Analytics & Observations Time-Series from Supabase
 */
export async function getAnalytics(period = '7') {
  try {
    const res = await fetch(`${API_BASE_URL}/api/analytics?period=${encodeURIComponent(period)}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getAnalytics failed:', err);
    return null;
  }
}

/**
 * Active Marine Hazard Advisories from Supabase
 */
export async function getAllAlerts() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/alerts`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getAllAlerts failed:', err);
    return null;
  }
}

/**
 * Past Multi-Agent Decision Records from Supabase
 */
export async function getAnalysisHistory(limit = 10) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/history?limit=${limit}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getAnalysisHistory failed:', err);
    return null;
  }
}

/**
 * Trigger Live Coastal Ingestion into Supabase
 */
export async function triggerSync() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/sync`, { method: 'POST' });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] triggerSync failed:', err);
    return null;
  }
}

