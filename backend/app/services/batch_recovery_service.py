from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.batch_run import BatchRun
from backend.app.models.recovery import RecoveryAction
from backend.app.models.transaction import Transaction
from backend.app.services.recovery_execution_service import (
    execute_recovery_action,
)


def run_batch_recovery(
    db: Session,
    merchant_id: str | None = None,
) -> dict:

    run_id = (
        f"BATCH-{uuid4().hex[:10].upper()}"
    )

    started_at = datetime.now()

    # =========================================
    # QUERY ELIGIBLE TRANSACTIONS
    # failed + recoverable + not yet actioned
    # =========================================

    actioned_ids = {
        row.transaction_id
        for row in db.query(
            RecoveryAction.transaction_id
        ).all()
    }

    query = db.query(Transaction).filter(
        Transaction.status == "failed",
        Transaction.is_recoverable == True,
    )

    if merchant_id:
        query = query.filter(
            Transaction.merchant_id
            == merchant_id
        )

    candidates = query.all()

    # =========================================
    # PROCESS EACH CANDIDATE
    # =========================================

    attempted = 0
    executed = 0
    blocked = 0
    skipped = 0
    potential_amount = 0.0

    for txn in candidates:

        if txn.transaction_id in actioned_ids:
            skipped += 1
            continue

        attempted += 1

        result = execute_recovery_action(
            db,
            txn.transaction_id,
        )

        if result.get("status") == "executed":
            executed += 1
            potential_amount += float(
                txn.amount or 0
            )

        elif result.get("status") == "blocked":
            blocked += 1

        else:
            skipped += 1

    # =========================================
    # SAVE BATCH RUN RECORD
    # =========================================

    completed_at = datetime.now()

    batch_run = BatchRun(
        run_id=run_id,
        merchant_id=merchant_id,
        started_at=started_at,
        completed_at=completed_at,
        attempted=attempted,
        executed=executed,
        blocked=blocked,
        skipped=skipped,
        potential_amount=round(
            potential_amount, 2
        ),
    )

    db.add(batch_run)
    db.commit()
    db.refresh(batch_run)

    return {
        "run_id": run_id,
        "merchant_id": merchant_id,
        "attempted": attempted,
        "executed": executed,
        "blocked": blocked,
        "skipped": skipped,
        "potential_amount": round(
            potential_amount, 2
        ),
        "started_at":
            started_at.isoformat(),
        "completed_at":
            completed_at.isoformat(),
    }


def get_batch_history(
    db: Session,
    merchant_id: str | None = None,
    limit: int = 10,
) -> list[dict]:

    query = db.query(BatchRun)

    if merchant_id:
        query = query.filter(
            BatchRun.merchant_id
            == merchant_id
        )

    runs = (
        query.order_by(
            BatchRun.started_at.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "run_id": r.run_id,
            "merchant_id": r.merchant_id,
            "attempted": r.attempted,
            "executed": r.executed,
            "blocked": r.blocked,
            "skipped": r.skipped,
            "potential_amount":
                r.potential_amount,
            "started_at":
                r.started_at.isoformat(),
            "completed_at": (
                r.completed_at.isoformat()
                if r.completed_at
                else None
            ),
        }
        for r in runs
    ]
