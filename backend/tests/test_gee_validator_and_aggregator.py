import unittest
from unittest.mock import patch

from app.integrations.gee import (
    validate_romania_polygon,
    InvalidPolygonError,
    fetch_full_site_telemetry,
)

VALID_BUCHAREST_POLYGON = [
    [
        [26.1000, 44.5000],
        [26.1100, 44.5000],
        [26.1100, 44.5060],
        [26.1000, 44.5060],
        [26.1000, 44.5000],
    ]
]

class TestGEEValidatorAndAggregator(unittest.TestCase):
    def test_valid_romania_polygon_metrics(self):
        """
        Checks the surface calculation and the number of vertices for a valid polygon.
        """
        metrics = validate_romania_polygon(VALID_BUCHAREST_POLYGON)

        self.assertEqual(metrics["vertex_count"], 4)
        self.assertGreater(metrics["area_sq_km"], 0.45)
        self.assertLess(metrics["area_sq_km"], 0.60)
        self.assertAlmostEqual(metrics["area_hectares"], metrics["area_sq_km"] * 100, places=1)

    def test_unclosed_polygon_raises_error(self):
        """
        The polygon is not closed, so it should raise an error.
        :return:
        """
        unclosed = [
            [
                [26.1000, 44.5000],
                [26.1100, 44.5000],
                [26.1100, 44.5060],
                [26.1000, 44.5060],
            ]
        ]
        with self.assertRaises(InvalidPolygonError):
            validate_romania_polygon(unclosed)

    def test_swapped_lat_lon_raises_descriptive_error(self):
        """
        Detects if the frontend sends [lat, lon] instead of [lon, lat].
        """
        swapped = [
            [
                [44.5000, 26.1000],
                [44.5000, 26.1100],
                [44.5060, 26.1100],
                [44.5060, 26.1000],
                [44.5000, 26.1000],
            ]
        ]
        with self.assertRaises(InvalidPolygonError) as ctx:
            validate_romania_polygon(swapped)

    def test_polygon_outside_romania_raises_error(self):
        """
        A polygon that is outside the Romania polygon should raise an error.
        """
        budapest = [
            [
                [19.0400, 47.4900],
                [19.0500, 47.4900],
                [19.0500, 47.5000],
                [19.0400, 47.5000],
                [19.0400, 47.4900],
            ]
        ]
        with self.assertRaises(InvalidPolygonError):
            validate_romania_polygon(budapest)

    def test_polygon_too_large_raises_error(self):
        """
        A polygon that is too large should raise an error to prevent timeout in GEE.
        """
        huge_polygon = [
            [
                [25.0000, 45.0000],
                [25.2000, 45.0000],
                [25.2000, 45.2000],
                [25.0000, 45.2000],
                [25.0000, 45.0000],
            ]
        ]
        with self.assertRaises(InvalidPolygonError):
            validate_romania_polygon(huge_polygon)

    @patch("app.integrations.gee.aggregator.get_landsat_historical_series")
    @patch("app.integrations.gee.aggregator.get_sentinel1_sar_series")
    @patch("app.integrations.gee.aggregator.get_sentinel2_ndvi_series")
    def test_aggregator_combines_all_sensors(self, mock_s2, mock_s1, mock_landsat):
        """
        Checks that the aggregator validates the polygon and combines the results from all 3 sensors.
        """
        mock_s2.return_value = [{"date": "2025-07-10", "ndvi": 0.45}]
        mock_s1.return_value = [{"date": "2025-07-12", "sar_vv": -10.5, "sar_vh": -17.2}]
        mock_landsat.return_value = [{"year": 2024, "ndvi": 0.52, "lst_celsius": 29.1}]

        result = fetch_full_site_telemetry(
            polygon_coords=VALID_BUCHAREST_POLYGON,
            recent_start_date="2025-07-01",
            recent_end_date="2025-07-31",
            include_historical=True,
        )

        self.assertIn("geometry", result)
        self.assertEqual(result["optical_sentinel2"], [{"date": "2025-07-10", "ndvi": 0.45}])
        self.assertEqual(result["radar_sentinel1"], [{"date": "2025-07-12", "sar_vv": -10.5, "sar_vh": -17.2}])
        self.assertEqual(result["historical_landsat"], [{"year": 2024, "ndvi": 0.52, "lst_celsius": 29.1}])

    @patch("app.integrations.gee.aggregator.get_sentinel2_ndvi_series")
    def test_aggregator_stops_before_calling_gee_if_polygon_invalid(self, mock_s2):
        """
        Assures that the aggregator stops calling GEE if the polygon is invalid.
        """
        with self.assertRaises(InvalidPolygonError):
            fetch_full_site_telemetry(
                polygon_coords=[[[0.0, 0.0], [1.0, 1.0]]],
                recent_start_date="2025-07-01",
                recent_end_date="2025-07-31",
            )
        mock_s2.assert_not_called()


if __name__ == "__main__":
    unittest.main()