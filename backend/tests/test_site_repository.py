import unittest
import uuid
from datetime import date
from unittest.mock import MagicMock

from app.models.spatial import AlertSeverity, SiteAlert, SiteCategory
from app.repositories.site_repository import SiteRepository

class TestSiteRepositoryUnit(unittest.TestCase):
    """Unit tests verifying SiteRepository query construction and transaction flow."""
    def setUp(self) -> None:
        self.mock_db = MagicMock()
        self.repo = SiteRepository(db=self.mock_db)
        self.sample_geojson = {
            "type": "Polygon",
            "coordinates": [
                [
                    [23.7210, 46.7890],
                    [23.7290, 46.7890],
                    [23.7290, 46.7940],
                    [23.7210, 46.7940],
                    [23.7210, 46.7890],
                ]
            ],
        }

    def test_create_site_persists_and_commits(self) -> None:
        """
        Check that the create_site method persists a new Site object to the database and commits the transaction.
        """
        site = self.repo.create_site(
            name="Cluj Innovation Corridor",
            city="Cluj-Napoca",
            category=SiteCategory.OFFICE_HUB,
            area_hectares=18.4,
            geojson_boundary=self.sample_geojson,
            metadata_json={"zoning": "Mixed Commercial"},
        )

        self.assertEqual(site.name, "Cluj Innovation Corridor")
        self.assertEqual(site.city, "Cluj-Napoca")
        self.mock_db.add.assert_called_once_with(site)
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(site)

    def test_upsert_snapshots_empty_list_noop(self) -> None:
        """
        Check that the upsert_snapshots method does nothing when given an empty list.
        """
        count = self.repo.upsert_snapshots(uuid.uuid4(), [])
        self.assertEqual(count, 0)
        self.mock_db.execute.assert_not_called()

    def test_upsert_snapshots_executes_and_commits(self) -> None:
        """
        Check that the upsert_snapshots method executes a bulk insert query and commits the transaction.
        """
        rows = [
            {
                "sensor": "SENTINEL_2",
                "observation_date": date(2026, 5, 10),
                "ndvi_mean": 0.61,
            },
            {
                "sensor": "SENTINEL_1",
                "observation_date": date(2026, 5, 12),
                "sar_vv_db": -10.4,
            },
        ]
        count = self.repo.upsert_snapshots(uuid.uuid4(), rows)
        self.assertEqual(count, 2)
        self.mock_db.execute.assert_called_once()
        self.mock_db.commit.assert_called_once()

    def test_save_alert_commits_and_refreshes(self) -> None:
        """
        Check that the save_alert method persists a new SiteAlert object to the database and commits the transaction.
        """
        alert = SiteAlert(
            site_id=uuid.uuid4(),
            severity=AlertSeverity.AMBER,
            signal_type="LAND_CLEARING",
            ndvi_delta_pct=-48.0,
            confidence_score=0.87,
        )
        saved = self.repo.save_alert(alert)
        self.assertEqual(saved, alert)
        self.mock_db.add.assert_called_once_with(alert)
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(alert)

if __name__ == "__main__":
    unittest.main()