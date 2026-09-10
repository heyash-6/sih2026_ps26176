# ORCA — SIH26176 Final Frontend

A single coherent React/Vite frontend for the ORCA Marine EcOsystem Reasoning platform.

## What is included

- One consistent ORCA visual system across Dashboard, Marine Map, Ocean Analytics, Fishing Intelligence, Safety & Routes, Assistant, Alerts, Settings and Profile.
- New ORCA logo asset based on the supplied reference.
- Light and blue-toned dark themes designed as two intentional theme modes, not a simple colour inversion.
- Ocean Analytics rebuilt around the supplied reference: KPI cards, filters, smooth area charts, coloured data categories, wave/wind panel and PFZ trend.
- Interactive Leaflet marine map with street/satellite layers, PFZ markers, alerts, vessel markers, language-aware curated labels and selected-zone focus.
- Eight reusable PFZ records in `src/data.js`; the UI renders the array so additional backend zones using the same data shape can be added later.
- Fishing Intelligence “View zone” navigation goes directly to the selected map zone.
- English / Hindi / Marathi UI selection persisted in localStorage.
- Dark mode persisted in localStorage.
- Editable demo profile: Devesh Madhavi, 1234556789, deveshxyz@gmail.com, Marine Researcher/Fisherman.
- ORCA assistant with demo conversational responses and suggested questions.
- Backend integration seam at `src/services/api.js`.

## Run on Windows

```powershell
cd C:\path\to\ORCA-SIH-FINAL
npm.cmd install
npm.cmd run dev
```

Open the localhost URL shown by Vite.

## Important

The frontend is intentionally backend-ready without exposing API keys. Replace the demo data/service functions in `src/services/api.js` when the team connects the real ISRO/EO, weather, GIS and AI services.

The map uses external OpenStreetMap/Esri tiles, so map imagery requires internet access. The curated city labels switch between English, Hindi and Marathi; the underlying OpenStreetMap basemap may still contain its own provider labels.

## Validation

The supplied source was syntax-checked with the TypeScript JSX transpiler. A full Vite install/build could not be completed in the packaging environment because the package installation timed out; run `npm.cmd install` and `npm.cmd run dev` locally.
