# 🌍 GeoGround

## 1. Vision & Product Overview (B2B SaaS)

GeoGround is a Commercial Real Estate & Retail Site Intelligence platform. We process raw satellite data (optical, radar, thermal) to provide institutional investment funds (REITs), real estate agents, and land buyers with early-warning economic signals. The platform detects land clearing, construction activity, and urban expansion months before public permits are filed.

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
- **Database:** PostgreSQL 16 with the PostGIS 3.4 extension (`SQLAlchemy 2.0` + `GeoAlchemy2`) for managing site polygons (`EPSG:4326`), historical telemetry snapshots, and early-warning alerts.
- **Frontend:** React.js (built with Vite), Tailwind CSS, interactive maps via Leaflet, and charts powered by Recharts.
- **AI Integration:** Multi-provider free-tier LLM gateway combining **Groq (`llama-3.3-70b-versatile`)** for sub-second conversational inference and **Google Gemini (`gemini-3.8-flash` / `gemini-3.5-flash-lite`)** as secondary cascade fallback. Strictly used to translate raw mathematical telemetry (e.g., *"NDVI dropped by 60% while SAR VV spiked by +3.4 dB"*) into plain-language, scientifically grounded real estate insights. No custom model training or fine-tuning is performed.

---

## 3. Core Platform Features

1. **Role-Based Access Control (RBAC / View Switcher):**
   - **Executive View:** Clean, minimalist dashboard designed for investors and agents. Focuses on maps, timeline sliders, color-coded status alerts (Green/Amber), and high-level business intelligence.
   - **Enterprise Analytics:** Bloomberg-terminal style dashboard for Data Science and GIS teams. Includes multispectral correlation charts (NDVI vs. SAR), raw coordinate logs, custom polygons, and CSV data exports.
2. **Timeline Slider (2000 – Present):** Correlating historical satellite imagery with local real estate market evolution.
3. **Persistent AI Real Estate Advisor:** A sidebar chat window anchored to the interface, translating satellite indices into practical ground insights tailored to the user's goal (homebuyer, investor, or real estate agent).

---

## 4. UI/UX Design Guidelines

- **Aesthetic:** "Architectural Dark Mode".
- **Color Palette:** Sober, institutional backgrounds (charcoal, slate shades) combined with engineering accents like copper/amber and muted blues. No neon or cyberpunk glows. The design must project precision, safety, and professional architectural planning.

---

## 5. Development Rules

1. Generate modular, production-ready code with strict layered separation of concerns (`api/` → `services/` → `repositories/` + `integrations/` → `models/`).
2. Stick strictly to the defined tech stack.
3. Every backend feature must be accompanied by automated unit and integration tests (`unittest`).
4. Keep the frontend clean, professional, B2B, and built with responsive Flex/Grid layouts.

---

## 6. Current Project Status & Roadmap

### Completed (Backend — Core, EO Pipeline, Spatial DB & Alert Engine)

- **FastAPI Core (`app/main.py`, `app/core/config.py`):** Environment-driven configuration (`pydantic-settings`), CORS middleware, lifespan initialization (`init_db()`), and live `/health` GEE diagnostic endpoint.
- **Google Earth Engine Integration (`app/integrations/gee/`):**
  - `client.py`: Service Account and local CLI authentication + live server connectivity check.
  - `sentinel2.py`: Optical NDVI time-series extraction with `SCL` cloud/shadow masking (10m scale).
  - `sentinel1.py`: All-weather C-band SAR (`VV`/`VH` backscatter in dB) time-series extraction (10m scale).
  - `landsat.py`: Harmonized 2000–present summer composite pipeline combining Landsat 7, 8, and 9 (`NDVI` + thermal `LST_C` at 30m scale).
  - `validator.py`: GeoJSON polygon validation (ring closure, `[lon, lat]` order check, Romania geographic bounds, and area cap protection).
  - `aggregator.py`: Unified facade (`fetch_full_site_telemetry`) orchestrating validation and multi-sensor extraction.
