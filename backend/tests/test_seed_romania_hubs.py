"""Unit tests validating Romanian demo hub polygons, calibrated archives, and seeding idempotency."""

import unittest
from unittest.mock import MagicMock, patch

from app.integrations.gee.validator import validate_romania_polygon
from scripts.seed_romania_hubs import (
    ROMANIA_DEMO_HUBS,
    build_calibrated_archive,
    seed_romania_hubs,
)


class TestSeedRomaniaHubs(unittest.TestCase):
    """Tests ensuring all seeded hubs pass Romania GeoJSON validation and do not duplicate."""

    def test_all_demo_hub_polygons_are_valid_in_romania(self) -> None:
        self.assertGreaterEqual(len(ROMANIA_DEMO_HUBS), 6)
        cities = {hub["city"] for hub in ROMANIA_DEMO_HUBS}
        self.assertEqual(cities, {"Cluj-Napoca", "Bucharest", "Timișoara"})

        for hub in ROMANIA_DEMO_HUBS:
            # Must not raise ValueError
            validate_romania_polygon(hub["geometry"])
            snapshots, alert = build_calibrated_archive(hub["profile"])
            self.assertGreaterEqual(len(snapshots), 15)
            self.assertEqual(alert["signal_type"], hub["profile"])

    @patch("scripts.seed_romania_hubs.SiteRepository")
    @patch("scripts.seed_romania_hubs.SessionLocal")
    @patch("scripts.seed_romania_hubs.init_db")
    def test_seed_is_idempotent_when_hubs_exist(
        self,
        mock_init_db: MagicMock,
        mock_session_cls: MagicMock,
        mock_repo_cls: MagicMock,
    ) -> None:
        mock_repo = MagicMock()
        mock_repo.list_sites.return_value = [
            MagicMock(name=hub["name"]) for hub in ROMANIA_DEMO_HUBS
        ]
        # Ensure .name attribute returns the actual string rather than MagicMock name
        for mock_obj, hub in zip(mock_repo.list_sites.return_value, ROMANIA_DEMO_HUBS):
            mock_obj.name = hub["name"]

        mock_repo_cls.return_value = mock_repo

        created = seed_romania_hubs(use_live_gee=False)
        self.assertEqual(created, 0)
        mock_repo.create_site.assert_not_called()


if __name__ == "__main__":
    unittest.main()