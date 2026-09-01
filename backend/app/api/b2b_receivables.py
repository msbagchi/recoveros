from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.services.b2b_receivables_service import (
    get_b2b_receivables,
)


router = APIRouter(
    prefix="/api/b2b-receivables",
    tags=["B2B Receivables"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def b2b_receivables(
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
    return get_b2b_receivables(
        db=db,
        merchant_id=merchant_id,
        limit=limit,
    )
