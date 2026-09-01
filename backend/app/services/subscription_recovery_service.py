from sqlalchemy import text
from sqlalchemy.orm import Session


def _retry_recommendation(
    subscription_failures: int,
) -> dict:

    if subscription_failures == 1:
        return {
            "action": "scheduled_retry",
            "retry_in_hours": 24,
            "rationale": (
                "First failure — retry in 24h "
                "during customer's active window."
            ),
        }

    if subscription_failures == 2:
        return {
            "action": "customer_notification",
            "retry_in_hours": 48,
            "rationale": (
                "Second consecutive failure — "
                "notify customer to update "
                "payment method."
            ),
        }

    return {
        "action": "subscription_pause",
        "retry_in_hours": None,
        "rationale": (
            "Three or more failures — "
            "pause subscription and escalate "
            "to account review."
        ),
    }


def get_subscription_recovery(
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
                t.payment_method,
                t.failure_reason,
                t.attempt_number,
                t.timestamp,
                c.segment AS customer_segment,
                c.successful_payments,
                c.previous_recoveries,
                c.lifetime_value,
                (
                    SELECT COUNT(*)
                    FROM transactions t2
                    WHERE t2.customer_id =
                          t.customer_id
                      AND t2.transaction_type =
                          'subscription'
                      AND t2.status = 'failed'
                ) AS subscription_failures
            FROM transactions t
            JOIN customers c
                ON c.customer_id = t.customer_id
            WHERE t.transaction_type =
                  'subscription'
              AND t.status = 'failed'
              {merchant_filter}
            ORDER BY subscription_failures DESC,
                     t.amount DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()

    candidates = []

    for row in rows:
        amount = float(row["amount"] or 0)
        failures = int(
            row["subscription_failures"] or 1
        )
        rec = _retry_recommendation(failures)

        candidates.append(
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
                "payment_method":
                    row["payment_method"],
                "failure_reason":
                    row["failure_reason"],
                "attempt_number":
                    row["attempt_number"],
                "failed_at":
                    row["timestamp"].isoformat()
                    if row["timestamp"]
                    else None,
                "customer_segment":
                    row["customer_segment"],
                "successful_payments": int(
                    row["successful_payments"]
                    or 0
                ),
                "previous_recoveries": int(
                    row["previous_recoveries"]
                    or 0
                ),
                "subscription_failures":
                    failures,
                "recommended_action":
                    rec["action"],
                "retry_in_hours":
                    rec["retry_in_hours"],
                "rationale":
                    rec["rationale"],
            }
        )

    # =========================================
    # SUMMARY
    # =========================================

    total_value = sum(
        c["amount"] for c in candidates
    )

    recoverable = [
        c
        for c in candidates
        if c["recommended_action"]
        != "subscription_pause"
    ]

    action_counts: dict[str, int] = {}

    for c in candidates:
        action = c["recommended_action"]
        action_counts[action] = (
            action_counts.get(action, 0) + 1
        )

    avg_failures = (
        round(
            sum(
                c["subscription_failures"]
                for c in candidates
            )
            / len(candidates),
            1,
        )
        if candidates
        else 0.0
    )

    return {
        "summary": {
            "total_failed_subscriptions":
                len(candidates),
            "total_value_at_risk": round(
                total_value, 2
            ),
            "recoverable_subscriptions":
                len(recoverable),
            "avg_failures_per_customer":
                avg_failures,
            "scheduled_retry":
                action_counts.get(
                    "scheduled_retry", 0
                ),
            "customer_notification":
                action_counts.get(
                    "customer_notification", 0
                ),
            "subscription_pause":
                action_counts.get(
                    "subscription_pause", 0
                ),
        },
        "count": len(candidates),
        "candidates": candidates,
    }
