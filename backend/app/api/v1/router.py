from fastapi import APIRouter
from app.api.v1.endpoints import intelligence, sites

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(sites.router)
api_router.include_router(intelligence.router)