- **Spatial Database & Persistence (`docker-compose.yml`, `app/db/session.py`, `app/models/`, `app/repositories/`):**
  - Containerized PostgreSQL 16 + PostGIS 3.4 instance (`docker-compose.yml`) with environment-driven credentials (`.env` / `.env.example`).
  - SQLAlchemy 2.0 session management (`app/db/session.py`) with connection pooling, `get_db` dependency injection, and automated `CREATE EXTENSION IF NOT EXISTS postgis` initialization.
  - GeoAlchemy2 ORM models (`MonitoredSite`, `SatelliteSnapshot`, `SiteAlert`) with `EPSG:4326` polygon geometries, unique sensor/date constraints, and GeoJSON ↔ WKT/WKB conversion helpers (`geometry_utils.py`).
  - `SiteRepository` (`app/repositories/site_repository.py`) encapsulating spatial CRUD operations, idempotent snapshot upserts, and alert queries.
- **Data Access / Repository Layer (`app/repositories/site_repository.py`):**
  - Dedicated `SiteRepository` isolating SQLAlchemy/PostGIS queries from business logic and HTTP routes.
  - Supports spatial parcel creation (`create_site`), city-filtered listing with eager-loaded alerts (`list_sites`, `get_site_by_id`), idempotent PostgreSQL `ON CONFLICT DO UPDATE` upserts for satellite time-series (`upsert_snapshots`), date/sensor-filtered telemetry queries (`get_snapshots_for_site`), and alert persistence (`save_alert`, `get_latest_alert`).
- **Business Logic & Alert Engine (`app/services/alert_engine.py`):**
  - Multi-sensor correlation engine comparing historical baseline vs. recent observation windows across optical NDVI drops and SAR (`VV`/`VH`) double-bounce backscatter spikes.
  - Deterministic signal classification (`BASELINE_STABLE`, `LAND_CLEARING`, `STRUCTURAL_EXPANSION`, `CONVERSION_ACTIVE`), `GREEN` / `AMBER` severity assignment, and cloud-quality-weighted confidence scoring.
- **Test Suite (`tests/`):** Comprehensive unit (mocked) and live integration tests (`unittest`) covering API health, GEE connectivity, GeoJSON polygon validation, all three satellite pipelines, PostGIS persistence (`test_spatial_models.py`), repository query/transaction flows (`test_site_repository.py`), anomaly alert thresholds (`test_alert_engine.py`), multi-provider LLM prompt grounding & offline failover (`test_llm_integration.py`), intelligence service orchestration (`test_intelligence_service.py`), REST API v1 endpoints & CSV streaming (`test_api_v1.py`), and Romanian hub seeding idempotency (`test_seed_romania_hubs.py`).
- **Multi-Provider LLM Executive & Assistant Integration (`app/integrations/llm/`, `app/schemas/intelligence.py`, `app/services/intelligence_service.py`):**
  - `app/schemas/intelligence.py`: Pydantic v2 data contracts (`TelemetryContextPayload`, `ExecutiveSummaryResponse`, `SiteChatRequest`, `SiteChatResponse`, `ChatTurn`) structuring normalized sensor telemetry and multi-turn chat payloads.
  - `app/integrations/llm/prompts.py`: Strict anti-hallucination system prompts (`SYSTEM_PROMPT_EXECUTIVE`, `SYSTEM_PROMPT_ASSISTANT`) and deterministic telemetry serializers (`format_telemetry_context`) translating verified NDVI, SAR (`VV`/`VH`), and thermal (`LST_C`) metrics into accessible real estate insights tailored to buyers, agents, and developers.
  - `app/integrations/llm/client.py`: Multi-provider `GeminiClient` gateway orchestrating **Groq** (`groq` SDK, `llama-3.3-70b-versatile`) as primary low-latency inference engine with automatic cascade fallback to **Google Gemini** (`google-genai` SDK, `gemini-3.8-flash` / `gemini-3.5-flash-lite`) and a deterministic rule-based offline safety net.
  - `app/services/intelligence_service.py`: `IntelligenceService` orchestrating `SiteRepository` spatial records, latest `SiteAlert` classifications, and 2000–present archive summaries with the LLM gateway to produce investor executive briefs and timeline-aware assistant responses.
