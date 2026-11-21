from datetime import date
from typing import Sequence, Any
import uuid

from sqlalchemy import select, ScalarResult
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, selectinload

from app.models.geometry_utils import geojson_polygon_to_wkt_element
from app.models.spatial import (
    MonitoredSite,
    SatelliteSnapshot,
    SiteAlert,
    SiteCategory
)

class SiteRepository:
    """
    Data-access layer encapsulating all PostgreSQL + PostGIS queries.
    """
    def __init__(self, db: Session) -> None:
        """
        Initialize the repository with an active SQLAlchemy database session.
        :param db: the SQLAlchemy database session used to execute database operations.
        """
        self.db = db

    def create_site(self, *, name: str, city: str, category: SiteCategory,
                    area_hectares: float, geojson_boundary: dict, metadata_json: dict | None = None) -> MonitoredSite:
        """
        Create and persist a new monitored site with its spatial boundary.
        Converts the input GeoJSON polygon into a PostGIS-compatiblw WKT element
        using SRID 4326 (WGS 84 - Word Geodetic System 1984) before committing the record to the database.
        :param name: human-readable name of the site
        :param city: city name where the site is located
        :param category: classification of the site (e.g. industrial, logistics, etc.)
        :param area_hectares: surface area of the site in hectares
        :param geojson_boundary: GeoJSON polygon defining the site's boundary
        :param metadata_json: optional metadata associated with the site (e.g. estimated Euro/sqm, zoning notes)
        :return: the newly created MonitoredSite object
        """
        wtk_boundary = geojson_polygon_to_wkt_element(geojson_boundary, srid=4326)
        site = MonitoredSite(
            name=name,
            city=city,
            category=category,
            area_hectares=area_hectares,
            boundary=wtk_boundary,
            metadata_json=metadata_json,
        )
        self.db.add(site)
        self.db.commit()
        self.db.refresh(site)
        return site

    def get_site_by_id(self, site_id: uuid.UUID) -> ScalarResult[Any]:
        """
        Retrieve a single monitored site by its UUID, including its associated snapshots and alerts.
        Eagerly loads the snapshots and alerts to avoid additional database queries.
        :param site_id: the unique identifier of the site
        :return: the matching MonitoredSite instance, or None if not found
        """
        stmt = (
            select(MonitoredSite)
            .options(
                selectinload(MonitoredSite.snapshots),
                selectinload(MonitoredSite.alerts),
            )
            .where(MonitoredSite.id == site_id)
        )
        return self.db.scalars(stmt)

    def list_sites(self, city: str | None = None) -> Sequence[MonitoredSite]:
        """
        List all monitored sites, optionally filtered by city.
        Eagerly loads the alerts for each site and orders the results from newest to oldest.
        :param city: optional city name for case-insensitive filtering
        :return: a sequence of MonitoredSite instances matching the filter criteria
        """
        stmt = (
            select(MonitoredSite)
            .options(selectinload(MonitoredSite.alerts))
        )
        if city:
            stmt = stmt.where(MonitoredSite.city.ilike(city))
        stmt = stmt.order_by(MonitoredSite.created_at.desc())
        return self.db.scalars(stmt).all()

    def upsert_snapshots(self, site_id: uuid.UUID, snapshot_data: list[dict],) -> int:
        """
        Idempotently insert or update satellite telemetry rows for a given site.
        Uses PostgreSQL's ON CONFLICT DO UPDATE against the 'uq_site_sensor_date' unique constraint
        to overwrite metrics if a record with the same site, sensor, and observation date already exists.
        :param site_id: the unique identifier of the site
        :param snapshot_data: a list of dictionaries containing telemetry metrics
        (e. g., sensor, observation_date, ndvi_mean, lst_celsius).
        :return: the total number of snapshot rows processed (inserted or updated)
        """
        if not snapshot_data:
            return 0

        rows = [
            {
                "id": uuid.uuid4(),
                "site_id": site_id,
                "sensor": item["sensor"],
                "observation_date": item["observation_date"],
                "ndvi_mean": item.get("ndvi_mean"),
                "ndvi_std": item.get("ndvi_std"),
                "lst_celsius": item.get("lst_celsius"),
                "sar_vv_db": item.get("sar_vv_db"),
                "sar_vh_db": item.get("sar_vh_db"),
                "valid_pixel_ratio": item.get("valid_pixel_ratio"),
                "raw_payload": item.get("raw_payload", {}),
            }
            for item in snapshot_data
        ]

        stmt = pg_insert(SatelliteSnapshot).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_site_sensor_date",
            set_={
                "ndvi_mean": stmt.excluded.ndvi_mean,
                "ndvi_std": stmt.excluded.ndvi_std,
                "lst_celsius": stmt.excluded.lst_celsius,
                "sar_vv_db": stmt.excluded.sar_vv_db,
                "sar_vh_db": stmt.excluded.sar_vh_db,
                "valid_pixel_ratio": stmt.excluded.valid_pixel_ratio,
                "raw_payload": stmt.excluded.raw_payload,
            },
        )

        self.db.execute(stmt)
        self.db.commit()
        return len(rows)

    def get_snapshots_for_site(self, site_id: uuid.UUID,
                               start_date: date | None = None, end_date: date | None = None,
                               sensor: str | None = None,) -> Sequence[SatelliteSnapshot]:
        """
        Fetch time-series satellite snapshots for a specific site within a specified site.
        Results are ordered chronologically by observation date (ascending).
        :param site_id: the UUID of the monitored site
        :param start_date: optional inclusive start date for filtering
        :param end_date: optional exclusive end date for filtering
        :param sensor: optional sensor identifier filter (e.g., 'Sentinel-2')
        :return: a sequence of SatelliteSnapshot records matching the query filters
        """
        stmt = select(SatelliteSnapshot).where(SatelliteSnapshot.site_id == site_id)
        if sensor:
            stmt = stmt.where(SatelliteSnapshot.sensor == sensor)
        if start_date:
            stmt = stmt.where(SatelliteSnapshot.observation_date >= start_date)
        if end_date:
            stmt = stmt.where(SatelliteSnapshot.observation_date <= end_date)
        stmt = stmt.order_by(SatelliteSnapshot.observation_date.asc())
        return self.db.scalars(stmt).all()

    def save_alert(self, alert: SiteAlert) -> SiteAlert:
        """
        Persist a new site alert to the database.
        :param alert: the SiteAlert ORM instance to be saved.
        :return: the persisted and refreshed SiteAlert instance.
        """
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_latest_alert(self, site_id: uuid.UUID) -> SiteAlert | None:
        """
        Retrieve the most recently detected alert for a given site.
        :param site_id: the UUID of the monitored site.
        :return: the latest SiteAlert instance, or None if the site has no alerts.
        """
        stmt = (
            select(SiteAlert)
            .where(SiteAlert.site_id == site_id)
            .order_by(SiteAlert.detected_at.desc())
            .limit(1)
        )

        return self.db.scalar(stmt)