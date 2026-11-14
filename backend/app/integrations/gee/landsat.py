from typing import Any
import ee

from app.integrations.gee.client import GEEClientError


def _mask_landsat_c2_clouds(image: ee.Image) -> ee.Image:
    """
    Clears out the cloud shadows and the snow from the image from Landsat Collection 2 Level 2 using the QA_PIXEL band (bits 1 = Dilated Cloud, 3 = Cloud, 4 = Cloud Shadow, 5 = Snow).
    @param image: the image to mask
    :return: the masked image
    """
    qa = image.select("QA_PIXEL")
    cloud_mask = (
        qa.bitwiseAnd(1 << 1).eq(0)
        .And(qa.bitwiseAnd(1 << 3).eq(0))
        .And(qa.bitwiseAnd(1 << 4).eq(0))
        .And(qa.bitwiseAnd(1 << 5).eq(0))
    )
    return image.updateMask(cloud_mask)


def _prep_landsat_7(image: ee.Image) -> ee.Image:
    """
    Applies the official scaling factors for Landsat 7 (2000-2013) and calculates NDVI + Thermal Surface Temperature (LST in Celsius).
    Bands L7: SR_B3 (Red), SR_B4 (NIR), ST_B6 (Thermal Kelvin).
    :param image: the image to process
    :return: the processed image
    """
    masked = _mask_landsat_c2_clouds(image)
    optical = masked.select(["SR_B3", "SR_B4"]).multiply(0.0000275).add(-0.2)
    thermal_celsius = (
        masked.select("ST_B6")
        .multiply(0.00341802)
        .add(149.0)
        .subtract(273.15)
        .rename("LST_C")
    )
    ndvi = optical.normalizedDifference(["SR_B4", "SR_B3"]).rename("NDVI")
    return image.addBands([ndvi, thermal_celsius]).select(["NDVI", "LST_C"])


def _prep_landsat_8_9(image: ee.Image) -> ee.Image:
    """
    Applies the official scaling factors for Landsat 8 & 9 (2013-present) and calculates NDVI + Thermal Surface Temperature (LST in Celsius).
    Bands L8/L9: SR_B4 (Red), SR_B5 (NIR), ST_B10 (Thermal Kelvin).
    :param image: the image to process
    :return: the processed image
    """
    masked = _mask_landsat_c2_clouds(image)
    optical = masked.select(["SR_B4", "SR_B5"]).multiply(0.0000275).add(-0.2)
    thermal_celsius = (
        masked.select("ST_B10")
        .multiply(0.00341802)
        .add(149.0)
        .subtract(273.15)
        .rename("LST_C")
    )
    ndvi = optical.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    return image.addBands([ndvi, thermal_celsius]).select(["NDVI", "LST_C"])


def get_landsat_historical_series(
    polygon_coords: list[list[list[float]]],
    start_year: int = 2000,
    end_year: int = 2026,
    max_cloud_cover: int = 35,
) -> list[dict[str, Any]]:
    """
    Extracts the historical anual series (summer window: June - August) for NDVI (vegetation) and LST_C (thermal surface temperature in Celsius) using Landsat 7/8/9.
    :param polygon_coords: the coordinates of the polygon in GeoJSON format [[[lon, lat], ...]]
    :param start_year: the start year (must be >= 2000)
    :param end_year: the end year (ex: 2026)
    :param max_cloud_cover: the maximum cloud cover percentage (0-100)
    :return: the list of dictionaries sorted by year: [{"year": 2000, "ndvi": 0.68, "lst_celsius": 26.4}, ...]
    """
    if start_year < 2000 or end_year < start_year:
        raise ValueError("Interval de ani invalid: start_year trebuie să fie >= 2000 și <= end_year.")

    try:
        roi = ee.Geometry.Polygon(polygon_coords)

        l7 = (
            ee.ImageCollection("LANDSAT/LE07/C02/T1_L2")
            .filterBounds(roi)
            .filterDate("2000-01-01", "2013-04-30")
            .filter(ee.Filter.lt("CLOUD_COVER", max_cloud_cover))
            .map(_prep_landsat_7)
        )

        l8 = (
            ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
            .filterBounds(roi)
            .filterDate("2013-05-01", "2027-01-01")
            .filter(ee.Filter.lt("CLOUD_COVER", max_cloud_cover))
            .map(_prep_landsat_8_9)
        )

        l9 = (
            ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
            .filterBounds(roi)
            .filterDate("2021-11-01", "2027-01-01")
            .filter(ee.Filter.lt("CLOUD_COVER", max_cloud_cover))
            .map(_prep_landsat_8_9)
        )

        merged_collection = l7.merge(l8).merge(l9)
        years = ee.List.sequence(start_year, end_year)

        def compute_yearly_summer_composite(year: ee.Number) -> ee.Feature:
            year = ee.Number(year)
            # We use the summer months (June - August) for phenological comparison between years
            summer_start = ee.Date.fromYMD(year, 6, 1)
            summer_end = ee.Date.fromYMD(year, 8, 31)

            yearly_col = merged_collection.filterDate(summer_start, summer_end)
            count = yearly_col.size()

            def _compute_stats() -> ee.Dictionary:
                composite = yearly_col.median()
                return composite.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=roi,
                    scale=30,
                    maxPixels=1e8,
                )

            stats = ee.Dictionary(
                ee.Algorithms.If(
                    count.gt(0),
                    _compute_stats(),
                    ee.Dictionary({"NDVI": None, "LST_C": None}),
                )
            )

            return ee.Feature(
                None,
                {
                    "year": year,
                    "image_count": yearly_col.size(),
                    "ndvi": stats.get("NDVI"),
                    "lst_celsius": stats.get("LST_C"),
                },
            )

        features_info = ee.FeatureCollection(years.map(compute_yearly_summer_composite)).getInfo()
    except Exception as exc:
        raise GEEClientError(f"Error for Landsat archival processing: {exc}") from exc

    results: list[dict[str, Any]] = []
    for feat in features_info.get("features", []):
        props = feat.get("properties", {})
        ndvi_val = props.get("ndvi")
        lst_val = props.get("lst_celsius")
        year_val = props.get("year")
        img_count = props.get("image_count", 0)

        # Ignoring the years without valid images (e.g., an year with fully clouded summers over the polygon)
        if img_count == 0 or ndvi_val is None or lst_val is None or year_val is None:
            continue

        results.append(
            {
                "year": int(year_val),
                "ndvi": round(float(ndvi_val), 4),
                "lst_celsius": round(float(lst_val), 2),
            }
        )

    results.sort(key=lambda item: item["year"])
    return results