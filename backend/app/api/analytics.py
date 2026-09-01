from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy import text
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


@router.get("/impact")
def recovery_impact(
    merchant_id: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    params = {}

    recovery_filter = ""
    escalation_filter = ""
    promise_filter = ""
    batch_filter = ""

    if merchant_id:
        params["merchant_id"] = merchant_id

        recovery_filter = """
            AND t.merchant_id = :merchant_id
        """

        escalation_filter = """
            WHERE merchant_id = :merchant_id
        """

        promise_filter = """
            WHERE merchant_id = :merchant_id
        """

        batch_filter = """
            WHERE merchant_id = :merchant_id
        """

    # -----------------------------------------
    # TOTAL RECOVERY ACTIONS EXECUTED
    # -----------------------------------------

    total_executed = (
        db.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM recovery_actions ra
                JOIN transactions t
                    ON ra.transaction_id =
                       t.transaction_id
                WHERE ra.status = 'executed'
                {recovery_filter}
                """
            ),
            params,
        ).scalar()
        or 0
    )

    # -----------------------------------------
    # SUCCESSFULLY RECOVERED
    # -----------------------------------------

    total_recovered = (
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

    total_recovery_actions = (
        total_executed + total_recovered
    )

    recovery_rate_pct = 0.0

    if total_recovery_actions > 0:
        recovery_rate_pct = round(
            total_recovered
            / total_recovery_actions
            * 100,
            2,
        )

    # -----------------------------------------
    # BATCH RUNS
    # -----------------------------------------

    batch_runs_total = (
        db.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM batch_runs
                {batch_filter}
                """
            ),
            params,
        ).scalar()
        or 0
    )

    batch_executed_total = (
        db.execute(
            text(
                f"""
                SELECT COALESCE(SUM(executed), 0)
                FROM batch_runs
                {batch_filter}
                """
            ),
            params,
        ).scalar()
        or 0
    )

    batch_potential_total = (
        db.execute(
            text(
                f"""
                SELECT COALESCE(
                    SUM(potential_amount), 0
                )
                FROM batch_runs
                {batch_filter}
                """
            ),
            params,
        ).scalar()
        or 0
    )

    # -----------------------------------------
    # ESCALATIONS PENDING
    # -----------------------------------------

    escalations_pending = (
        db.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM escalations
                {escalation_filter}
                {"AND" if merchant_id else "WHERE"}
                status = 'PENDING'
                """
            ),
            params,
        ).scalar()
        or 0
    )

    # -----------------------------------------
    # PROMISES KEPT RATE
    # -----------------------------------------

    total_promises = (
        db.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM promise_to_pay
                {promise_filter}
                """
            ),
            params,
        ).scalar()
        or 0
    )

    kept_promises = (
        db.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM promise_to_pay
                {promise_filter}
                {"AND" if merchant_id else "WHERE"}
                status = 'KEPT'
                """
            ),
            params,
        ).scalar()
        or 0
    )

    promises_kept_rate_pct = 0.0

    if total_promises > 0:
        promises_kept_rate_pct = round(
            kept_promises
            / total_promises
            * 100,
            2,
        )

    return {
        "total_recovery_actions":
            int(total_recovery_actions),
        "total_executed":
            int(total_executed),
        "total_recovered":
            int(total_recovered),
        "recovery_rate_pct":
            recovery_rate_pct,
        "batch_runs_total":
            int(batch_runs_total),
        "batch_executed_total":
            int(batch_executed_total),
        "batch_potential_amount":
            round(
                float(batch_potential_total),
                2,
            ),
        "escalations_pending":
            int(escalations_pending),
        "total_promises":
            int(total_promises),
        "kept_promises":
            int(kept_promises),
        "promises_kept_rate_pct":
            promises_kept_rate_pct,
    }