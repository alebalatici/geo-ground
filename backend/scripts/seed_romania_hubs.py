"""Idempotent database seeder populating 7 real Romanian CRE & logistics hubs for instant demo."""

import argparse
from datetime import date
import logging
from typing import Any

from app.db.session import SessionLocal, init_db
from app.integrations.gee.aggregator import fetch_full_site_telemetry
from app.integrations.gee.validator import validate_romania_polygon
from app.repositories.site_repository import SiteRepository
from app.services.alert_engine import evaluate_site_anomalies

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _box_polygon(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> dict[str, Any]:
    """Construct a closed counter-clockwise GeoJSON Polygon in EPSG:4326."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat],
            ]
        ],
    }


ROMANIA_DEMO_HUBS: list[dict[str, Any]] = [
    {
        "name": "Tetarom III Industrial & Logistics Corridor (Jucu)",
        "city": "Cluj-Napoca",
        "sector_type": "Industrial & Logistics",
        "area_hectares": 18.4,
        "geometry": _box_polygon(23.7810, 46.8420, 23.7865, 46.8460),
        "profile": "STRUCTURAL_EXPANSION",
    },
    {
        "name": "Lomb / Cluj Innovation Park North Expansion",
        "city": "Cluj-Napoca",
        "sector_type": "Mixed-Use & Tech Campus",
        "area_hectares": 14.2,
        "geometry": _box_polygon(23.5650, 46.8100, 23.5698, 46.8135),
        "profile": "CONVERSION_ACTIVE",
    },
    {
        "name": "Florești West Retail & Warehousing Zone",
        "city": "Cluj-Napoca",
        "sector_type": "Retail Park",
        "area_hectares": 9.6,
        "geometry": _box_polygon(23.4820, 46.7445, 23.4862, 46.7475),
        "profile": "LAND_CLEARING",
    },
    {
        "name": "Pipera Nord Commercial & Logistics Hub",
        "city": "Bucharest",
        "sector_type": "Commercial & Retail",
        "area_hectares": 12.8,
        "geometry": _box_polygon(26.1190, 44.5005, 26.1238, 44.5038),
        "profile": "CONVERSION_ACTIVE",
    },
    {
        "name": "A1 West Logistics Park (Chiajna Corridor)",
        "city": "Bucharest",
        "sector_type": "Industrial & Logistics",
        "area_hectares": 21.5,
        "geometry": _box_polygon(25.9510, 44.4530, 25.9570, 44.4570),
        "profile": "BASELINE_STABLE",
    },
    {
        "name": "Dumbrăvița / Giarmata Airport Logistics Hub",
        "city": "Timișoara",
        "sector_type": "Industrial & Logistics",
        "area_hectares": 16.7,
        "geometry": _box_polygon(21.2720, 45.8030, 21.2772, 45.8068),
        "profile": "STRUCTURAL_EXPANSION",
    },
    {
        "name": "Calea Șagului South Retail & Distribution Park",
        "city": "Timișoara",
        "sector_type": "Retail Park",
        "area_hectares": 11.3,
        "geometry": _box_polygon(21.1920, 45.7105, 21.1965, 45.7138),
        "profile": "BASELINE_STABLE",
    },
]


def build_calibrated_archive(profile: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Generate a realistic 2000–2026 multi-sensor archive + alert matching the hub's activity profile."""
    snapshots: list[dict[str, Any]] = []

    # 1. Historical Landsat summer archive (2000–2015)
    for year in range(2000, 2016, 3):
        snapshots.append(
            {
                "observation_date": date(year, 7, 15),
                "sensor": "LANDSAT",
                "ndvi_mean": 0.66 if profile != "BASELINE_STABLE" else 0.28,
                "vv_mean": None,
                "vh_mean": None,
                "lst_c": 27.4 if profile != "BASELINE_STABLE" else 31.0,
                "cloud_cover_pct": 4.5,
            }
        )

    # 2. Modern Sentinel-2 + Sentinel-1 era (2018–2026)
    modern_years = [2018, 2020, 2022, 2024, 2025, 2026]
    for year in modern_years:
        is_recent = year >= 2025

        if profile == "CONVERSION_ACTIVE":
            ndvi = 0.21 if is_recent else 0.63
            vv = -7.8 if is_recent else -11.4
            vh = -13.9 if is_recent else -17.2
            lst = 32.1 if is_recent else 28.2
        elif profile == "LAND_CLEARING":
            ndvi = 0.23 if is_recent else 0.65
            vv = -10.9 if is_recent else -11.3
            vh = -16.8 if is_recent else -17.1
            lst = 31.4 if is_recent else 27.9
        elif profile == "STRUCTURAL_EXPANSION":
            ndvi = 0.29 if is_recent else 0.34
            vv = -7.2 if is_recent else -10.5
            vh = -13.1 if is_recent else -16.4
            lst = 33.0 if is_recent else 30.8
        else:  # BASELINE_STABLE
            ndvi = 0.27
            vv = -8.4
            vh = -14.5
            lst = 31.2

        snapshots.append(
            {
                "observation_date": date(year, 8, 10),
                "sensor": "SENTINEL-2",
                "ndvi_mean": ndvi,
                "vv_mean": None,
                "vh_mean": None,
                "lst_c": lst,
                "cloud_cover_pct": 3.2,
            }
        )
        snapshots.append(
            {
                "observation_date": date(year, 8, 12),
                "sensor": "SENTINEL-1",
                "ndvi_mean": None,
                "vv_mean": vv,
                "vh_mean": vh,
                "lst_c": None,
                "cloud_cover_pct": 0.0,
            }
        )

    alert_map: dict[str, dict[str, Any]] = {
        "CONVERSION_ACTIVE": {
            "signal_type": "CONVERSION_ACTIVE",
            "severity": "AMBER",
            "confidence_score": 0.93,
            "ndvi_baseline": 0.64,
            "ndvi_current": 0.21,
            "ndvi_delta": -0.43,
            "sar_vv_delta_db": 3.6,
            "sar_vh_delta_db": 3.3,
            "lst_current_c": 32.1,
            "lst_delta_c": 3.9,
            "observation_window": "2025-01-01 to 2026-08-12",
        },
        "LAND_CLEARING": {
            "signal_type": "LAND_CLEARING",
            "severity": "AMBER",
            "confidence_score": 0.89,
            "ndvi_baseline": 0.65,
            "ndvi_current": 0.23,
            "ndvi_delta": -0.42,
            "sar_vv_delta_db": 0.4,
            "sar_vh_delta_db": 0.3,
            "lst_current_c": 31.4,
            "lst_delta_c": 3.5,
            "observation_window": "2025-01-01 to 2026-08-12",
        },
        "STRUCTURAL_EXPANSION": {
            "signal_type": "STRUCTURAL_EXPANSION",
            "severity": "AMBER",
            "confidence_score": 0.91,
            "ndvi_baseline": 0.34,
            "ndvi_current": 0.29,
            "ndvi_delta": -0.05,
            "sar_vv_delta_db": 3.3,
            "sar_vh_delta_db": 3.3,
            "lst_current_c": 33.0,
            "lst_delta_c": 2.2,
            "observation_window": "2025-01-01 to 2026-08-12",
        },
        "BASELINE_STABLE": {
            "signal_type": "BASELINE_STABLE",
            "severity": "GREEN",
            "confidence_score": 0.95,
            "ndvi_baseline": 0.28,
            "ndvi_current": 0.27,
            "ndvi_delta": -0.01,
            "sar_vv_delta_db": 0.1,
            "sar_vh_delta_db": 0.0,
            "lst_current_c": 31.2,
            "lst_delta_c": 0.2,
            "observation_window": "2025-01-01 to 2026-08-12",
        },
    }

    return snapshots, alert_map[profile]


def seed_romania_hubs(use_live_gee: bool = False) -> int:
    """Insert Romanian demo hubs if not already present. Returns count of newly created sites."""
    init_db()
    repo = SiteRepository()
    created_count = 0

    with SessionLocal() as db:
        existing_sites = repo.list_sites(db)
        existing_names = {s.name for s in existing_sites}

        for hub in ROMANIA_DEMO_HUBS:
            if hub["name"] in existing_names:
                logger.info("Skipping existing hub: %s", hub["name"])
                continue

            validate_romania_polygon(hub["geometry"])

            site = repo.create_site(
                db,
                name=hub["name"],
                city=hub["city"],
                geojson=hub["geometry"],
                area_hectares=hub["area_hectares"],
                sector_type=hub["sector_type"],
            )

            if use_live_gee:
                logger.info("Fetching live GEE telemetry for %s...", hub["name"])
                bundle = fetch_full_site_telemetry(hub["geometry"])
                snapshots = bundle.get("snapshots", []) if isinstance(bundle, dict) else []
                alert_data = evaluate_site_anomalies(snapshots) if snapshots else None
            else:
                snapshots, alert_data = build_calibrated_archive(hub["profile"])

            if snapshots:
                repo.upsert_snapshots(db, site.id, snapshots)
            if alert_data:
                repo.save_alert(db, site.id, alert_data)

            created_count += 1
            logger.info("Seeded hub [%s] in %s (%s)", hub["name"], hub["city"], hub["profile"])

    return created_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Romanian CRE demo hubs into PostGIS.")
    parser.add_argument(
        "--live-gee",
        action="store_true",
        help="Fetch live Google Earth Engine telemetry instead of calibrated demo archives.",
    )
    args = parser.parse_args()
    total = seed_romania_hubs(use_live_gee=args.live_gee)
    logger.info("Seeding complete. Newly created sites: %d", total)