import math
from typing import Any


class InvalidPolygonError(ValueError):
    """
    Thrown when the GeoJSON polygon is invalid or does not fit within the Romanian territory.
    """

ROMANIA_LON_MIN = 20.2
ROMANIA_LON_MAX = 29.8
ROMANIA_LAT_MIN = 43.6
ROMANIA_LAT_MAX = 48.3

MAX_AREA_SQ_KM = 50.0


def _approx_polygon_area_sq_km(ring: list[list[float]]) -> float:
    """
    Calculates the approximate area of a polygon in square kilometers using the Shoelace formula projected on the average latitude of the polygon.
    Precise > 99.5% for Romania, without external dependencies.
    """
    avg_lat_rad = math.radians(sum(pt[1] for pt in ring[:-1]) / (len(ring) - 1))
    km_per_deg_lat = 111.132
    km_per_deg_lon = 111.320 * math.cos(avg_lat_rad)

    area = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i][0] * km_per_deg_lon, ring[i][1] * km_per_deg_lat
        x2, y2 = ring[i + 1][0] * km_per_deg_lon, ring[i + 1][1] * km_per_deg_lat
        area += (x1 * y2) - (x2 * y1)

    return abs(area) / 2.0


def validate_romania_polygon(
    polygon_coords: list[list[list[float]]],
    max_area_sq_km: float = MAX_AREA_SQ_KM,
) -> dict[str, Any]:
    """
    Validates the GeoJSON polygon structure and checks if it fits within the Romanian territory and if the area is within the specified limit for GEE processing.
    :param polygon_coords: the coordinates of the polygon in GeoJSON format [[[lon, lat], ...]]
    :param max_area_sq_km: the maximum area allowed in square kilometers
    :return: a dictionary with geometric metrics: {"area_sq_km": float, "area_hectares": float, "vertex_count": int}
    :raises InvalidPolygonError: if the polygon is invalid
    """
    if isinstance(polygon_coords, dict):
        if polygon_coords.get("type") != "Polygon":
            raise InvalidPolygonError("GeoJSON geometry must be of type 'Polygon'.")
        polygon_coords = polygon_coords.get("coordinates", [])

    if not polygon_coords or not isinstance(polygon_coords, list) or not polygon_coords[0]:
        raise InvalidPolygonError("The GeoJSON polygon is empty or has an invalid structure.")

    outer_ring = polygon_coords[0]

    # A valid GeoJSON polygon must have at least 3 distinct vertices + the closing point = 4 points
    if len(outer_ring) < 4:
        raise InvalidPolygonError(
            f"The polygon must contain at least 4 coordinates (3 vertices + closing point). Received: {len(outer_ring)}."
        )

    if outer_ring[0] != outer_ring[-1]:
        raise InvalidPolygonError(
            "The polygon must be closed. The first and last coordinates must be identical."
        )

    for idx, point in enumerate(outer_ring):
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            raise InvalidPolygonError(f"Invalid coordinate at index {idx}: {point}.")

        lon, lat = point[0], point[1]

        # Catches the classic Leaflet mistake [lat, lon] vs GeoJSON [lon, lat]
        if 43.0 <= lon <= 49.0 and 20.0 <= lat <= 30.0:
            raise InvalidPolygonError(
                f"The order of coordinates seems to be [lat, lon] instead of [lon, lat]: [lat, lon] = [{lon}, {lat}]."
                "The GeoJSON standard requires the first coordinate to be the longitude, and the second to be the latitude."
            )

        if not (ROMANIA_LON_MIN <= lon <= ROMANIA_LON_MAX and ROMANIA_LAT_MIN <= lat <= ROMANIA_LAT_MAX):
            raise InvalidPolygonError(
                f"The point [{lon}, {lat}] is outside the Romanian territory."
                f"(the MVP scope is limited to Romania)"
            )

    area_sq_km = _approx_polygon_area_sq_km(outer_ring)

    if area_sq_km <= 0.0001:
        raise InvalidPolygonError("The polygon surface is too small (minimum 100 m^2")

    if area_sq_km > max_area_sq_km:
        raise InvalidPolygonError(
            f"The polygon surface ({area_sq_km: .2f} km^2) is too large. It exceeds the maximum allowed area of {max_area_sq_km: .2f} km^2. for satellite processing."
        )

    return {
        "area_sq_km": round(area_sq_km, 4),
        "area_hectares": round(area_sq_km * 100, 2),
        "vertex_count": len(outer_ring) - 1,
    }