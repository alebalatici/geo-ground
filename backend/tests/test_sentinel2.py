import unittest
from unittest.mock import patch, MagicMock

from app.integrations.gee.client import init_gee
from app.integrations.gee.sentinel2 import get_sentinel2_ndvi_series

# Real polygon in the north part of Cluj-Napoca (Dealul Lomb / Tetarom)
CLUJ_TEST_POLYGON = [
    [
        [23.5750, 46.7980],
        [23.5850, 46.7980],
        [23.5850, 46.8040],
        [23.5750, 46.8040],
        [23.5750, 46.7980],
    ]
]

class TestSentinel2NDVI(unittest.TestCase):
    @patch("app.integrations.gee.sentinel2.ee")
    def test_ndvi_series_parsing_and_sorting_mocked(self, mock_ee):
        """
        Offline unit test for get_sentinel2_ndvi_series.
        Checks that the function filters out None values and sorts the result by date.
        """
        mock_collection = MagicMock()
        mock_ee.ImageCollection.return_value.filterBounds.return_value.filterDate.return_value.filter.return_value.map.return_value.map.return_value = mock_collection

        # We simulate the response from Google: 2 valid images (unsorted) + 1 incomplete image (ndvi=None)
        mock_collection.map.return_value.getInfo.return_value = {
            "features": [
                {"properties": {"timestamp": 1747267200000, "ndvi": 0.61234}},  # 2025-05-15
                {"properties": {"timestamp": 1746057600000, "ndvi": None}},     # 2025-05-01 (clouds -> ignored)
                {"properties": {"timestamp": 1746403200000, "ndvi": 0.54891}},  # 2025-05-05
            ]
        }

        result = get_sentinel2_ndvi_series(
            polygon_coords=CLUJ_TEST_POLYGON,
            start_date="2025-05-01",
            end_date="2025-05-30",
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"date": "2025-05-05", "ndvi": 0.5489})
        self.assertEqual(result[1], {"date": "2025-05-15", "ndvi": 0.6123})

    def test_ndvi_series_live_cluj_polygon(self):
        """
        Real unit test for get_sentinel2_ndvi_series on the Gooogle Earth Engine server.
        Extracts NDVI from Sentinel-2 imagery for a specific polygon in the north part of Cluj-Napoca in summer 2025.
        """
        init_gee()
        result = get_sentinel2_ndvi_series(
            polygon_coords=CLUJ_TEST_POLYGON,
            start_date="2025-06-01",
            end_date="2025-08-31",
            max_cloud_cover=20,
        )

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0, "There should be at least one image withoud clouds in the polygon in summer 2025")

        for point in result:
            self.assertIn("date", point)
            self.assertIn("ndvi", point)
            # The NDVI value is always between -1.0 and +1.0
            self.assertGreaterEqual(point["ndvi"], -1.0)
            self.assertLessEqual(point["ndvi"], 1.0)


if __name__ == "__main__":
    unittest.main()