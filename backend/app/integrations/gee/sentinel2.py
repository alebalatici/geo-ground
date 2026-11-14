from datetime import datetime, timezone
from typing import Any
import ee

from app.integrations.gee.client import GEEClientError


def _mask_s2_clouds(image: ee.Image) -> ee.Image:
    """
    Clears out the cloud shadows and the snow from the image using the SCL band (Scene Classification Layer)
    from the Sentinel-2 Surface Reflectance (COPERNICUS/S2_SR_HARMONIZED) collection.
    Kept classes: 4 (Vegetation), 5 (Snow/Ice), 6 (Clouds), 7 (Other).
    :param image: the image to mask
    :return: the masked image
    """
    scl = image.select("SCL")
    clear_mask = (
        scl.eq(4)
        .Or(scl.eq(5))
        .Or(scl.eq(6))
        .Or(scl.eq(7))
    )

    # Bringing the reflectance in the [0, 1] range
    return image.updateMask(clear_mask).divide(10000).copyProperties(image, ["system:time_start"])


def _add_ndvi_band(image: ee.Image) -> ee.Image:
    """
    Calculates the Normalized Difference Vegetation Index (NDVI) using the B8 and B4 bands.
    NDVI = (NIR - RED) / (NIR + RED)
    :param image: the image to calculate NDVI for
    :return: the image with the NDVI band added
    """
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return image.addBands(ndvi)


def get_sentinel2_ndvi_series(
    polygon_coords: list[list[list[float]]],
    start_date: str,
    end_date: str,
    max_cloud_cover: int = 30,
) -> list[dict[str, Any]]:
    """
    Extracts the NDVI series for a given polygon in a given time interval.
    :param polygon_coords: the coordinates of the polygon in GeoJSON format [[[lon, lat], ...]]
    :param start_date: the start date 'YYYY-MM-DD'
    :param end_date: the end date 'YYYY-MM-DD'
    :param max_cloud_cover: the maximum cloud cover percentage (0-100)
    :return: the list of dictionaries sorted by date: [{"date": "2025-05-12", "ndvi": 0.64}, ...]
    """
    try:
        roi = ee.Geometry.Polygon(polygon_coords)

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(roi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_cover))
            .map(_mask_s2_clouds)
            .map(_add_ndvi_band)
        )

        def extract_mean_ndvi(image: ee.Image) -> ee.Feature:
            stats = image.select("NDVI").reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=10,
                maxPixels=1e8,
            )
            return ee.Feature(
                None,
                {
                    "timestamp": image.get("system:time_start"),
                    "ndvi": stats.get("NDVI"),
                },
            )

        features_info = collection.map(extract_mean_ndvi).getInfo()
    except Exception as exc:
        raise GEEClientError(f"Eroare la procesarea Sentinel-2 NDVI: {exc}") from exc

    results: list[dict[str, Any]] = []
    for feat in features_info.get("features", []):
        props = feat.get("properties", {})
        ndvi_val = props.get("ndvi")
        ts_ms = props.get("timestamp")

        if ndvi_val is None or ts_ms is None:
            continue

        date_str = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
        results.append(
            {
                "date": date_str,
                "ndvi": round(float(ndvi_val), 4),
            }
        )

    results.sort(key=lambda item: item["date"])
    return results