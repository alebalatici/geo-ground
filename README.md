# 🌍 GeoGround

## 1. Vision & Product Overview (B2B SaaS)
GeoGround is a Commercial Real Estate & Retail Site Intelligence platform. We process raw satellite data (optical, radar, thermal) to provide institutional investment funds (REITs) and real estate developers with early-warning economic signals. The platform detects land clearing, construction activity, and urban expansion months before public permits are filed.

**Current Scope (4-Week MVP):**
- Data processing and demonstrations limited exclusively to Romania (focusing on major hubs like Cluj-Napoca, Bucharest, and Timișoara) for speed, efficiency, and real-world ground-truth validation.
- Web platform only (Desktop/Browser). Mobile applications (React Native) are planned for the future roadmap.

---

## 2. Tech Stack
- **Backend:** Python 3.11+ with FastAPI.
- **Geospatial Data Processing:** Google Earth Engine (GEE) via Python API. Raw terabytes of imagery are not downloaded locally; cloud masking and raster math (NDVI, SAR, LST) execute directly on Google servers.
- **Satellites Utilized:**
  - **Sentinel-2 (`COPERNICUS/S2_SR_HARMONIZED`):** Optical vegetation health (NDVI) with `SCL` scene-level cloud/shadow masking at 10m resolution.
  - **Sentinel-1 (`COPERNICUS/S1_GRD`):** All-weather C-band SAR radar backscatter (`VV` & `VH` in dB) for structural/construction activity detection.
  - **Landsat 7 / 8 / 9 (`C02/T1_L2`):** Harmonized historical archives (2000–present) for long-term NDVI trends and Land Surface Temperature (`LST_C` in °C).
- **Database:** PostgreSQL with the PostGIS extension for managing site polygons (GeoJSON), historical alerts, and valuation metrics.
- **Frontend:** React.js (built with Vite), Tailwind CSS, interactive maps via Leaflet, and charts powered by Recharts.
- **AI Integration:** Free-tier LLMs (Gemini via Google AI Studio, Groq, or local Ollama) integrated via API into FastAPI. Strictly used to translate raw mathematical telemetry (e.g., *"NDVI dropped by 60% while SAR VV spiked by +3.4 dB"*) into human-readable executive summaries. No custom model training or fine-tuning is performed.

---

## 3. Core Platform Features
1. **Role-Based Access Control (RBAC / View Switcher):**
   - **Executive View:** Clean, minimalist dashboard designed for investors. Focuses on maps, timeline sliders, color-coded status alerts (Green/Amber), and high-level business intelligence.
   - **Enterprise Analytics:** Bloomberg-terminal style dashboard for Data Science and GIS teams. Includes multispectral correlation charts (NDVI vs. SAR), raw coordinate logs, custom polygons, and CSV data exports.
2. **Timeline Slider (2000 – Present):** Correlating historical satellite imagery with local real estate market evolution.
3. **Persistent AI Assistant:** A sidebar chat window anchored to the interface, ready to answer contextual questions about the active site.

---

## 4. UI/UX Design Guidelines
- **Aesthetic:** "Architectural Dark Mode".
- **Color Palette:** Sober, institutional backgrounds (charcoal, slate shades) combined with engineering accents like copper/amber and muted blues. No neon or cyberpunk glows. The design must project precision, safety, and professional architectural planning.

---

## 5. Development Rules
1. Generate modular, production-ready code with strict separation of concerns (`api/` → `services/` → `integrations/` → `models/`).
2. Stick strictly to the defined tech stack.
3. Every backend feature must be accompanied by automated unit and integration tests (`unittest`).
4. Keep the frontend clean, professional, B2B, and built with responsive Flex/Grid layouts.

---

## 6. Current Project Status & Roadmap

### Completed (Backend — Core & Earth Observation Pipeline)
- **FastAPI Core (`app/main.py`, `app/core/config.py`):** Environment-driven configuration (`pydantic-settings`), CORS middleware, lifespan initialization, and live `/health` GEE diagnostic endpoint.
- **Google Earth Engine Integration (`app/integrations/gee/`):**
  - `client.py`: Service Account and local CLI authentication + live server connectivity check.
  - `sentinel2.py`: Optical NDVI time-series extraction with `SCL` cloud/shadow masking (10m scale).
  - `sentinel1.py`: All-weather C-band SAR (`VV`/`VH` backscatter in dB) time-series extraction (10m scale).
  - `landsat.py`: Harmonized 2000–present summer composite pipeline combining Landsat 7, 8, and 9 (`NDVI` + thermal `LST_C` at 30m scale).
  - `validator.py`: GeoJSON polygon validation (ring closure, `[lon, lat]` order check, Romania geographic bounds, and area cap protection).
  - `aggregator.py`: Unified facade (`fetch_full_site_telemetry`) orchestrating validation and multi-sensor extraction.
- **Test Suite (`tests/`):** Comprehensive unit (mocked) and live GEE integration tests (`unittest`) covering API health, polygon validation, and all three satellite pipelines.

### 🚧 Next Up (Backend)
1. **Spatial Database (PostgreSQL + PostGIS):** Configure SQLAlchemy + GeoAlchemy2 models (`MonitoredSite`, `SatelliteSnapshot`, `SiteAlert`) to persist polygons and cache telemetry series.
2. **Business Logic & Alert Engine (`app/services/`):** Correlate NDVI drops with SAR backscatter spikes to trigger automated Green/Amber early-warning signals.
3. **LLM Executive Layer (`app/integrations/llm/`):** Integrate Gemini/Groq API to generate executive summaries and power the contextual site chat assistant.
4. **REST API v1 & Seeding (`app/api/v1/`, `scripts/`):** Expose endpoints for sites, 2000–present timeline, spectral correlations, CSV exports, and pre-populate 6–8 real Romanian real-estate/industrial hubs for instant demo performance.