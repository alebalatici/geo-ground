from typing import Any

from app.integrations.gee.validator import validate_romania_polygon
from app.integrations.gee.sentinel2 import get_sentinel2_ndvi_series
from app.integrations.gee.sentinel1 import get_sentinel1_sar_series
from app.integrations.gee.landsat import get_landsat_historical_series


def fetch_full_site_telemetry(
    polygon_coords: list[list[list[float]]],
    recent_start_date: str,
    recent_end_date: str,
    historical_start_year: int = 2000,
    historical_end_year: int = 2026,
    include_historical: bool = True,
) -> dict[str, Any]:
    """
    Unique facade for complete site telemetry extraction for a Romania polygon:
    1. Validates the geometry and calculates the surface (km^2 / hectares).
    2. Extracts the recent Sentinel-2 NDVI optical series (resolution 10m).
    3. Extracts the recent Sentinel-1 SAR radar VV/VH series (resolution 10m).
    4. Optionally, extracts the historical archive Landsat 7/8/9 (2000 - present: NDVI + LST C)
    :param polygon_coords: the coordinates of the polygon in GeoJSON format [[[lon, lat], ...]]
    :param recent_start_date: the start date 'YYYY-MM-DD'
    :param recent_end_date: the end date 'YYYY-MM-DD'
    :param historical_start_year: the start year (must be >= 2000)
    :param historical_end_year: the end year (ex: 2026)
    :param include_historical: the historical data to include
    :return: a unified dictionary ready to be saved in PostgreSQL/PostGIS or sent to the alerting engine.
    """
    geometry_metrics = validate_romania_polygon(polygon_coords)

    optical_series = get_sentinel2_ndvi_series(
        polygon_coords=polygon_coords,
        start_date=recent_start_date,
        end_date=recent_end_date,
    )

    radar_series = get_sentinel1_sar_series(
        polygon_coords=polygon_coords,
        start_date=recent_start_date,
        end_date=recent_end_date,
    )

    historical_series: list[dict[str, Any]] = []
    if include_historical:
        historical_series = get_landsat_historical_series(
            polygon_coords=polygon_coords,
            start_year=historical_start_year,
            end_year=historical_end_year,
        )

    return {
        "geometry": geometry_metrics,
        "optical_sentinel2": optical_series,
        "radar_sentinel1": radar_series,
        "historical_landsat": historical_series,
    }