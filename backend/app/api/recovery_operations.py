from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from backend.app.db.database import (
    SessionLocal,
)
from backend.app.services.recovery_operations_service import (
    get_recovery_operations,
)


router = APIRouter(
    prefix="/api/recovery-operations",
    tags=["Recovery Operations"],
)


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


@router.get("")
def recovery_operations(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    merchant_id: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):

    return get_recovery_operations(
        db=db,
        limit=limit,
        merchant_id=merchant_id,
    )