from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.escalation import Escalation


ALLOWED_RESOLVE_STATUSES = {
    "APPROVED",
    "REJECTED",
}


def auto_create_escalation(
    db: Session,
    transaction_id: str,
    merchant_id: str | None,
    reason: str,
) -> Escalation | None:

    existing = (
        db.query(Escalation)
        .filter(
            Escalation.transaction_id
            == transaction_id,
            Escalation.status == "PENDING",
        )
        .first()
    )

    if existing:
        return existing

    escalation = Escalation(
        escalation_id=(
            f"ESC-{uuid4().hex[:10].upper()}"
        ),
        transaction_id=transaction_id,
        merchant_id=merchant_id,
        reason=reason,
        status="PENDING",
        created_at=datetime.now(),
    )

    db.add(escalation)
    db.commit()
    db.refresh(escalation)

    return escalation


def get_escalations(
    db: Session,
    merchant_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict]:

    query = db.query(Escalation)

    if merchant_id:
        query = query.filter(
            Escalation.merchant_id
            == merchant_id
        )

    if status:
        query = query.filter(
            Escalation.status == status
        )

    escalations = (
        query.order_by(
            Escalation.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "escalation_id":
                e.escalation_id,
            "transaction_id":
                e.transaction_id,
            "merchant_id":
                e.merchant_id,
            "reason":
                e.reason,
            "status":
                e.status,
            "created_at":
                e.created_at.isoformat(),
            "resolved_at": (
                e.resolved_at.isoformat()
                if e.resolved_at
                else None
            ),
            "notes":
                e.notes,
        }
        for e in escalations
    ]


def get_escalation_summary(
    db: Session,
    merchant_id: str | None = None,
) -> dict:

    query = db.query(Escalation)

    if merchant_id:
        query = query.filter(
            Escalation.merchant_id
            == merchant_id
        )

    all_escalations = query.all()

    pending = sum(
        1
        for e in all_escalations
        if e.status == "PENDING"
    )

    approved = sum(
        1
        for e in all_escalations
        if e.status == "APPROVED"
    )

    rejected = sum(
        1
        for e in all_escalations
        if e.status == "REJECTED"
    )

    return {
        "total": len(all_escalations),
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
    }


def resolve_escalation(
    db: Session,
    escalation_id: str,
    status: str,
    notes: str | None = None,
) -> dict | None:

    if status not in ALLOWED_RESOLVE_STATUSES:
        return None

    escalation = (
        db.query(Escalation)
        .filter(
            Escalation.escalation_id
            == escalation_id
        )
        .first()
    )

    if not escalation:
        return None

    escalation.status = status
    escalation.resolved_at = datetime.now()

    if notes:
        escalation.notes = notes

    db.commit()
    db.refresh(escalation)

    return {
        "escalation_id":
            escalation.escalation_id,
        "transaction_id":
            escalation.transaction_id,
        "status":
            escalation.status,
        "resolved_at":
            escalation.resolved_at.isoformat(),
        "notes":
            escalation.notes,
    }
