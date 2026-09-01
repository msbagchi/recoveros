from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.services.escalation_service import (
    get_escalation_summary,
    get_escalations,
    resolve_escalation,
)


router = APIRouter(
    prefix="/api/escalations",
    tags=["Escalations"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


class ResolveRequest(BaseModel):
    status: str
    notes: str | None = None


@router.get("")
def list_escalations(
    merchant_id: str | None = Query(
        default=None,
    ),
    status: str | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
):
    escalations = get_escalations(
        db=db,
        merchant_id=merchant_id,
        status=status,
        limit=limit,
    )

    return {
        "count": len(escalations),
        "escalations": escalations,
    }


@router.get("/summary")
def escalation_summary(
    merchant_id: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    return get_escalation_summary(
        db=db,
        merchant_id=merchant_id,
    )


@router.patch(
    "/{escalation_id}/resolve"
)
def resolve(
    escalation_id: str,
    body: ResolveRequest,
    db: Session = Depends(get_db),
):
    result = resolve_escalation(
        db=db,
        escalation_id=escalation_id,
        status=body.status,
        notes=body.notes,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Escalation not found or "
                "invalid status value. "
                "Allowed: APPROVED, REJECTED"
            ),
        )

    return result
