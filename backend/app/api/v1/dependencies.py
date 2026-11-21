"""FastAPI dependency providers injecting services into v1 route handlers."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.intelligence_service import IntelligenceService
from app.services.site_service import SiteService


def get_site_service(db: Session = Depends(get_db)) -> SiteService:
    """Provide a request-scoped SiteService instance."""
    return SiteService(db=db)


def get_intelligence_service(db: Session = Depends(get_db)) -> IntelligenceService:
    """Provide a request-scoped IntelligenceService instance."""
    return IntelligenceService(db=db)