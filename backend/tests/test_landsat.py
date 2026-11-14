import unittest
from unittest.mock import patch, MagicMock

from app.integrations.gee.client import init_gee
from app.integrations.gee.landsat import get_landsat_historical_series


# Polygon in the industrial/logistical area of Floresti - Gilau (near Cluj-Napoca) where the agricultural terrains in the 2000s were new constructions were being made

CLUJ_WEST_CORRIDOR_POLYGON = [
    [
        [23.4700, 46.7420],
        [23.4820, 46.7420],
        [23.4820, 46.7480],
        [23.4700, 46.7480],
        [23.4700, 46.7420],
    ]
]


class TestLandsatHistorical(unittest.TestCase):
    def test_invalid_year_range_raises_value_error(self):
        """
        Checks that the function raises a ValueError if the start_year is before 2000 or if the end_year is after 2024.
        """
        with self.assertRaises(ValueError):
            get_landsat_historical_series(CLUJ_WEST_CORRIDOR_POLYGON, start_year=1995, end_year=2020)

        with self.assertRaises(ValueError):
            get_landsat_historical_series(CLUJ_WEST_CORRIDOR_POLYGON, start_year=2022, end_year=2020)

    @patch("app.integrations.gee.landsat.ee")
    def test_landsat_series_parsing_and_filtering_mocked(self, mock_ee):
        """
        Offline unit test for get_landsat_historical_series without images and NDVI + temperature formatting.
        """
        mock_fc = MagicMock()
        mock_ee.FeatureCollection.return_value = mock_fc

        mock_fc.getInfo.return_value = {
            "features": [
                {"properties": {"year": 2005, "image_count": 4, "ndvi": 0.67432, "lst_celsius": 25.891}},
                {"properties": {"year": 2012, "image_count": 0, "ndvi": None, "lst_celsius": None}},  # an fără date -> ignorat
                {"properties": {"year": 2000, "image_count": 3, "ndvi": 0.71234, "lst_celsius": 24.126}},
                {"properties": {"year": 2024, "image_count": 5, "ndvi": 0.24567, "lst_celsius": 31.458}},
            ]
        }

        result = get_landsat_historical_series(
            polygon_coords=CLUJ_WEST_CORRIDOR_POLYGON,
            start_year=2000,
            end_year=2024,
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], {"year": 2000, "ndvi": 0.7123, "lst_celsius": 24.13})
        self.assertEqual(result[1], {"year": 2005, "ndvi": 0.6743, "lst_celsius": 25.89})
        self.assertEqual(result[2], {"year": 2024, "ndvi": 0.2457, "lst_celsius": 31.46})

    def test_landsat_historical_live_2000_to_2025(self):
        """
        Real unit test on the Google Earth Engine server: extracts 26 years of historical Landsat 7 + 8 + 9 data for the Cluj-Napoca west corridor.
        """
        init_gee()
        result = get_landsat_historical_series(
            polygon_coords=CLUJ_WEST_CORRIDOR_POLYGON,
            start_year=2000,
            end_year=2025,
        )

        self.assertIsInstance(result, list)
        # For 26 years, we should have data for most of the years (at least 18-20 years)
        self.assertGreaterEqual(len(result), 18)

        for point in result:
            self.assertIn("year", point)
            self.assertIn("ndvi", point)
            self.assertIn("lst_celsius", point)
            self.assertGreaterEqual(point["ndvi"], -1.0)
            self.assertLessEqual(point["ndvi"], 1.0)
            # The surface temperature in the summer in Romania is between 10 C and 55 C
            self.assertGreater(point["lst_celsius"], 10.0)
            self.assertLess(point["lst_celsius"], 55.0)


if __name__ == "__main__":
    unittest.main()