from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

class GeoJSONPolygon(BaseModel):
    """
    RFC 7946 GeoJSON Polygon geometry in EPSG:4326 ([lon, lat]).
    """
    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[list[float]]] = Field(
        ...,
        description="Linear rings of [longitude, latitude] coordinate pairs.",
    )


class SiteCreateRequest(BaseModel):
    """
    Payload for registering and analyzing a custom commercial real-estate parcel.
    The geometry must be a valid GeoJSON Polygon in EPSG:4326.
    """
    name: str = Field(..., min_length=2, max_length=160)
    city: str = Field(..., min_length=2, max_length=80)
    sector_type: str = Field(
        default="Industrial & Logistics",
        max_length=80,
        description="CRE asset class (e.g., Industrial & Logistics, Retail Park, Mixed-Use).",
    )
    geometry: GeoJSONPolygon
    run_live_gee: bool = Field(
        default=True,
        description="When True, triggers live Google Earth Engine multi-sensor extraction on creation.",
    )


class AlertSummarySchema(BaseModel):
    """
    Latest anomaly detection classification for a monitored site.
    """
    signal_type: str = "BASELINE_STABLE"
    severity: Literal["GREEN", "AMBER"] = "GREEN"
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    ndvi_baseline: float | None = None
    ndvi_current: float | None = None
    ndvi_delta: float | None = None
    sar_vv_delta_db: float | None = None
    sar_vh_delta_db: float | None = None
    lst_current_c: float | None = None
    lst_delta_c: float | None = None
    observation_window: str | None = None
    evaluated_at: datetime | None = None


class SiteListItemResponse(BaseModel):
    """
    Compact site representation used for map markers, polygons, and portfolio tables.
    Includes basic parcel metadata and the latest anomaly detection classification.
    """
    id: str
    name: str
    city: str
    sector_type: str | None = None
    area_hectares: float | None = None
    geometry: dict[str, Any]
    latest_alert: AlertSummarySchema
    created_at: datetime | None = None


class SiteDetailResponse(SiteListItemResponse):
    """
    Full parcel metadata returned when inspecting an individual site.
    """
    snapshot_count: int = 0
    archive_start_year: int | None = None
    archive_end_year: int | None = None


class TimelinePoint(BaseModel):
    """
    Single chronological observation point for the 2000–Present Timeline Slider.
    """
    observation_date: date
    year: int
    sensor: str
    ndvi: float | None = None
    sar_vv_db: float | None = None
    sar_vh_db: float | None = None
    lst_c: float | None = None
    cloud_cover_pct: float | None = None


class SiteTimelineResponse(BaseModel):
    """
    Chronological 2000–present telemetry series powering the Timeline Slider.
    """
    site_id: str
    site_name: str
    city: str
    start_year: int
    end_year: int
    total_points: int
    points: list[TimelinePoint]


class SpectralCorrelationPoint(BaseModel):
    """
    Aligned optical vs. radar vs. thermal telemetry record for Enterprise Analytics charts.
    """
    period: str
    observation_date: date
    ndvi: float | None = None
    sar_vv_db: float | None = None
    sar_vh_db: float | None = None
    lst_c: float | None = None
    regime_label: str = "BASELINE"


class SpectralCorrelationResponse(BaseModel):
    """
    Multispectral correlation dataset (NDVI vs. SAR VV/VH) + summary statistics.
    """
    site_id: str
    site_name: str
    pearson_ndvi_vs_vv: float | None = Field(
        default=None,
        description="Pearson correlation coefficient between optical NDVI and SAR VV backscatter.",
    )
    interpretation: str
    series: list[SpectralCorrelationPoint]