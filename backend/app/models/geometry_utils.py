from typing import Any
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping, shape

def geojson_polygon_to_wkt_element(geojson: dict[str, Any], srid: int = 4326) -> WKTElement:
    """Convert a validated GeoJSON Polygon (or Feature) dict into a GeoAlchemy2 WKTElement."""
    geom_dict = geojson["geometry"] if geojson.get("type") == "Feature" else geojson
    if geom_dict.get("type") != "Polygon":
        raise ValueError(f"Expected GeoJSON Polygon, got {geom_dict.get('type')}")

    shapely_geom = shape(geom_dict)
    if not shapely_geom.is_valid:
        raise ValueError("Invalid polygon topology cannot be converted to WKT.")

    return WKTElement(shapely_geom.wkt, srid=srid)

def wkb_element_to_geojson(wkb_element: Any) -> dict[str, Any]:
    """Convert a PostGIS WKBElement returned by SQLAlchemy back into a GeoJSON Polygon dict."""
    shapely_geom = to_shape(wkb_element)
    return mapping(shapely_geom)