from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.services.opportunity_service import (
    get_recovery_opportunities,
)


router = APIRouter(
    prefix="/api/opportunities",
    tags=["Recovery Opportunities"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("")
def opportunities(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    results = get_recovery_opportunities(
        db,
        limit=limit,
    )

    return {
        "count": len(results),
        "opportunities": results,
    }