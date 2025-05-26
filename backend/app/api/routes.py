from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import HealthResponse

router = APIRouter()

# ==================== HEALTH CHECK ====================


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return HealthResponse(status="healthy", timestamp=datetime.now(UTC).isoformat(), database="connected")
    except Exception as e:
        return HealthResponse(status="unhealthy", timestamp=datetime.now(UTC).isoformat(), database=f"error: {str(e)}")
