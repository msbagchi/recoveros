from sqlalchemy import text
from sqlalchemy.orm import Session


ABANDONMENT_FAILURE_REASONS = {
    "gateway_timeout",
    "temporary_network",
    "bank_declined",
    "processing_error",
    "network_error",
    "timeout",
}


def _recommended_action(amount: float) -> str:
    if amount >= 10000:
        return "send_payment_link"
    if amount >= 1000:
        return "send_recovery_nudge"
    return "auto_retry"


def _urgency(amount: float) -> str:
    if amount >= 10000:
        return "HIGH"
    if amount >= 1000:
        return "MEDIUM"
    return "LOW"


def get_checkout_abandonment(
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
                c.lifetime_value
            FROM transactions t
            JOIN customers c
                ON c.customer_id = t.customer_id
            WHERE t.transaction_type = 'one_time'
              AND t.status = 'failed'
              AND t.failure_reason IN (
                  'gateway_timeout',
                  'temporary_network',
                  'bank_declined',
                  'processing_error',
                  'network_error',
                  'timeout'
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM recovery_actions ra
                  WHERE ra.transaction_id =
                        t.transaction_id
              )
              {merchant_filter}
            ORDER BY t.timestamp DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()

    candidates = []

    for row in rows:
        amount = float(row["amount"] or 0)
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
                "abandoned_at":
                    row["timestamp"].isoformat()
                    if row["timestamp"]
                    else None,
                "customer_segment":
                    row["customer_segment"],
                "lifetime_value": round(
                    float(
                        row["lifetime_value"] or 0
                    ),
                    2,
                ),
                "recommended_action":
                    _recommended_action(amount),
                "urgency":
                    _urgency(amount),
            }
        )

    # =========================================
    # SUMMARY
    # =========================================

    total_value = sum(
        c["amount"] for c in candidates
    )

    action_counts: dict[str, int] = {}

    for c in candidates:
        action = c["recommended_action"]
        action_counts[action] = (
            action_counts.get(action, 0) + 1
        )

    return {
        "summary": {
            "total_abandoned": len(candidates),
            "total_value_at_risk": round(
                total_value, 2
            ),
            "send_payment_link":
                action_counts.get(
                    "send_payment_link", 0
                ),
            "send_recovery_nudge":
                action_counts.get(
                    "send_recovery_nudge", 0
                ),
            "auto_retry":
                action_counts.get(
                    "auto_retry", 0
                ),
        },
        "count": len(candidates),
        "candidates": candidates,
    }
