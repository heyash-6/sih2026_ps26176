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
export async function askOrca(queryText, langOrSession = 'en', priorContext = null, sessionId = null) {
  const isLangCode = ['en', 'hi', 'mr'].includes(langOrSession);
  const effectiveLang = isLangCode ? langOrSession : 'en';
  const effectiveSessionId = sessionId || (!isLangCode ? langOrSession : `sess_${Date.now()}`);
  const mergedContext = {
    ...(priorContext || {}),
    language: effectiveLang
  };

  try {
    const res = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: effectiveSessionId,
        text: queryText,
        prior_context: mergedContext
      })
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    }
    const data = await res.json();
    if (data && !data.answer && data.explanation_text) {
      data.answer = data.explanation_text;
    }
    return data;
  } catch (err) {
    console.warn('[ORCA API] askOrca backend request failed:', err);
    return null;
  }
}

/**
 * Direct Potential Fishing Zone (PFZ) Lookup
 */
export async function getPfzCandidates(lat = null, lon = null, port = null, date = '2026-09-09') {
  try {
    const params = new URLSearchParams();
    if (port) params.append('port', port);
    if (lat !== null && lat !== undefined) params.append('lat', lat);
    if (lon !== null && lon !== undefined) params.append('lon', lon);
    if (date) params.append('date', date);

    const res = await fetch(`${API_BASE_URL}/api/pfz?${params.toString()}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getPfzCandidates failed:', err);
    return null;
  }
}

/**
 * Get all 20 Indian coastal ports catalog
 */
export async function getCoastalPorts() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/ports`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getCoastalPorts failed:', err);
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
export async function getAnalytics(period = '7', port = 'mumbai') {
  try {
    const res = await fetch(`${API_BASE_URL}/api/analytics?period=${encodeURIComponent(period)}&port=${encodeURIComponent(port)}`);
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
export async function getAllAlerts(port = null) {
  try {
    const url = port ? `${API_BASE_URL}/api/alerts?port=${encodeURIComponent(port)}` : `${API_BASE_URL}/api/alerts`;
    const res = await fetch(url);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getAllAlerts failed:', err);
    return null;
  }
}

/**
 * Multi-Day Deterministic Trip Simulation & Outlook
 */
export async function getFishingMultiDay(port = 'mumbai', pfz = null, days = 4, startDate = null, language = 'en') {
  try {
    const params = new URLSearchParams({ port, days: String(days), language });
    if (pfz) params.append('pfz', pfz);
    if (startDate) params.append('start_date', startDate);
    const res = await fetch(`${API_BASE_URL}/api/fishing/multi-day?${params.toString()}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getFishingMultiDay failed:', err);
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

/**
 * Resolve User GPS coordinates to closest coastal port & live telemetry
 */
export async function resolveUserLocation(lat, lon) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/location/resolve?lat=${lat}&lon=${lon}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] resolveUserLocation failed:', err);
    return null;
  }
}

/**
 * Calculate Safe Marine Navigation Route via Risk-Aware A*
 */
export async function getSafeMarineRoute(startLat, startLon, endLat, endLon, vesselSpeedKmh = 18.0) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/gis/route/safe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_latitude: startLat,
        start_longitude: startLon,
        end_latitude: endLat,
        end_longitude: endLon,
        vessel_speed_kmh: vesselSpeedKmh
      })
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getSafeMarineRoute failed:', err);
    return null;
  }
}

/**
 * Analyze Voyage Navigation (PFZ, Hazards, Conditions, Waypoints)
 */
export async function analyzeNavigation(startLat, startLon, endLat, endLon, vesselSpeedKmh = 18.0) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/gis/navigation/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_latitude: startLat,
        start_longitude: startLon,
        end_latitude: endLat,
        end_longitude: endLon,
        vessel_speed_kmh: vesselSpeedKmh
      })
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] analyzeNavigation failed:', err);
    return null;
  }
}

/**
 * Live INCOIS Telemetry for specific coordinate
 */
export async function getLiveIncoisTelemetry(lat, lon) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/incois/live?lat=${lat}&lon=${lon}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] getLiveIncoisTelemetry failed:', err);
    return null;
  }
}

/**
 * -----------------------------------------------------------------------------
 * User-Specific Conversation & Chat History Services (Requirements 5, 6, 7, 8)
 * -----------------------------------------------------------------------------
 */

export async function getUserConversations(userId) {
  if (!userId) return [];
  const storageKey = `orca_convs_${userId}`;
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations?user_id=${encodeURIComponent(userId)}`);
    if (res.ok) {
      const data = await res.json();
      if (data && Array.isArray(data.conversations)) {
        localStorage.setItem(storageKey, JSON.stringify(data.conversations));
        return data.conversations;
      }
    }
  } catch (err) {
    console.warn('[ORCA API] getUserConversations network error, falling back to local cache:', err);
  }
  // Local cache fallback
  try {
    const cached = localStorage.getItem(storageKey);
    return cached ? JSON.parse(cached) : [];
  } catch {
    return [];
  }
}

export async function createNewConversation(userId, title = 'New Marine Chat') {
  if (!userId) return null;
  const storageKey = `orca_convs_${userId}`;
  const localId = 'conv_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6);
  const newConvObj = {
    id: localId,
    user_id: userId,
    title: title.slice(0, 70),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, title: title.slice(0, 70) })
    });
    if (res.ok) {
      const data = await res.json();
      const serverConv = Array.isArray(data) ? data[0] : data;
      if (serverConv?.id) {
        // Update local cache
        const convs = await getUserConversations(userId);
        const updated = [serverConv, ...convs.filter(c => c.id !== serverConv.id)];
        localStorage.setItem(storageKey, JSON.stringify(updated));
        return serverConv;
      }
    }
  } catch (err) {
    console.warn('[ORCA API] createNewConversation network error, saving locally:', err);
  }

  // Fallback to local storage
  const cached = localStorage.getItem(storageKey);
  const currentList = cached ? JSON.parse(cached) : [];
  const updatedList = [newConvObj, ...currentList];
  localStorage.setItem(storageKey, JSON.stringify(updatedList));
  return newConvObj;
}

export async function getConversationMessages(convId) {
  if (!convId) return [];
  const storageKey = `orca_msgs_${convId}`;
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations/${encodeURIComponent(convId)}/messages`);
    if (res.ok) {
      const data = await res.json();
      if (data && Array.isArray(data.messages)) {
        const normalized = data.messages.map(m => ({
          ...m,
          message_text: m.message_text || m.message || m.text || '',
          text: m.message_text || m.message || m.text || '',
          message: m.message || m.message_text || m.text || '',
          structured_data: m.structured_data || m.metadata || null,
          metadata: m.metadata || m.structured_data || {}
        }));
        localStorage.setItem(storageKey, JSON.stringify(normalized));
        return normalized;
      }
    }
  } catch (err) {
    console.warn('[ORCA API] getConversationMessages network error, checking local cache:', err);
  }
  // Local cache fallback
  try {
    const cached = localStorage.getItem(storageKey);
    if (!cached) return [];
    const parsed = JSON.parse(cached);
    return Array.isArray(parsed) ? parsed.map(m => ({
      ...m,
      message_text: m.message_text || m.message || m.text || '',
      text: m.message_text || m.message || m.text || '',
      message: m.message || m.message_text || m.text || '',
      structured_data: m.structured_data || m.metadata || null,
      metadata: m.metadata || m.structured_data || {}
    })) : [];
  } catch {
    return [];
  }
}

export async function saveChatMessage(convId, userIdOrSender, senderOrText, textOrMeta = null, language = 'en', hasRoute = false, metadata = {}) {
  if (!convId) return null;
  const storageKey = `orca_msgs_${convId}`;

  // Flexible argument normalization
  let actualUserId = 'guest_user';
  let actualSender = 'user';
  let actualText = '';
  let actualMeta = {};

  if (userIdOrSender === 'user' || userIdOrSender === 'orca') {
    actualSender = userIdOrSender;
    actualText = typeof senderOrText === 'string' ? senderOrText : '';
    actualMeta = (typeof textOrMeta === 'object' && textOrMeta !== null) ? textOrMeta : {};
  } else {
    actualUserId = userIdOrSender || 'guest_user';
    actualSender = senderOrText || 'user';
    actualText = typeof textOrMeta === 'string' ? textOrMeta : (typeof senderOrText === 'string' ? senderOrText : '');
    actualMeta = (typeof metadata === 'object' && metadata !== null) ? metadata : {};
  }

  const msgObj = {
    id: 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6),
    conversation_id: convId,
    user_id: actualUserId,
    sender: actualSender,
    message: actualText,
    message_text: actualText,
    text: actualText,
    language,
    has_route: hasRoute,
    metadata: actualMeta,
    structured_data: actualMeta,
    created_at: new Date().toISOString()
  };

  // Immediate local cache update
  try {
    const cached = localStorage.getItem(storageKey);
    const msgs = cached ? JSON.parse(cached) : [];
    localStorage.setItem(storageKey, JSON.stringify([...msgs, msgObj]));
  } catch {}

  // Sync to backend Supabase
  try {
    fetch(`${API_BASE_URL}/api/conversations/${encodeURIComponent(convId)}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: convId,
        user_id: actualUserId,
        sender: actualSender,
        message: actualText,
        language,
        has_route: hasRoute,
        metadata: actualMeta
      })
    }).catch(() => {});
  } catch {}

  return msgObj;
}

