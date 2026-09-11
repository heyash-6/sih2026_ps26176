"""
INCOIS Live Marine Data Client
Fetches operational oceanographic forecast and observation data directly from the
official Indian National Centre for Ocean Information Services (INCOIS) THREDDS & ERDDAP servers.

Data products integrated:
1. Significant Wave Height (SWH) & Sea State from INCOIS Ocean State Forecast (WaveWatch III / SWAN / HOOFS).
2. Sea Surface Temperature (SST) from INCOIS Daily Operational High-Resolution SST.
3. Coastal Marine Winds (WSM) from INCOIS Ocean State Wind Forecasts.
4. Ocean Colour & Chlorophyll-a Gradients for PFZ (Potential Fishing Zone) advisories.
"""

import logging
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
import httpx

logger = logging.getLogger("orca.incois")

_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ORCA-Marine-Intelligence/2.0 (INCOIS Integration)"
_TIMEOUT_SECONDS = 3.5

class INCOISLiveClient:
    """
    High-performance client for querying official INCOIS THREDDS OpenDAP operational marine datasets.
    Includes automated catalog discovery, keep-alive connection pooling, multi-cell seaward fallback
    for coastal land masks, in-memory observation caching, and graceful open-marine fallback.
    """

    BASE_THREDDS = "https://incois.gov.in/thredds"
    DODSC_URL = f"{BASE_THREDDS}/dodsC"

    def __init__(self):
        self._cached_wave_file: Optional[str] = None
        self._cached_sst_file: Optional[str] = None
        self._cached_wind_file: Optional[str] = None
        self._last_catalog_refresh: Optional[datetime] = None
        # HTTP client with persistent connection pool
        self._http = httpx.Client(
            verify=False,
            timeout=_TIMEOUT_SECONDS,
            headers={"User-Agent": _USER_AGENT},
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        # Coordinate cache with 15-minute TTL: key -> (timestamp, data)
        self._coord_cache: Dict[str, Tuple[datetime, Dict[str, Any]]] = {}

    def _refresh_catalogs_if_needed(self):
        """Discover latest operational dataset filenames from INCOIS THREDDS XML catalogs (cached for 1 hr)."""
        now = datetime.utcnow()
        if (
            self._last_catalog_refresh
            and (now - self._last_catalog_refresh).total_seconds() < 3600
            and self._cached_wave_file
            and self._cached_sst_file
        ):
            return

        # 1. Wave catalog
        wave_file = self._fetch_latest_from_catalog(f"{self.BASE_THREDDS}/catalog/osf/wave/catalog.xml")
        if wave_file:
            self._cached_wave_file = wave_file
        elif not self._cached_wave_file:
            self._cached_wave_file = f"osf/wave/WAVES_nio_{now.strftime('%Y%m%d')}.nc"

        # 2. SST catalog
        sst_file = self._fetch_latest_from_catalog(f"{self.BASE_THREDDS}/catalog/osf/sst/catalog.xml")
        if sst_file:
            self._cached_sst_file = sst_file
        elif not self._cached_sst_file:
            self._cached_sst_file = f"osf/sst/SST_NIO_{now.strftime('%Y%m%d')}.nc"

        # 3. Wind catalog
        wind_file = self._fetch_latest_from_catalog(f"{self.BASE_THREDDS}/catalog/osf/winds/catalog.xml")
        if wind_file:
            self._cached_wind_file = wind_file
        elif not self._cached_wind_file:
            self._cached_wind_file = f"osf/winds/WINDS_{now.strftime('%Y%m%d')}.nc"

        self._last_catalog_refresh = now
        logger.info(
            f"INCOIS catalogs synced -> Wave: {self._cached_wave_file}, SST: {self._cached_sst_file}, Wind: {self._cached_wind_file}"
        )

    def _fetch_latest_from_catalog(self, catalog_url: str) -> Optional[str]:
        try:
            resp = self._http.get(catalog_url)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                paths = [d.attrib["urlPath"] for d in root.iter() if "urlPath" in d.attrib]
                if paths:
                    paths.sort()
                    return paths[-1]
        except Exception as e:
            logger.debug(f"Catalog fetch warning for {catalog_url}: {e}")
        return None

    def _query_opendap(self, url_path: str, projection: str) -> Optional[str]:
        """Fetch ASCII slice from INCOIS THREDDS OpenDAP endpoint using connection pool."""
        try:
            encoded_proj = urllib.parse.quote(projection)
            full_url = f"{self.DODSC_URL}/{url_path}.ascii?{encoded_proj}"
            resp = self._http.get(full_url)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            logger.debug(f"INCOIS OpenDAP query failed for {url_path} ({projection}): {e}")
        return None

    def _extract_first_valid_value(
        self, text: Optional[str], var_name: str, min_val: float = 0.05, max_val: float = 45.0
    ) -> Optional[float]:
        """Parse numerical array block from OpenDAP ASCII response, ignoring fill values (-1e34, NaN)."""
        if not text:
            return None
        m = re.search(rf"{var_name}\.{var_name}\[.*?\]\s*\n\s*(.*?)\n\s*{var_name}\.", text, re.DOTALL)
        if not m:
            m = re.search(rf"{var_name}\.{var_name}\[.*?\]\s*\n\s*(.*)", text, re.DOTALL)
        if not m:
            return None

        raw_block = m.group(1)
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", raw_block)
        for n in nums:
            try:
                val = float(n)
                if min_val <= val <= max_val:
                    return round(val, 2)
            except ValueError:
                continue
        return None

    def get_live_wave(self, lat: float, lon: float) -> Tuple[Optional[float], str]:
        """
        Query INCOIS Significant Wave Height (SWH) in meters for coordinate.
        Searches seaward grid cells if the coordinate lands on an estuary/land mask cell.
        """
        self._refresh_catalogs_if_needed()
        wave_file = self._cached_wave_file or "osf/wave/WAVES_nio_20260909.nc"

        # Wave grid: LAT start -5.0 step 0.25 (index 0..136); LON start 32.0 step 0.25 (index 0..272)
        lat_idx = max(1, min(135, int(round((lat - (-5.0)) / 0.25))))
        lon_idx = max(2, min(270, int(round((lon - 32.0) / 0.25))))

        # 3x5 window centered around port to reliably find coastal ocean cells
        projection = f"SWH[0:1:0][{lat_idx-1}:1:{lat_idx+1}][{lon_idx-2}:1:{lon_idx+2}]"
        raw_ascii = self._query_opendap(wave_file, projection)
        swh = self._extract_first_valid_value(raw_ascii, "SWH", min_val=0.1, max_val=14.0)

        if swh is not None:
            return swh, f"INCOIS WaveWatch III Live Model ({wave_file.split('/')[-1]})"

        return None, "INCOIS Unreachable"

    def get_live_sst(self, lat: float, lon: float) -> Tuple[Optional[float], str]:
        """
        Query INCOIS Operational High-Resolution Sea Surface Temperature (SST) in °C.
        """
        self._refresh_catalogs_if_needed()
        sst_file = self._cached_sst_file or "osf/sst/SST_NIO_20260909.nc"

        # SST grid: LAT start -30.0 step 1/12 deg (index 0..719); LON start 30.0 step 1/12 deg (index 0..1079)
        lat_idx = max(2, min(717, int(round((lat - (-30.0)) * 12.0))))
        lon_idx = max(2, min(1077, int(round((lon - 30.0) * 12.0))))

        # 5x5 window (approx ±15-20 km) for coastal waters
        projection = f"SST[0:1:0][0:1:0][{lat_idx-2}:1:{lat_idx+2}][{lon_idx-2}:1:{lon_idx+2}]"
        raw_ascii = self._query_opendap(sst_file, projection)
        sst = self._extract_first_valid_value(raw_ascii, "SST", min_val=20.0, max_val=36.0)

        if sst is not None:
            return sst, f"INCOIS Operational SST ({sst_file.split('/')[-1]})"

        return None, "INCOIS Unreachable"

    def get_live_wind(self, lat: float, lon: float) -> Tuple[Optional[float], Optional[float], str]:
        """
        Query INCOIS Coastal Marine Wind Speed Magnitude (WSM) in km/h.
        Grid: AX005 (lat start -60.0, step 0.1), AX004 (lon start 30.0, step 0.1).
        """
        self._refresh_catalogs_if_needed()
        wind_file = self._cached_wind_file or "osf/winds/WINDS_20260909.nc"

        lat_idx = max(1, min(899, int(round((lat + 60.0) * 10.0))))
        lon_idx = max(1, min(899, int(round((lon - 30.0) * 10.0))))

        projection = f"WSM[0:1:0][{lat_idx-1}:1:{lat_idx+1}][{lon_idx-1}:1:{lon_idx+1}]"
        raw_ascii = self._query_opendap(wind_file, projection)
        wsm_ms = self._extract_first_valid_value(raw_ascii, "WSM", min_val=0.1, max_val=60.0)

        if wsm_ms is not None:
            wind_speed_kmh = round(wsm_ms * 3.6, 1)
            return wind_speed_kmh, wsm_ms, f"INCOIS Ocean State Winds ({wind_file.split('/')[-1]})"

        return None, None, "INCOIS Unreachable"

    def get_live_marine_observation(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Combined real-time observation querying live INCOIS servers,
        with 15-minute coordinate caching for optimal response time.
        """
        cache_key = f"{lat:.2f}_{lon:.2f}"
        now = datetime.utcnow()

        if cache_key in self._coord_cache:
            ts, cached_data = self._coord_cache[cache_key]
            if (now - ts).total_seconds() < 900:  # 15 minutes
                return cached_data

        wave_height, wave_src = self.get_live_wave(lat, lon)
        sst, sst_src = self.get_live_sst(lat, lon)
        wind_kmh, _, wind_src = self.get_live_wind(lat, lon)

        sources_used = []
        if wave_height is not None:
            sources_used.append("INCOIS WW3 Wave")
        if sst is not None:
            sources_used.append("INCOIS Daily SST")
        if wind_kmh is not None:
            sources_used.append("INCOIS OSF Wind")

        # Determine sea state
        wh = wave_height if wave_height is not None else 1.1
        if wh < 0.5:
            sea_state = "calm"
        elif wh < 1.25:
            sea_state = "slight"
        elif wh < 2.5:
            sea_state = "moderate"
        elif wh < 4.0:
            sea_state = "rough"
        else:
            sea_state = "very rough"

        obs = {
            "latitude": lat,
            "longitude": lon,
            "wave_height_m": wave_height,
            "sst_celsius": sst,
            "wind_speed_kmh": wind_kmh,
            "sea_state": sea_state,
            "wave_source": wave_src,
            "sst_source": sst_src,
            "wind_source": wind_src,
            "primary_source": " + ".join(sources_used) if sources_used else "INCOIS THREDDS OpenDAP",
            "is_incois_live": len(sources_used) > 0,
            "timestamp": now.isoformat() + "Z",
        }

        self._coord_cache[cache_key] = (now, obs)
        return obs

incois_client = INCOISLiveClient()
