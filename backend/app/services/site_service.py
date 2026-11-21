from collections import defaultdict
import csv
from datetime import date, datetime, timezone
import io
import math
from typing import Any
from uuid import UUID
from app.integrations.gee.validator import InvalidPolygonError, validate_romania_polygon
from sqlalchemy.orm import Session

from app.integrations.gee.aggregator import fetch_full_site_telemetry
from app.integrations.gee.validator import validate_romania_polygon
from app.models.geometry_utils import wkb_element_to_geojson
from app.models.spatial import SiteCategory
from app.repositories.site_repository import SiteRepository
from app.schemas.site import (
    AlertSummarySchema,
    SiteCreateRequest,
    SiteDetailResponse,
    SiteListItemResponse,
    SiteTimelineResponse,
    SpectralCorrelationPoint,
    SpectralCorrelationResponse,
    TimelinePoint,
)
from app.services.alert_engine import evaluate_site_anomalies
from app.services.intelligence_service import SiteNotFoundError


class InvalidSitePolygonError(Exception):
    """
    Raised when a submitted GeoJSON polygon fails geometric or Romania bounds validation.
    """

class SiteService:
    """
    Orchestrates SiteRepository, GEE validation/extraction, and AlertEngine.
    Provides a RESTful API for site management and telemetry.
    """
    def __init__(
        self,
        db: Session,
        site_repository: SiteRepository | None = None,
    ) -> None:
        self.db = db
        self.site_repo = site_repository or SiteRepository(db=self.db)

    def list_monitored_sites(
        self, city: str | None = None
    ) -> list[SiteListItemResponse]:
        """
        Return all monitored parcels (optionally filtered by city) with latest alerts.
        """
        sites = self.site_repo.list_sites(city=city)
        return [self._serialize_site_item(site) for site in sites]

    def get_monitored_site(self, site_id: UUID | str) -> SiteDetailResponse:
        """
        Return detailed parcel metadata, geometry, latest alert, and archive span.
        """
        site_uuid = UUID(str(site_id))
        site = self.site_repo.get_site_by_id(site_uuid).first()
        if site is None:
            raise SiteNotFoundError(f"Monitored site '{site_id}' was not found.")

        snapshots = self.site_repo.get_snapshots_for_site(site_uuid)
        years = [
            d.year
            for s in snapshots
            if (d := self._extract_date(s)) is not None
        ]

        base_item = self._serialize_site_item(site)
        return SiteDetailResponse(
            **base_item.model_dump(),
            snapshot_count=len(snapshots),
            archive_start_year=min(years) if years else None,
            archive_end_year=max(years) if years else None,
        )

    def create_and_analyze_site(
        self, payload: SiteCreateRequest
    ) -> SiteDetailResponse:
        """
        Validate a custom GeoJSON polygon, persist in PostGIS, and run EO + Alert pipeline.
        :param payload: the SiteCreateRequest payload
        """
        geojson_dict = payload.geometry.model_dump()
        try:
            validation_info = validate_romania_polygon(payload.geometry.coordinates)
        except (InvalidPolygonError, ValueError) as exc:
            raise InvalidSitePolygonError(str(exc)) from exc

        area_ha = (
            validation_info.get("area_hectares")
            if isinstance(validation_info, dict)
            else 10.0
        )

        category = self._resolve_site_category(payload.sector_type)

        site = self.site_repo.create_site(
            name=payload.name,
            city=payload.city,
            category=category,
            area_hectares=area_ha or 10.0,
            geojson_boundary=geojson_dict,
            metadata_json={"sector": payload.sector_type} if payload.sector_type else None,
        )

        if payload.run_live_gee:
            telemetry_bundle = fetch_full_site_telemetry(geojson_dict)
            snapshots_payload = (
                telemetry_bundle.get("snapshots", [])
                if isinstance(telemetry_bundle, dict)
                else []
            )
            if snapshots_payload:
                self.site_repo.upsert_snapshots(site.id, snapshots_payload)
                orm_snapshots = self.site_repo.get_snapshots_for_site(site.id)
                alert_result = evaluate_site_anomalies(site.id, orm_snapshots)
                if alert_result:
                    self.site_repo.save_alert(alert_result)

        return self.get_monitored_site(site.id)

    def get_site_timeline(
        self,
        site_id: UUID | str,
        start_year: int = 2000,
        end_year: int | None = None,
        sensor: str | None = None,
    ) -> SiteTimelineResponse:
        """Return chronological multi-sensor observations for the 2000–Present Timeline Slider."""
        site_uuid = UUID(str(site_id))
        site = self.site_repo.get_site_by_id(site_uuid).first()
        if site is None:
            raise SiteNotFoundError(f"Monitored site '{site_id}' was not found.")

        effective_end_year = end_year or datetime.now(timezone.utc).year
        start_dt = date(start_year, 1, 1)
        end_dt = date(effective_end_year, 12, 31)

        snapshots = self.site_repo.get_snapshots_for_site(
            site_uuid,
            start_date=start_dt,
            end_date=end_dt,
            sensor=sensor,
        )

        points: list[TimelinePoint] = []
        for snap in snapshots:
            obs_date = self._extract_date(snap)
            if obs_date is None:
                continue
            points.append(
                TimelinePoint(
                    observation_date=obs_date,
                    year=obs_date.year,
                    sensor=str(getattr(snap, "sensor", "UNKNOWN")),
                    ndvi=self._safe_float(
                        getattr(snap, "ndvi_mean", None) or getattr(snap, "ndvi", None)
                    ),
                    sar_vv_db=self._safe_float(
                        getattr(snap, "sar_vv_db", None)
                        or getattr(snap, "vv_mean", None)
                    ),
                    sar_vh_db=self._safe_float(
                        getattr(snap, "sar_vh_db", None)
                        or getattr(snap, "vh_mean", None)
                    ),
                    lst_c=self._safe_float(
                        getattr(snap, "lst_celsius", None)
                        or getattr(snap, "lst_c", None)
                    ),
                    cloud_cover_pct=self._safe_float(
                        getattr(snap, "cloud_cover_pct", None)
                    ),
                )
            )

        points.sort(key=lambda p: p.observation_date)

        return SiteTimelineResponse(
            site_id=str(site.id),
            site_name=site.name,
            city=site.city,
            start_year=start_year,
            end_year=effective_end_year,
            total_points=len(points),
            points=points,
        )

    def get_multispectral_correlations(
        self, site_id: UUID | str
    ) -> SpectralCorrelationResponse:
        """Align optical NDVI and radar SAR backscatter by month/year and compute Pearson r."""
        site_uuid = UUID(str(site_id))
        site = self.site_repo.get_site_by_id(site_uuid).first()
        if site is None:
            raise SiteNotFoundError(f"Monitored site '{site_id}' was not found.")

        snapshots = self.site_repo.get_snapshots_for_site(site_uuid)

        # Bucket observations by YYYY-MM so Sentinel-2 (optical) and Sentinel-1 (SAR) align cleanly
        buckets: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "dates": [],
                "ndvi": [],
                "vv": [],
                "vh": [],
                "lst": [],
            }
        )

        for snap in snapshots:
            obs_date = self._extract_date(snap)
            if obs_date is None:
                continue
            period_key = f"{obs_date.year:04d}-{obs_date.month:02d}"
            buckets[period_key]["dates"].append(obs_date)

            ndvi = self._safe_float(
                getattr(snap, "ndvi_mean", None) or getattr(snap, "ndvi", None)
            )
            vv = self._safe_float(
                getattr(snap, "sar_vv_db", None) or getattr(snap, "vv_mean", None)
            )
            vh = self._safe_float(
                getattr(snap, "sar_vh_db", None) or getattr(snap, "vh_mean", None)
            )
            lst = self._safe_float(
                getattr(snap, "lst_celsius", None) or getattr(snap, "lst_c", None)
            )

            if ndvi is not None:
                buckets[period_key]["ndvi"].append(ndvi)
            if vv is not None:
                buckets[period_key]["vv"].append(vv)
            if vh is not None:
                buckets[period_key]["vh"].append(vh)
            if lst is not None:
                buckets[period_key]["lst"].append(lst)

        series: list[SpectralCorrelationPoint] = []
        paired_ndvi: list[float] = []
        paired_vv: list[float] = []

        for period_key in sorted(buckets.keys()):
            b = buckets[period_key]
            avg_ndvi = self._mean(b["ndvi"])
            avg_vv = self._mean(b["vv"])
            avg_vh = self._mean(b["vh"])
            avg_lst = self._mean(b["lst"])
            rep_date = min(b["dates"])

            if avg_ndvi is not None and avg_vv is not None:
                paired_ndvi.append(avg_ndvi)
                paired_vv.append(avg_vv)

            regime = self._classify_point_regime(avg_ndvi, avg_vv)
            series.append(
                SpectralCorrelationPoint(
                    period=period_key,
                    observation_date=rep_date,
                    ndvi=round(avg_ndvi, 4) if avg_ndvi is not None else None,
                    sar_vv_db=round(avg_vv, 3) if avg_vv is not None else None,
                    sar_vh_db=round(avg_vh, 3) if avg_vh is not None else None,
                    lst_c=round(avg_lst, 2) if avg_lst is not None else None,
                    regime_label=regime,
                )
            )

        pearson_r = self._compute_pearson(paired_ndvi, paired_vv)
        interpretation = self._interpret_correlation(pearson_r, len(paired_ndvi))

        return SpectralCorrelationResponse(
            site_id=str(site.id),
            site_name=site.name,
            pearson_ndvi_vs_vv=pearson_r,
            interpretation=interpretation,
            series=series,
        )

    def export_site_telemetry_csv(
        self, site_id: UUID | str
    ) -> tuple[str, str]:
        """Generate a raw telemetry CSV string and filename for Enterprise Analytics export."""
        timeline = self.get_site_timeline(site_id=site_id, start_year=2000)

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "site_id",
                "site_name",
                "city",
                "observation_date",
                "year",
                "sensor",
                "ndvi",
                "sar_vv_db",
                "sar_vh_db",
                "lst_c",
                "cloud_cover_pct",
            ]
        )

        for pt in timeline.points:
            writer.writerow(
                [
                    timeline.site_id,
                    timeline.site_name,
                    timeline.city,
                    pt.observation_date.isoformat(),
                    pt.year,
                    pt.sensor,
                    pt.ndvi if pt.ndvi is not None else "",
                    pt.sar_vv_db if pt.sar_vv_db is not None else "",
                    pt.sar_vh_db if pt.sar_vh_db is not None else "",
                    pt.lst_c if pt.lst_c is not None else "",
                    pt.cloud_cover_pct if pt.cloud_cover_pct is not None else "",
                ]
            )

        safe_slug = (
            timeline.site_name.lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
        )
        filename = f"geoground_{safe_slug}_telemetry.csv"
        return filename, buffer.getvalue()

    def _serialize_site_item(self, site: Any) -> SiteListItemResponse:
        """Convert ORM MonitoredSite + eager-loaded alert into Pydantic response."""
        raw_geom = (
            getattr(site, "boundary", None)
            or getattr(site, "geometry", None)
            or getattr(site, "geom", None)
        )
        if isinstance(raw_geom, dict):
            geojson = raw_geom
        elif raw_geom is not None:
            geojson = wkb_element_to_geojson(raw_geom)
        else:
            geojson = {"type": "Polygon", "coordinates": []}

        latest_alert = getattr(site, "latest_alert", None)
        if latest_alert is None:
            alerts = getattr(site, "alerts", None) or []
            latest_alert = alerts[0] if alerts else None

        meta = getattr(site, "metadata_json", None) or {}
        cat = getattr(site, "category", None)
        sector = (
            getattr(site, "sector_type", None)
            or meta.get("sector")
            or (cat.value if hasattr(cat, "value") else str(cat) if cat else None)
        )

        severity_val = getattr(latest_alert, "severity", "GREEN") if latest_alert else "GREEN"
        if hasattr(severity_val, "value"):
            severity_val = severity_val.value

        alert_schema = AlertSummarySchema(
            signal_type=getattr(latest_alert, "signal_type", "BASELINE_STABLE")
            if latest_alert
            else "BASELINE_STABLE",
            severity=severity_val,
            confidence_score=self._safe_float(
                getattr(latest_alert, "confidence_score", 0.0)
            )
            or 0.0,
            ndvi_baseline=self._safe_float(getattr(latest_alert, "ndvi_baseline", None)),
            ndvi_current=self._safe_float(getattr(latest_alert, "ndvi_current", None)),
            ndvi_delta=self._safe_float(
                getattr(latest_alert, "ndvi_delta", None)
                or getattr(latest_alert, "ndvi_delta_pct", None)
            ),
            sar_vv_delta_db=self._safe_float(
                getattr(latest_alert, "sar_vv_delta_db", None)
                or getattr(latest_alert, "vv_delta_db", None)
            ),
            sar_vh_delta_db=self._safe_float(
                getattr(latest_alert, "sar_vh_delta_db", None)
                or getattr(latest_alert, "vh_delta_db", None)
            ),
            lst_current_c=self._safe_float(getattr(latest_alert, "lst_current_c", None)),
            lst_delta_c=self._safe_float(getattr(latest_alert, "lst_delta_c", None)),
            observation_window=getattr(latest_alert, "observation_window", None),
            evaluated_at=getattr(latest_alert, "detected_at", None)
            or getattr(latest_alert, "created_at", None),
        )

        return SiteListItemResponse(
            id=str(site.id),
            name=site.name,
            city=site.city,
            sector_type=sector,
            area_hectares=self._safe_float(getattr(site, "area_hectares", None)),
            geometry=geojson,
            latest_alert=alert_schema,
            created_at=getattr(site, "created_at", None),
        )

    @staticmethod
    def _resolve_site_category(sector_type: str | None) -> SiteCategory | str:
        if sector_type:
            upper = sector_type.upper()
            for member in SiteCategory:
                if member.name.upper() in upper or upper in member.name.upper():
                    return member
        return next(iter(SiteCategory))

    @staticmethod
    def _extract_date(snap: Any) -> date | None:
        val = getattr(snap, "observation_date", None) or getattr(snap, "date", None)
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val
        return None

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        """

        :param value:
        :return:
        """
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _mean(values: list[float]) -> float | None:
        """
        Return the mean of a list of values.
        :param values: the list of values
        :return: the mean value, or None if the list is empty
        """
        return sum(values) / len(values) if values else None

    @staticmethod
    def _classify_point_regime(ndvi: float | None, vv: float | None) -> str:
        """
        Classify the spectral regime of a given point based on its NDVI and SAR VV.
        :param ndvi: the NDVI value at the point
        :param vv: the SAR VV value at the point
        :return: the spectral regime label (e.g. "VEGETATED_BASELINE", "STRUCTURAL_BUILDUP")
        """
        if ndvi is not None and vv is not None:
            if ndvi < 0.30 and vv > -9.5:
                return "STRUCTURAL_BUILDUP"
            if ndvi < 0.30:
                return "EXPOSED_SOIL_OR_PAVED"
        return "VEGETATED_BASELINE"

    @staticmethod
    def _compute_pearson(xs: list[float], ys: list[float]) -> float | None:
        """
        Compute the Pearson correlation coefficient between two sets of paired observations.
        :param xs: the first set of paired observations
        :param ys: the second set of paired observations
        :return: the Pearson correlation coefficient, or None if insufficient observations
        """
        n = len(xs)
        if n < 3 or len(ys) != n:
            return None
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        den_x = sum((x - mean_x) ** 2 for x in xs)
        den_y = sum((y - mean_y) ** 2 for y in ys)
        denom = math.sqrt(den_x * den_y)
        if denom == 0:
            return None
        return round(num / denom, 4)

    @staticmethod
    def _interpret_correlation(pearson_r: float | None, sample_count: int) -> str:
        """
        Return a human-readable interpretation of the Pearson correlation coefficient.
        :param pearson_r: the Pearson correlation coefficient, or None if insufficient observations
        :param sample_count: the number of overlapping periods (e.g. 12 months)
        :return: a human-readable string describing the correlation
        """
        if pearson_r is None:
            return (
                f"Insufficient paired optical/SAR observations ({sample_count} overlapping periods) "
                "to establish a statistically valid correlation."
            )
        if pearson_r <= -0.5:
            return (
                f"Strong inverse correlation (r = {pearson_r:+.2f}): declining vegetation (NDVI) "
                "coincides with rising radar backscatter (SAR VV), characteristic of active construction."
            )
        if pearson_r >= 0.5:
            return (
                f"Positive correlation (r = {pearson_r:+.2f}): optical and radar signals co-vary "
                "with seasonal surface moisture rather than structural conversion."
            )
        return (
            f"Weak or decoupled spectral relationship (r = {pearson_r:+.2f}): surface structure "
            "and vegetation canopy are evolving independently."
        )