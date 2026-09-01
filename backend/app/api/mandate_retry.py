from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.services.mandate_retry_service import (
    get_mandate_retry,
)


router = APIRouter(
    prefix="/api/mandate-retry",
    tags=["Mandate Retry"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def mandate_retry(
    merchant_id: str | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    return get_mandate_retry(
        db=db,
        merchant_id=merchant_id,
        limit=limit,
    )
