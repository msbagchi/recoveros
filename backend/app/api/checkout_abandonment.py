from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.services.checkout_abandonment_service import (
    get_checkout_abandonment,
)


router = APIRouter(
    prefix="/api/checkout-abandonment",
    tags=["Checkout Abandonment"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def checkout_abandonment(
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
    return get_checkout_abandonment(
        db=db,
        merchant_id=merchant_id,
        limit=limit,
    )
