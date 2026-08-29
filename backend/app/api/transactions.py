from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from backend.app.db.database import (
    SessionLocal,
)
from backend.app.models.recovery import (
    RecoveryAction,
)
from backend.app.services.recovery_service import (
    analyze_transaction,
)


router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/{transaction_id}/analysis")
def transaction_analysis(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    # =========================================
    # ANALYZE TRANSACTION
    # =========================================

    analysis = analyze_transaction(
        db,
        transaction_id,
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    transaction = analysis[
        "transaction"
    ]

    decision = analysis[
        "decision"
    ]

    ml_probability = analysis[
        "ml_probability"
    ]

    signals = analysis.get(
        "signals",
        {},
    )

    explanation = analysis.get(
        "explanation",
        {},
    )

    # =========================================
    # RECOVERY HISTORY / AUDIT TRAIL
    # =========================================

    recovery_history = (
        db.query(
            RecoveryAction
        )
        .filter(
            RecoveryAction.transaction_id
            == transaction_id
        )
        .order_by(
            RecoveryAction.executed_at.desc()
        )
        .all()
    )

    history = []

    for action in recovery_history:

        history.append(
            {
                "recovery_id":
                    action.recovery_id,

                "action":
                    action.action,

                "status":
                    action.status,

                "amount_recovered":
                    float(
                        action.amount_recovered
                        or 0
                    ),

                "executed_at":
                    (
                        action.executed_at.isoformat()
                        if action.executed_at
                        else None
                    ),
            }
        )

    # =========================================
    # FINAL RESPONSE
    # =========================================

    return {
        "transaction":
            transaction,

        "ml_probability":
            ml_probability,

        "decision":
            decision,

        "signals":
            signals,

        "explanation":
            explanation,

        "recovery_history":
            history,
    }