from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from backend.app.db.database import (
    SessionLocal,
)
from backend.app.services.analytics_service import (
    get_analytics_overview,
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


@router.get("/overview")
def analytics_overview(
    merchant_id: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    return get_analytics_overview(
        db=db,
        merchant_id=merchant_id,
    )