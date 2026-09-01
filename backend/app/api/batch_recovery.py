from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.services.batch_recovery_service import (
    get_batch_history,
    run_batch_recovery,
)


router = APIRouter(
    prefix="/api/recovery",
    tags=["Batch Recovery"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


class BatchRequest(BaseModel):
    merchant_id: str | None = None


@router.post("/batch")
def batch_recovery(
    body: BatchRequest = BatchRequest(),
    db: Session = Depends(get_db),
):
    return run_batch_recovery(
        db=db,
        merchant_id=body.merchant_id,
    )


@router.get("/batch/history")
def batch_history(
    merchant_id: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    runs = get_batch_history(
        db=db,
        merchant_id=merchant_id,
    )

    return {
        "count": len(runs),
        "runs": runs,
    }
