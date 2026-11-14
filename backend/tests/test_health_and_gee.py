import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app


class TestHealthAndGEE(unittest.TestCase):
    @patch("app.main.init_gee")
    @patch("app.main.check_gee_connection")
    def test_health_endpoint_unit_mocked(self, mock_check_gee, mock_init_gee):
        """
        Unit test for the health endpoint. Checks that the endpoint returns the correct status without making any actual API calls.
        """
        mock_check_gee.return_value = {"connected": True, "test_computation": 2}

        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["gee"]["connected"])
        mock_init_gee.assert_called_once()

    @patch("app.main.init_gee")
    @patch("app.main.check_gee_connection")
    def test_health_endpoint_degraded_when_gee_fails(self, mock_check_gee):
        """
        Unit test for the health endpoint. Checks that the endpoint returns 'degraded' when GEE fails to connect.
        """
        mock_check_gee.return_value = {"connected": False, "error": "Auth failed"}

        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "degraded")
        self.assertFalse(data["gee"]["connected"])

    def test_health_endpoint_live_gee_integration(self):
        """
        IntegrationTest for the health endpoint. Initializes GEE and checks that the endpoint returns the correct status.
        """
        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok", f"Conexiunea live GEE a eșuat: {data}")
        self.assertEqual(data["gee"]["test_computation"], 2)


if __name__ == "__main__":
    unittest.main()