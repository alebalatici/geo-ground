# geo-ground
# 🌍 GeoGround
## 1. Vision & Product Overview (B2B SaaS)

GeoGround is a Commercial Real Estate & Retail Site Intelligence platform. We process raw satellite data (optical, radar, thermal) to provide institutional investment funds (REITs) and real estate developers with early-warning economic signals. The platform detects land clearing, construction activity, and urban expansion months before public permits are filed.

**Current Scope (4-Week MVP):**
* Data processing and demonstrations limited exclusively to **Romania** (focusing on major hubs like Cluj, Bucharest, and Timișoara) for speed, efficiency, and real-world ground-truth validation.
* Web platform only (Desktop/Browser). Mobile applications (React Native) are planned for the future roadmap.

---

## 2. Tech Stack
* **Backend:** Python with `FastAPI`.
* **Geospatial Data Processing:** `Google Earth Engine (GEE)` via Python API. Raw terabytes of imagery are not downloaded locally; cloud masking and raster math (NDVI, SAR) execute directly on Google servers.
* **Satellites Utilized:** Sentinel-2 (optical/vegetation health), Sentinel-1 (radar/industrial activity), Landsat (historical archives since 2000 & thermal tracking).
* **Database:** `PostgreSQL` with the `PostGIS` extension for managing site polygons (GeoJSON), historical alerts, and valuation metrics.
* **Frontend:** `React.js` (built with Vite), `Tailwind CSS`, interactive maps via `Leaflet`, and charts powered by `Recharts`.
* **AI Integration:** Free-tier LLMs (Gemini via Google AI Studio, Groq, or local Ollama) integrated via API into FastAPI. The model is strictly used to translate raw mathematical telemetry (e.g., "NDVI dropped by 60%") into human-readable executive summaries. No custom model training or fine-tuning is performed.

---

## 3. Core Platform Features

1. **Role-Based Access Control (RBAC):**
   * **Executive View:** Clean, minimalist dashboard designed for investors. Focuses on maps, timeline sliders, color-coded status alerts (Green/Amber), and high-level business intelligence.
   * **Enterprise Analytics:** Bloomberg-terminal style dashboard for Data Science and GIS teams. Includes multispectral correlation charts (NDVI vs. SAR), raw coordinate logs, custom polygons, and CSV/PDF data exports.
2. **Timeline Slider (2000 - Present):** Correlating historical satellite imagery with local real estate market evolution.
3. **Persistent AI Assistant:** A sidebar chat window anchored to the interface, ready to answer contextual questions about the active site.

---

## 4. UI/UX Design Guidelines

* **Aesthetic:** "Architectural Dark Mode".
* **Color Palette:** Sober, institutional backgrounds (charcoal, slate shades) combined with engineering accents like copper/amber and muted blues. No neon or cyberpunk glows. The design must project precision, safety, and professional architectural planning.

---

## 5. Development Rules for AI

1. Generate modular, production-ready code.
2. Stick strictly to the defined tech stack.
3. Avoid lengthy theoretical explanations unless explicitly requested. Provide direct technical solutions.
4. Keep the frontend clean, professional, B2B, and built with responsive Flex/Grid layouts.
5. Assume the local development environment (PyCharm / VS Code) is configured and authentication keys for GEE and LLM APIs are ready.

---

## 6. Current Project Status & Roadmap

### Completed (Backend - Earth Observation Pipeline)
- **FastAPI Core & Configuration:** Environment-driven settings (`pydantic-settings`), CORS setup, lifespan lifecycle management, and `/health` diagnostic endpoint.
- **Google Earth Engine Integration (`app/integrations/gee/`):**
  - `client.py`: Service Account and local CLI authentication handler.
  - `sentinel2.py`: Optical vegetation tracking (NDVI) with `SCL` scene-level cloud/shadow masking at 10m resolution.
  - `sentinel1.py`: All-weather C-band SAR radar backscatter (`VV` & `VH` in dB) for detecting structural changes, machinery, and site clearing.
  - `landsat.py`: Harmonized 2000–present annual summer composite pipeline combining Landsat 7, 8, and 9 (`NDVI` + Land Surface Temperature `LST_C` in °C).
- **Automated Testing:** Unit and live integration test suites (`unittest`) covering API health and all three satellite sensors over Romanian test polygons.

### Next Up (Backend)
1. **Spatial Database (PostgreSQL + PostGIS):** Models (`MonitoredSite`, `SatelliteSnapshot`, `SiteAlert`) and spatial persistence for Romanian hubs (Cluj-Napoca, Bucharest, Timișoara).
2. **Analysis & Alert Engine (`app/services/`):** Correlating NDVI drops with SAR spikes to trigger Green/Amber early-warning signals.
3. **LLM Executive Layer (`app/integrations/llm/`):** Gemini/Groq integration for translating telemetry anomalies into executive summaries and powering the contextual site assistant.
4. **REST API v1 & Seeding:** Endpoints for sites, 2000–present timeline, spectral correlation charts, CSV exports, and pre-computed demo data for instant UI rendering.
