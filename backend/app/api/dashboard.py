from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.decision.rules import STOPPING_RULES


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/summary")
def dashboard_summary(
    merchant_id: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    params = {}

    transaction_filter = ""

    recovery_filter = ""

    if merchant_id:
        params["merchant_id"] = merchant_id

        transaction_filter = """
            WHERE merchant_id = :merchant_id
        """

        recovery_filter = """
            AND t.merchant_id = :merchant_id
        """

    # -----------------------------------------
    # TOTAL TRANSACTIONS
    # -----------------------------------------

    total_transactions = db.execute(
        text(
            f"""
            SELECT COUNT(*)
            FROM transactions
            {transaction_filter}
            """
        ),
        params,
    ).scalar() or 0

    # -----------------------------------------
    # FAILED TRANSACTIONS
    # -----------------------------------------

    if merchant_id:
        failed_query = text(
            """
            SELECT COUNT(*)
            FROM transactions
            WHERE status = 'failed'
              AND merchant_id = :merchant_id
            """
        )

    else:
        failed_query = text(
            """
            SELECT COUNT(*)
            FROM transactions
            WHERE status = 'failed'
            """
        )

    failed_transactions = (
        db.execute(
            failed_query,
            params,
        ).scalar()
        or 0
    )

    # -----------------------------------------
    # RECOVERED ACTIONS
    # -----------------------------------------

    recovered_transactions = (
        db.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM recovery_actions ra
                JOIN transactions t
                    ON ra.transaction_id =
                       t.transaction_id
                WHERE ra.status = 'recovered'
                {recovery_filter}
                """
            ),
            params,
        ).scalar()
        or 0
    )

    # -----------------------------------------
    # FAILED RECOVERY ACTIONS
    # -----------------------------------------

    failed_recovery_actions = (
        db.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM recovery_actions ra
                JOIN transactions t
                    ON ra.transaction_id =
                       t.transaction_id
                WHERE ra.status = 'failed'
                {recovery_filter}
                """
            ),
            params,
        ).scalar()
        or 0
    )

    # -----------------------------------------
    # RECOVERED AMOUNT
    # -----------------------------------------

    recovered_amount = (
        db.execute(
            text(
                f"""
                SELECT COALESCE(
                    SUM(
                        ra.amount_recovered
                    ),
                    0
                )
                FROM recovery_actions ra
                JOIN transactions t
                    ON ra.transaction_id =
                       t.transaction_id
                WHERE ra.status = 'recovered'
                {recovery_filter}
                """
            ),
            params,
        ).scalar()
        or 0
    )

    # -----------------------------------------
    # FAILED TRANSACTION AMOUNT
    # -----------------------------------------

    if merchant_id:
        failed_amount_query = text(
            """
            SELECT COALESCE(
                SUM(amount),
                0
            )
            FROM transactions
            WHERE status = 'failed'
              AND merchant_id = :merchant_id
            """
        )

    else:
        failed_amount_query = text(
            """
            SELECT COALESCE(
                SUM(amount),
                0
            )
            FROM transactions
            WHERE status = 'failed'
            """
        )

    failed_amount = (
        db.execute(
            failed_amount_query,
            params,
        ).scalar()
        or 0
    )

    # -----------------------------------------
    # RECOVERY RATE
    # -----------------------------------------

    total_recovery_actions = (
        recovered_transactions
        + failed_recovery_actions
    )

    recovery_rate = 0.0

    if total_recovery_actions:
        recovery_rate = (
            recovered_transactions
            / total_recovery_actions
        )

    return {
        "merchant_id":
            merchant_id,
        "total_transactions":
            int(total_transactions),
        "failed_transactions":
            int(failed_transactions),
        "recovered_transactions":
            int(recovered_transactions),
        "recovery_rate":
            round(
                recovery_rate * 100,
                2,
            ),
        "recovered_amount":
            round(
                float(
                    recovered_amount
                ),
                2,
            ),
        "failed_amount":
            round(
                float(
                    failed_amount
                ),
                2,
            ),
    }


@router.get("/stopping-rules")
def stopping_rules():
    return STOPPING_RULES