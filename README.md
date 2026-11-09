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

## 6. Current Project Status & Task

**Current Status:** The repository structure (Monorepo) is set up with separate `backend` (FastAPI) and `frontend` (React) directories.
