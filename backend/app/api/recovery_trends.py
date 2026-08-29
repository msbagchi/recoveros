from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from backend.app.db.database import (
    SessionLocal,
)

from backend.app.services.recovery_trend_service import (
    get_recovery_trends,
)


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


@router.get("/trends")
def recovery_trends(
    merchant_id: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):

    return {
        "merchant_id":
            merchant_id,

        "trends":
            get_recovery_trends(
                db=db,
                merchant_id=merchant_id,
            ),
    }