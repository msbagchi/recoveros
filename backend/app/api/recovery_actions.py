from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from backend.app.db.database import (
    SessionLocal,
)
from backend.app.services.recovery_execution_service import (
    execute_recovery_action,
)


router = APIRouter(
    prefix="/api/recovery-actions",
    tags=["Recovery Actions"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post(
    "/{transaction_id}/execute"
)
def execute_recovery(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    result = execute_recovery_action(
        db,
        transaction_id,
    )

    if result["status"] == "not_found":
        raise HTTPException(
            status_code=404,
            detail=result["message"],
        )

    return result