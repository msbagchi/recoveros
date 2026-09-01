from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.services.subscription_recovery_service import (
    get_subscription_recovery,
)


router = APIRouter(
    prefix="/api/subscription-recovery",
    tags=["Subscription Recovery"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def subscription_recovery(
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
    return get_subscription_recovery(
        db=db,
        merchant_id=merchant_id,
        limit=limit,
    )
