from datetime import date
import unittest
from unittest.mock import MagicMock
from types import SimpleNamespace

from app.integrations.llm.client import LLMGenerationResult
from app.schemas.intelligence import SiteChatRequest
from app.services.intelligence_service import IntelligenceService, SiteNotFoundError


class TestIntelligenceService(unittest.TestCase):
    """
    Tests verifying spatial data loading, error handling, and response assembly.
    """
    def setUp(self) -> None:
        self.mock_db = MagicMock()
        self.mock_repo = MagicMock()
        self.mock_llm = MagicMock()

        self.fake_site = SimpleNamespace(
            id="22222222-2222-2222-2222-222222222222",
            name="Pipera Nord Retail Park",
            city="Bucharest",
            area_hectares=8.2,
        )
        self.fake_alert = SimpleNamespace(
            signal_type="LAND_CLEARING",
            severity="AMBER",
            confidence_score=0.87,
            ndvi_baseline=0.61,
            ndvi_current=0.22,
            ndvi_delta=-0.39,
            sar_vv_delta_db=0.4,
            sar_vh_delta_db=0.2,
            lst_current_c=29.5,
            lst_delta_c=1.9,
            observation_window="2026-09-01 to 2026-10-20",
        )
        self.fake_snapshots = [
            SimpleNamespace(
                observation_date=date(2012, 7, 15),
                sensor="LANDSAT",
                ndvi_mean=0.64,
                vv_mean=None,
                lst_c=27.1,
            ),
            SimpleNamespace(
                observation_date=date(2026, 10, 15),
                sensor="SENTINEL-2",
                ndvi_mean=0.22,
                vv_mean=-11.2,
                lst_c=29.5,
            ),
        ]

        self.service = IntelligenceService(
            db=self.mock_db,
            site_repository=self.mock_repo,
            llm_client=self.mock_llm,
        )

    def test_get_site_executive_summary_success(self) -> None:
        """
        Test that the service returns a valid response when all dependencies are met.
        """
        self.mock_repo.get_site_by_id.return_value = self.fake_site
        self.mock_repo.get_latest_alert.return_value = self.fake_alert
        self.mock_repo.get_snapshots_for_site.return_value = self.fake_snapshots
        self.mock_llm.generate_executive_summary.return_value = LLMGenerationResult(
            text="Vegetation clearing confirmed across 8.2 ha in Pipera Nord.",
            provider="gemini:gemini-2.5-flash",
        )

        response = self.service.get_site_executive_summary(self.fake_site.id)

        self.assertEqual(response.site_name, "Pipera Nord Retail Park")
        self.assertEqual(response.signal_type, "LAND_CLEARING")
        self.assertEqual(response.severity, "AMBER")
        self.assertIn("NDVI -0.39", response.key_signals)
        self.assertEqual(response.provider_used, "gemini:gemini-2.5-flash")

    def test_answer_site_chat_passes_active_year_and_metrics(self) -> None:
        """
        Test that the service passes the active year and metrics to the LLM.
        """
        self.mock_repo.get_site_by_id.return_value = self.fake_site
        self.mock_repo.get_latest_alert.return_value = self.fake_alert
        self.mock_repo.get_snapshots_for_site.return_value = self.fake_snapshots
        self.mock_llm.generate_chat_reply.return_value = LLMGenerationResult(
            text="In 2012, Landsat recorded dense vegetation (NDVI 0.64).",
            provider="gemini:gemini-2.5-flash",
        )

        req = SiteChatRequest(
            message="How did this parcel look in 2012?",
            active_year=2012,
        )
        res = self.service.answer_site_chat(self.fake_site.id, req)

        self.assertEqual(res.referenced_metrics["ndvi_delta"], -0.39)
        self.assertIn("2012", res.reply)
        called_telemetry = self.mock_llm.generate_chat_reply.call_args.kwargs["telemetry"]
        self.assertIn("2012-07-15", called_telemetry.historical_trend_notes)

    def test_raises_site_not_found_when_missing(self) -> None:
        """
        Test that the service raises a SiteNotFoundError when the site is not found.
        """
        self.mock_repo.get_site_by_id.return_value = None

        with self.assertRaises(SiteNotFoundError):
            self.service.get_site_executive_summary("99999999-9999-9999-9999-999999999999")


if __name__ == "__main__":
    unittest.main()