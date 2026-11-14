import unittest
from unittest.mock import patch, MagicMock

from app.integrations.gee.client import init_gee
from app.integrations.gee.sentinel1 import get_sentinel1_sar_series

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

class TestSentinel1SAR(unittest.TestCase):
    @patch("app.integrations.gee.sentinel1.ee")
    def test_sar_series_parsing_and_sorting_mocked(self, mock_ee):
        """
        Offline unit test for get_sentinel1_sar_series.
        Checks that VV/VH are extracted, rounded to 2 decimal places, and sorted by date.
        """
        mock_chain = (
            mock_ee.ImageCollection.return_value
            .filterBounds.return_value
            .filterDate.return_value
            .filter.return_value
            .filter.return_value
            .filter.return_value
            .filter.return_value
            .select.return_value
        )

        mock_chain.map.return_value.getInfo.return_value = {
            "features": [
                {"properties": {"timestamp": 1749513600000, "vv": -9.8432, "vh": -16.129}},  # 2025-06-10
                {"properties": {"timestamp": 1748908800000, "vv": -12.456, "vh": -19.001}},  # 2025-06-03
                {"properties": {"timestamp": 1749000000000, "vv": None, "vh": -18.0}},       # incomplete -> ignored
            ]
        }

        result = get_sentinel1_sar_series(
            polygon_coords=CLUJ_TEST_POLYGON,
            start_date="2025-06-01",
            end_date="2025-06-15",
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"date": "2025-06-03", "sar_vv": -12.46, "sar_vh": -19.0})
        self.assertEqual(result[1], {"date": "2025-06-10", "sar_vv": -9.84, "sar_vh": -16.13})

    def test_sar_series_live_cluj_polygon(self):
        """
        Real unit test for get_sentinel1_sar_series on the Gooogle Earth Engine server for the Cluj-Napoca polygon.
        """
        init_gee()
        result = get_sentinel1_sar_series(
            polygon_coords=CLUJ_TEST_POLYGON,
            start_date="2025-06-01",
            end_date="2025-07-31",
        )

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0, "Sentinel-1 should have radar images every ~6-12 days.")

        for point in result:
            self.assertIn("date", point)
            self.assertIn("sar_vv", point)
            self.assertIn("sar_vh", point)
            # Typical physical backscatter over land values are negative (between -35 dB and +5 dB)
            self.assertGreater(point["sar_vv"], -35.0)
            self.assertLess(point["sar_vv"], 5.0)


if __name__ == "__main__":
    unittest.main()