export async function deleteConversation(userId, convId) {
  if (!convId) return false;
  const storageKey = `orca_convs_${userId}`;
  const msgKey = `orca_msgs_${convId}`;

  // Update local storage
  try {
    localStorage.removeItem(msgKey);
    if (userId) {
      const cached = localStorage.getItem(storageKey);
      if (cached) {
        const convs = JSON.parse(cached);
        const filtered = convs.filter(c => c.id !== convId);
        localStorage.setItem(storageKey, JSON.stringify(filtered));
      }
    }
  } catch {}

  // Delete from backend
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations/${encodeURIComponent(convId)}`, {
      method: 'DELETE'
    });
    return res.ok;
  } catch (err) {
    console.warn('[ORCA API] deleteConversation network error:', err);
    return true;
  }
}

export async function clearConversationMessages(convId) {
  if (!convId) return false;
  const msgKey = `orca_msgs_${convId}`;
  try {
    localStorage.removeItem(msgKey);
  } catch {}

  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations/${encodeURIComponent(convId)}/messages`, {
      method: 'DELETE'
    });
    return res.ok;
  } catch (err) {
    console.warn('[ORCA API] clearConversationMessages network error:', err);
    return true;
  }
}

/**
 * Port-Specific Dashboard Context, Marine Conditions, Advisories & Active/Inactive PFZs
 */
export async function getPortContext(portId = 'mumbai') {
  try {
    const res = await fetch(`${API_BASE_URL}/api/ports/${encodeURIComponent(portId)}/context`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Port context API error:', err);
  }
  return null;
}

/**
 * Location-Aware Tide Predictions & Schedule
 */
export async function getTides(portId = 'mumbai') {
  try {
    const res = await fetch(`${API_BASE_URL}/api/tides?port=${encodeURIComponent(portId)}`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Tides API error:', err);
  }
  return null;
}
