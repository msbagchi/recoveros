from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from backend.app.db.database import (
    SessionLocal,
)
from backend.app.services.merchant_service import (
    get_merchants,
)


router = APIRouter(
    prefix="/api/merchants",
    tags=["Merchants"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("")
def list_merchants(
    db: Session = Depends(get_db),
):
    return {
        "merchants": get_merchants(db)
    }