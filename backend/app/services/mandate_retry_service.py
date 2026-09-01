from sqlalchemy import text
from sqlalchemy.orm import Session


def _retry_sequence(
    attempt_number: int,
    amount: float,
) -> dict:

    if attempt_number >= 3:
        return {
            "retry_action": "escalate_to_bank",
            "retry_window_hours": None,
            "rationale": (
                "Three attempts exhausted — "
                "escalate to bank for mandate "
                "investigation."
            ),
        }

    if attempt_number == 2:
        return {
            "retry_action": "retry_with_reminder",
            "retry_window_hours": 48,
            "rationale": (
                "Second attempt — retry in 48h "
                "with customer balance reminder."
            ),
        }

    # attempt_number == 1
    if amount > 15000:
        return {
            "retry_action": "scheduled_retry",
            "retry_window_hours": 24,
            "rationale": (
                "High-value mandate — "
                "retry next business day "
                "to maximise success chance."
            ),
        }

    return {
        "retry_action": "immediate_retry",
        "retry_window_hours": 2,
        "rationale": (
            "Low-value UPI mandate — "
            "retry in 2h during morning "
            "active window (9 AM–11 AM)."
        ),
    }


def get_mandate_retry(
    db: Session,
    merchant_id: str | None = None,
    limit: int = 20,
) -> dict:

    merchant_filter = ""
    params: dict = {"limit": limit}

    if merchant_id:
        merchant_filter = (
            "AND t.merchant_id = :merchant_id"
        )
        params["merchant_id"] = merchant_id

    rows = db.execute(
        text(
            f"""
            SELECT
                t.transaction_id,
                t.merchant_id,
                t.customer_id,
                t.amount,
                t.currency,
                t.failure_reason,
                t.attempt_number,
                t.is_recoverable,
                t.timestamp,
                c.segment AS customer_segment,
                c.preferred_payment_method
            FROM transactions t
            JOIN customers c
                ON c.customer_id = t.customer_id
            WHERE t.payment_method = 'upi'
              AND t.status = 'failed'
              AND t.is_recoverable = true
              {merchant_filter}
            ORDER BY t.amount DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()

    mandates = []

    for row in rows:
        amount = float(row["amount"] or 0)
        attempt = int(
            row["attempt_number"] or 1
        )
        seq = _retry_sequence(attempt, amount)

        mandates.append(
            {
                "transaction_id":
                    row["transaction_id"],
                "merchant_id":
                    row["merchant_id"],
                "customer_id":
                    row["customer_id"],
                "amount": round(amount, 2),
                "currency":
                    row["currency"] or "INR",
                "failure_reason":
                    row["failure_reason"],
                "attempt_number": attempt,
                "failed_at":
                    row["timestamp"].isoformat()
                    if row["timestamp"]
                    else None,
                "customer_segment":
                    row["customer_segment"],
                "preferred_payment_method":
                    row[
                        "preferred_payment_method"
                    ],
                "retry_action":
                    seq["retry_action"],
                "retry_window_hours":
                    seq["retry_window_hours"],
                "rationale":
                    seq["rationale"],
            }
        )

    # =========================================
    # SUMMARY
    # =========================================

    total_value = sum(
        m["amount"] for m in mandates
    )

    action_counts: dict[str, int] = {}

    for m in mandates:
        action = m["retry_action"]
        action_counts[action] = (
            action_counts.get(action, 0) + 1
        )

    return {
        "summary": {
            "total_failed_mandates":
                len(mandates),
            "total_mandate_value": round(
                total_value, 2
            ),
            "immediate_retry":
                action_counts.get(
                    "immediate_retry", 0
                ),
            "scheduled_retry":
                action_counts.get(
                    "scheduled_retry", 0
                ),
            "retry_with_reminder":
                action_counts.get(
                    "retry_with_reminder", 0
                ),
            "escalate_to_bank":
                action_counts.get(
                    "escalate_to_bank", 0
                ),
        },
        "count": len(mandates),
        "mandates": mandates,
    }
