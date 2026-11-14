from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.integrations.gee.client import init_gee, check_gee_connection, GEEClientError

logger = logging.getLogger("uvicorn")
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_gee()
        logger.info("Google Earth Engine initialized successfully.")
    except GEEClientError as e:
        logger.error(f"Error: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check():
    """Checks the health of the server and the connection to Google Earth Engine."""
    gee_status = check_gee_connection()
    return {
        "status": "ok" if gee_status["connected"] else "degraded",
        "environment": settings.ENVIRONMENT,
        "gee": gee_status,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)