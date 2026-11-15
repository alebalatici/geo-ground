import enum
import uuid
from datetime import date, datetime, timezone
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AlertSeverity(str, enum.Enum):
    GREEN = "GREEN"   # Normal baseline / stable vegetation & backscatter
    AMBER = "AMBER"   # Early-warning signal: land clearing or structural spike


class SiteCategory(str, enum.Enum):
    LOGISTICS = "LOGISTICS"
    RETAIL_PARK = "RETAIL_PARK"
    OFFICE_HUB = "OFFICE_HUB"
    RESIDENTIAL = "RESIDENTIAL"
    INDUSTRIAL = "INDUSTRIAL"

class MonitoredSite(Base):
    """Commercial real estate / development parcel tracked via satellite telemetry."""

    __tablename__ = "monitored_sites"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    category: Mapped[SiteCategory] = mapped_column(
        Enum(SiteCategory, name="site_category_enum"),
        nullable=False,
        default=SiteCategory.INDUSTRIAL,
    )
    area_hectares: Mapped[float] = mapped_column(Float, nullable=False)

    # Polygon stored in WGS84 (lon/lat); GeoAlchemy2 creates a GIST spatial index automatically
    boundary: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True),
        nullable=False,
    )

    # Cached valuation & metadata context (e.g. estimated EUR/sqm, zoning notes)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    snapshots: Mapped[list["SatelliteSnapshot"]] = relationship(
        back_populates="site",
        cascade="all, delete-orphan",
        order_by="SatelliteSnapshot.observation_date.asc()",
    )
    alerts: Mapped[list["SiteAlert"]] = relationship(
        back_populates="site",
        cascade="all, delete-orphan",
        order_by="SiteAlert.detected_at.desc()",
    )


class SatelliteSnapshot(Base):
    """Cached multi-sensor observation for a specific date/period on a MonitoredSite."""
    __tablename__ = "satellite_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "site_id", "sensor", "observation_date", name="uq_site_sensor_date"
        ),
        Index("ix_snapshots_site_date", "site_id", "observation_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monitored_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    sensor: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "SENTINEL_2", "SENTINEL_1", "LANDSAT_HARMONIZED"
    observation_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Optical & Thermal Metrics
    ndvi_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    ndvi_std: Mapped[float | None] = mapped_column(Float, nullable=True)
    lst_celsius: Mapped[float | None] = mapped_column(Float, nullable=True)

    # SAR Radar Backscatter Metrics (dB)
    sar_vv_db: Mapped[float | None] = mapped_column(Float, nullable=True)
    sar_vh_db: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Quality / Cloud coverage metadata
    valid_pixel_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    site: Mapped["MonitoredSite"] = relationship(back_populates="snapshots")


class SiteAlert(Base):
    """Automated early-warning economic signal generated from telemetry anomalies."""
    __tablename__ = "site_alerts"
    __table_args__ = (
        Index("ix_alerts_site_detected", "site_id", "detected_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monitored_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity_enum"),
        nullable=False,
        default=AlertSeverity.GREEN,
    )
    signal_type: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # e.g., "LAND_CLEARING", "STRUCTURAL_EXPANSION", "BASELINE_STABLE"

    # Quantitative deltas backing the alert
    ndvi_delta_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    sar_vv_delta_db: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # LLM-generated executive summary (populated by app/integrations/llm/)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    site: Mapped["MonitoredSite"] = relationship(back_populates="alerts")