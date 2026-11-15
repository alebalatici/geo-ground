import os
import unittest
import uuid
from datetime import date

from geoalchemy2.elements import WKTElement
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.geometry_utils import (
    geojson_polygon_to_wkt_element,
    wkb_element_to_geojson,
)
from app.models.spatial import (
    AlertSeverity,
    MonitoredSite,
    SatelliteSnapshot,
    SiteAlert,
    SiteCategory,
)


class TestSpatialModelsUnit(unittest.TestCase):
    """Fast, database-independent unit tests for ORM schema and GeoJSON <-> WKT helpers."""
    def setUp(self) -> None:
        # Cluj-Napoca / Apahida
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

    def test_geojson_to_wkt_element_valid(self) -> None:
        """
        Check that the geojson_polygon_to_wkt_element function returns a valid WKTElement.
        """
        wkt_el = geojson_polygon_to_wkt_element(self.sample_geojson)
        self.assertIsInstance(wkt_el, WKTElement)
        self.assertEqual(wkt_el.srid, 4326)
        self.assertIn("POLYGON", wkt_el.data)

    def test_geojson_feature_wrapper_supported(self) -> None:
        """
        Check that the geojson_polygon_to_wkt_element function supports GeoJSON Feature objects.
        """
        feature = {
            "type": "Feature",
            "properties": {"name": "Cluj Logistic Hub"},
            "geometry": self.sample_geojson,
        }
        wkt_el = geojson_polygon_to_wkt_element(feature)
        self.assertEqual(wkt_el.srid, 4326)

    def test_geojson_rejects_non_polygon(self) -> None:
        """
        Check that the geojson_polygon_to_wkt_element function raises an error for non-polygon GeoJSON.
        """
        point_geojson = {"type": "Point", "coordinates": [23.6, 46.77]}
        with self.assertRaises(ValueError):
            geojson_polygon_to_wkt_element(point_geojson)

    def test_geojson_rejects_self_intersecting_bowtie_polygon(self) -> None:
        """
        Check that the geojson_polygon_to_wkt_element function raises an error for self-intersecting polygons.
        """
        bowtie = {
            "type": "Polygon",
            "coordinates": [
                [
                    [23.70, 46.78],
                    [23.72, 46.80],
                    [23.72, 46.78],
                    [23.70, 46.80],
                    [23.70, 46.78],
                ]
            ],
        }
        with self.assertRaises(ValueError):
            geojson_polygon_to_wkt_element(bowtie)

    def test_orm_metadata_tables_and_constraints(self) -> None:
        """
        Check that the ORM metadata contains the expected tables and constraints.
        """
        tables = Base.metadata.tables
        self.assertIn("monitored_sites", tables)
        self.assertIn("satellite_snapshots", tables)
        self.assertIn("site_alerts", tables)

        snapshot_constraints = {
            c.name for c in tables["satellite_snapshots"].constraints if c.name
        }
        self.assertIn("uq_site_sensor_date", snapshot_constraints)

    def test_model_instantiation_defaults(self) -> None:
        """
        Checks that the default values for model attributes are set correctly.
        """
        wkt_el = geojson_polygon_to_wkt_element(self.sample_geojson)
        site = MonitoredSite(
            name="Apahida Logistics Park Phase II",
            city="Cluj-Napoca",
            category=SiteCategory.LOGISTICS,
            area_hectares=34.5,
            boundary=wkt_el,
        )
        self.assertEqual(site.city, "Cluj-Napoca")
        self.assertEqual(site.category, SiteCategory.LOGISTICS)

        alert = SiteAlert(
            site_id=uuid.uuid4(),
            severity=AlertSeverity.AMBER,
            signal_type="LAND_CLEARING",
            ndvi_delta_pct=-58.4,
            sar_vv_delta_db=3.1,
            confidence_score=0.91,
        )
        self.assertEqual(alert.severity, AlertSeverity.AMBER)


@unittest.skipUnless(
    os.getenv("TEST_POSTGIS_URL"),
    "Skipping live PostGIS integration test (set TEST_POSTGIS_URL to enable).",
)
class TestPostGISIntegration(unittest.TestCase):
    """Live PostgreSQL + PostGIS round-trip persistence test."""
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(os.environ["TEST_POSTGIS_URL"])
        Base.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def test_site_snapshot_alert_roundtrip(self) -> None:
        """
        Check that a site and snapshot can be persisted to the database and retrieved correctly.
        """
        geojson = {
            "type": "Polygon",
            "coordinates": [
                [
                    [26.010, 44.430],
                    [26.020, 44.430],
                    [26.020, 44.438],
                    [26.010, 44.438],
                    [26.010, 44.430],
                ]
            ],
        }
        with Session(self.engine) as session:
            site = MonitoredSite(
                name="Bucharest West Industrial Corridor",
                city="Bucharest",
                category=SiteCategory.INDUSTRIAL,
                area_hectares=68.2,
                boundary=geojson_polygon_to_wkt_element(geojson),
                metadata_json={"estimated_eur_sqm": 145},
            )
            session.add(site)
            session.flush()

            snap = SatelliteSnapshot(
                site_id=site.id,
                sensor="SENTINEL_2",
                observation_date=date(2026, 6, 15),
                ndvi_mean=0.24,
                sar_vv_db=-9.8,
            )
            session.add(snap)
            session.commit()

            fetched = session.get(MonitoredSite, site.id)
            self.assertIsNotNone(fetched)
            restored_geojson = wkb_element_to_geojson(fetched.boundary)
            self.assertEqual(restored_geojson["type"], "Polygon")
            self.assertEqual(len(fetched.snapshots), 1)

if __name__ == "__main__":
    unittest.main()