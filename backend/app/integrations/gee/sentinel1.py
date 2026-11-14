from datetime import datetime, timezone
from typing import Any
import ee

from app.integrations.gee.client import GEEClientError


def get_sentinel1_sar_series(
    polygon_coords: list[list[list[float]]],
    start_date: str,
    end_date: str,
    orbit_pass: str = "DESCENDING",
) -> list[dict[str, Any]]:
    """
    Extracts the temporal SAR series from Sentinel-1 GRD for a given GeoJSON polygon in a given time interval.
    Why do we count VV and VH:
    - VV (Vertical-Vertical): sensitive to structures, buildings, utilities, asphalt/concrete.
    - VH (Vertical-Horizontal): sensitive to volume (vegetation density vs. land surface).
    Rising VV (values less than -14 dB, e.g., from -14 dB to -8 dB) indicates construction activity or presence of artificial structures.
    :param polygon_coords: the coordinates of the polygon in GeoJSON format [[[lon, lat], ...]]
    :param start_date: the start date 'YYYY-MM-DD'
    :param end_date: the end date 'YYYY-MM-DD'
    :param orbit_pass: the orbit pass ('ASCENDING' or 'DESCENDING')
    :return: the list of dictionaries sorted by date: [{"date": "2025-05-12", "sar_vv": 0.64, "sar_vh": 0.78}, ...]
    """
    try:
        roi = ee.Geometry.Polygon(polygon_coords)

        collection = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(roi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.eq("instrumentMode", "IW"))  # Interferometric Wide swath (standard above the land)
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
            .filter(ee.Filter.eq("orbitProperties_pass", orbit_pass))
            .select(["VV", "VH"])
        )

        def extract_mean_sar(image: ee.Image) -> ee.Feature:
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=10, # 10 metres/pixel resolution
                maxPixels=1e8,
            )
            return ee.Feature(
                None,
                {
                    "timestamp": image.get("system:time_start"),
                    "vv": stats.get("VV"),
                    "vh": stats.get("VH"),
                },
            )

        features_info = collection.map(extract_mean_sar).getInfo()
    except Exception as exc:
        raise GEEClientError(f"Error at processing Sentinel-1 SAR: {exc}") from exc

    results: list[dict[str, Any]] = []
    for feat in features_info.get("features", []):
        props = feat.get("properties", {})
        vv_val = props.get("vv")
        vh_val = props.get("vh")
        ts_ms = props.get("timestamp")

        if vv_val is None or vh_val is None or ts_ms is None:
            continue

        date_str = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
        results.append(
            {
                "date": date_str,
                "sar_vv": round(float(vv_val), 2),
                "sar_vh": round(float(vh_val), 2),
            }
        )

    results.sort(key=lambda item: item["date"])
    return results