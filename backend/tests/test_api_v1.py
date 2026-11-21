"""Unit & endpoint tests for GeoGround REST API v1 using FastAPI TestClient."""

from datetime import date, datetime, timezone
import unittest
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.dependencies import get_intelligence_service, get_site_service
from app.api.v1.router import api_router
from app.schemas.intelligence import ExecutiveSummaryResponse, SiteChatResponse
from app.schemas.site import (
    AlertSummarySchema,
    SiteDetailResponse,
    SiteListItemResponse,
    SiteTimelineResponse,
    SpectralCorrelationPoint,
    SpectralCorrelationResponse,
    TimelinePoint,
)
from app.services.intelligence_service import SiteNotFoundError
from app.services.site_service import InvalidSitePolygonError


class TestApiV1Endpoints(unittest.TestCase):
    """End-to-end HTTP layer tests with mocked SiteService and IntelligenceService."""

    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.include_router(api_router)

        self.mock_site_service = MagicMock()
        self.mock_intel_service = MagicMock()

        self.app.dependency_overrides[get_site_service] = lambda: self.mock_site_service
        self.app.dependency_overrides[get_intelligence_service] = (
            lambda: self.mock_intel_service
        )
        self.client = TestClient(self.app)

        self.site_id = "11111111-1111-1111-1111-111111111111"
        self.sample_site = SiteDetailResponse(
            id=self.site_id,
            name="Tetarom III Industrial Corridor",
            city="Cluj-Napoca",
            sector_type="Industrial & Logistics",
            area_hectares=18.4,
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [23.781, 46.842],
                        [23.786, 46.842],
                        [23.786, 46.846],
                        [23.781, 46.846],
                        [23.781, 46.842],
                    ]
                ],
            },
            latest_alert=AlertSummarySchema(
                signal_type="STRUCTURAL_EXPANSION",
                severity="AMBER",
                confidence_score=0.91,
                ndvi_delta=-0.05,
                sar_vv_delta_db=3.3,
            ),
            snapshot_count=18,
            archive_start_year=2000,
            archive_end_year=2026,
        )

    def test_list_sites_filtered_by_city(self) -> None:
        self.mock_site_service.list_monitored_sites.return_value = [
            SiteListItemResponse(**self.sample_site.model_dump())
        ]

        res = self.client.get("/api/v1/sites?city=Cluj-Napoca")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["city"], "Cluj-Napoca")
        self.mock_site_service.list_monitored_sites.assert_called_once_with(
            city="Cluj-Napoca"
        )

    def test_create_site_invalid_polygon_returns_422(self) -> None:
        self.mock_site_service.create_and_analyze_site.side_effect = (
            InvalidSitePolygonError("Polygon coordinates lie outside Romania bounds.")
        )

        payload = {
            "name": "Out of Bounds Parcel",
            "city": "Vienna",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [16.3, 48.2],
                        [16.4, 48.2],
                        [16.4, 48.3],
                        [16.3, 48.3],
                        [16.3, 48.2],
                    ]
                ],
            },
        }
        res = self.client.post("/api/v1/sites", json=payload)
        self.assertEqual(res.status_code, 422)
        self.assertIn("Romania bounds", res.json()["detail"])

    def test_get_site_timeline_and_not_found(self) -> None:
        self.mock_site_service.get_site_timeline.return_value = SiteTimelineResponse(
            site_id=self.site_id,
            site_name="Tetarom III Industrial Corridor",
            city="Cluj-Napoca",
            start_year=2000,
            end_year=2026,
            total_points=1,
            points=[
                TimelinePoint(
                    observation_date=date(2005, 7, 15),
                    year=2005,
                    sensor="LANDSAT",
                    ndvi=0.66,
                    lst_c=27.4,
                )
            ],
        )

        res = self.client.get(f"/api/v1/sites/{self.site_id}/timeline?start_year=2000")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["points"][0]["year"], 2005)

        self.mock_site_service.get_site_timeline.side_effect = SiteNotFoundError(
            "Not found"
        )
        res_404 = self.client.get("/api/v1/sites/missing-id/timeline")
        self.assertEqual(res_404.status_code, 404)

    def test_get_multispectral_correlations(self) -> None:
        self.mock_site_service.get_multispectral_correlations.return_value = (
            SpectralCorrelationResponse(
                site_id=self.site_id,
                site_name="Tetarom III Industrial Corridor",
                pearson_ndvi_vs_vv=-0.84,
                interpretation="Strong inverse correlation indicating active construction.",
                series=[
                    SpectralCorrelationPoint(
                        period="2026-08",
                        observation_date=date(2026, 8, 10),
                        ndvi=0.21,
                        sar_vv_db=-7.8,
                        sar_vh_db=-13.9,
                        lst_c=32.1,
                        regime_label="STRUCTURAL_BUILDUP",
                    )
                ],
            )
        )

        res = self.client.get(f"/api/v1/sites/{self.site_id}/correlations")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["pearson_ndvi_vs_vv"], -0.84)
        self.assertEqual(body["series"][0]["regime_label"], "STRUCTURAL_BUILDUP")

    def test_export_csv_streams_attachment(self) -> None:
        csv_text = "site_id,site_name,ndvi\n1111,Tetarom III,0.21\n"
        self.mock_site_service.export_site_telemetry_csv.return_value = (
            "geoground_tetarom_iii_telemetry.csv",
            csv_text,
        )

        res = self.client.get(f"/api/v1/sites/{self.site_id}/export/csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.headers["content-type"])
        self.assertIn(
            "geoground_tetarom_iii_telemetry.csv",
            res.headers["content-disposition"],
        )
        self.assertEqual(res.text, csv_text)

    def test_intelligence_endpoints(self) -> None:
        self.mock_intel_service.get_site_executive_summary.return_value = (
            ExecutiveSummaryResponse(
                site_id=self.site_id,
                site_name="Tetarom III Industrial Corridor",
                signal_type="STRUCTURAL_EXPANSION",
                severity="AMBER",
                summary="Vertical warehouse structure expansion confirmed via SAR VV spike.",
                key_signals=["SAR VV +3.30 dB", "Confidence 91%"],
                provider_used="gemini:gemini-2.5-flash",
                generated_at=datetime.now(timezone.utc),
            )
        )
        self.mock_intel_service.answer_site_chat.return_value = SiteChatResponse(
            site_id=self.site_id,
            reply="SAR VV increased by +3.30 dB in 2026.",
            referenced_metrics={"sar_vv_delta_db": 3.3},
            provider_used="gemini:gemini-2.5-flash",
        )

        res_brief = self.client.get(f"/api/v1/sites/{self.site_id}/executive-summary")
        self.assertEqual(res_brief.status_code, 200)
        self.assertEqual(res_brief.json()["provider_used"], "gemini:gemini-2.5-flash")

        res_chat = self.client.post(
            f"/api/v1/sites/{self.site_id}/chat",
            json={"message": "Explain the radar spike.", "active_year": 2026},
        )
        self.assertEqual(res_chat.status_code, 200)
        self.assertIn("+3.30 dB", res_chat.json()["reply"])


if __name__ == "__main__":
    unittest.main()