- **REST API v1 & Seeding (`app/api/v1/`, `app/schemas/site.py`, `app/services/site_service.py`, `scripts/`):**
  - `app/schemas/site.py`: Pydantic v2 contracts (`GeoJSONPolygon`, `SiteCreateRequest`, `SiteListItemResponse`, `SiteDetailResponse`, `SiteTimelineResponse`, `SpectralCorrelationResponse`, `AlertSummarySchema`) defining the HTTP API surface.
  - `app/services/site_service.py`: `SiteService` orchestrating custom Romania polygon validation & PostGIS ingestion, 2000–present chronological timeline queries, monthly-bucketed optical NDVI vs. SAR `VV`/`VH` Pearson correlation analytics, and streaming CSV telemetry exports.
  - `app/api/v1/` (`router.py`, `dependencies.py`, `endpoints/sites.py`, `endpoints/intelligence.py`, mounted in `app/main.py`): Versioned FastAPI routers exposing parcel CRUD (`GET/POST /api/v1/sites`, `GET /api/v1/sites/{site_id}`), historical timelines (`/timeline`), multispectral correlations (`/correlations`), CSV downloads (`/export/csv`), AI executive briefs (`/executive-summary`), and contextual site chat (`/chat`).
  - `scripts/seed_romania_hubs.py`: Idempotent PostGIS seeder pre-populating 7 real Romanian commercial/logistics hubs across Cluj-Napoca, Bucharest, and Timișoara with calibrated 2000–2026 multi-sensor archives and anomaly alerts (plus optional `--live-gee` ingestion mode).

---

## 🚀 Getting Started (Local Development Setup)

Follow the steps below to set up and run the **GeoGround** backend locally.

### Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose** (for the PostgreSQL 16 + PostGIS 3.4 spatial database)
- **Google Earth Engine (GEE)** approved account or the team's Service Account JSON key
- **LLM API Keys (Free Tier):** [Groq Console](https://console.groq.com/) (primary) and/or [Google AI Studio](https://aistudio.google.com/) (backup)

---

### 1. Clone the Repository & Set Up `.venv`

```bash
git clone https://github.com/alebalatici/geo-ground
cd geoground

# Create the Python virtual environment
python -m venv .venv

# Activate it (Linux / macOS):
source .venv/bin/activate

# Activate it (Windows PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Configure Environment Variables (`.env`)

Do **not** delete `.env.example` — it serves as the shared configuration template for all contributors. Create your own local `.env` file (which is automatically ignored by Git):

```bash
# Linux / macOS:
cp .env.example .env

# Windows (CMD / PowerShell):
copy .env.example .env
```

Open your local `.env` file and fill in the required values:

1. **Spatial Database (PostGIS):**
   The default credentials in `.env.example` are pre-configured for the local Docker container. Leave them as-is unless you already have another PostgreSQL instance running on port `5432`.

   
2.  (Personal GEE Account via CLI):** If using your own approved Earth Engine account, leave the Service Account fields blank in `.env` and authenticate via CLI (with `.venv` activated):
     ```bash
     earthengine authenticate
     ```

3. **LLM API Key (Executive Summaries & Site Assistant):**
   Generate a free-tier API key from [Google AI Studio](https://aistudio.google.com/) (Gemini) or [Groq Console](https://console.groq.com/) and add it to your `.env` file.

---

### 3. Start the Spatial Database (PostgreSQL + PostGIS)

Make sure Docker Desktop is running, then start the database container:

```bash
docker-compose up -d
```

*(The `postgis` extension is initialized automatically on the first FastAPI startup).*

---

### 4. Start the Backend Server & Verify Health

```bash
uvicorn app.main:app --reload
```

Confirm that both PostgreSQL/PostGIS and Google Earth Engine are properly connected:
* **Live Health Diagnostic (DB + GEE):** `http://127.0.0.1:8000/health`
* **Interactive API Docs (Swagger UI):** `http://127.0.0.1:8000/docs`

---

### 5. Run Automated Tests

Before opening a Pull Request, verify that all unit and integration tests pass:

```bash
python -m unittest discover -s tests -v
```

---

### 🌿 Team Git Workflow
* **Never push directly to `main`.**
* Create a dedicated feature branch for each task (e.g., `feature/llm-executive-layer`, `feature/api-v1-endpoints`, `feature/frontend-ui`).
* Open a **Pull Request (PR)** targeting `main` once all local tests pass.