import ee
from app.core.config import get_settings


class GEEClientError(Exception):
    """Thrwable exception for errors related to the Google Earth Engine client."""

def init_gee() -> None:
    """Initializes the connection to Google Earth Engine only once at server startup."""
    settings = get_settings()
    try:
        if settings.GEE_SERVICE_ACCOUNT_KEY_PATH:
            credentials = ee.ServiceAccountCredentials(
                email=None,
                key_file=settings.GEE_SERVICE_ACCOUNT_KEY_PATH,
            )
            ee.Initialize(credentials=credentials, project=settings.GEE_PROJECT_ID)
        else:
            ee.Initialize(project=settings.GEE_PROJECT_ID)
    except Exception as exc:
        raise GEEClientError(f"Nu s-a putut inițializa Google Earth Engine: {exc}") from exc


def check_gee_connection() -> dict:
    """Executes a simple calculation on Google Earth Engine servers to confirm the API is working."""
    try:
        return {"connected": True, "test_computation": result}
    except Exception as exc:
        return {"connected": False, "error": str(exc)}