from sqlalchemy import text
from sqlalchemy.orm import Session


B2B_HIGH_VALUE_THRESHOLD = 50000.0
B2B_ACCOUNT_MANAGER_THRESHOLD = 200000.0


def _collection_strategy(
    amount: float,
    segment: str,
) -> dict:

    if amount >= B2B_ACCOUNT_MANAGER_THRESHOLD:
        return {
            "strategy": "account_manager_escalation",
            "installment_amount": None,
            "rationale": (
                "High-value receivable — "
                "assign dedicated account manager "
                "for personal collection."
            ),
        }

    if amount >= B2B_HIGH_VALUE_THRESHOLD:
        installment = round(amount / 3, 2)
        return {
            "strategy": "payment_plan_offer",
            "installment_amount": installment,
            "rationale": (
                f"Large receivable — offer "
                f"3-instalment plan of "
                f"₹{installment:,.0f} each."
            ),
        }

    return {
        "strategy": "priority_retry",
        "installment_amount": None,
        "rationale": (
            "High-value B2B customer with "
            "manageable amount — priority "
            "automated retry."
        ),
    }


def get_b2b_receivables(
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
                c.lifetime_value,
                (
                    SELECT COALESCE(SUM(t2.amount), 0)
                    FROM transactions t2
                    WHERE t2.customer_id =
                          t.customer_id
                      AND t2.status = 'failed'
                ) AS total_outstanding
            FROM transactions t
            JOIN customers c
                ON c.customer_id = t.customer_id
            WHERE t.status = 'failed'
              AND (
                  c.segment = 'high_value'
                  OR t.amount >= :threshold
              )
              {merchant_filter}
            ORDER BY t.amount DESC
            LIMIT :limit
            """
        ),
        {
            **params,
            "threshold": B2B_HIGH_VALUE_THRESHOLD,
        },
    ).mappings().all()

    receivables = []

    for row in rows:
        amount = float(row["amount"] or 0)
        segment = row["customer_segment"] or ""
        col = _collection_strategy(
            amount, segment
        )

        receivables.append(
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
                "customer_segment": segment,
                "lifetime_value": round(
                    float(
                        row["lifetime_value"] or 0
                    ),
                    2,
                ),
                "total_outstanding": round(
                    float(
                        row["total_outstanding"]
                        or 0
                    ),
                    2,
                ),
                "collection_strategy":
                    col["strategy"],
                "installment_amount":
                    col["installment_amount"],
                "rationale":
                    col["rationale"],
            }
        )

    # =========================================
    # SUMMARY
    # =========================================

    total_value = sum(
        r["amount"] for r in receivables
    )

    strategy_counts: dict[str, int] = {}

    for r in receivables:
        s = r["collection_strategy"]
        strategy_counts[s] = (
            strategy_counts.get(s, 0) + 1
        )

    return {
        "summary": {
            "total_receivables":
                len(receivables),
            "total_receivables_value": round(
                total_value, 2
            ),
            "account_manager_escalation":
                strategy_counts.get(
                    "account_manager_escalation",
                    0,
                ),
            "payment_plan_offer":
                strategy_counts.get(
                    "payment_plan_offer", 0
                ),
            "priority_retry":
                strategy_counts.get(
                    "priority_retry", 0
                ),
        },
        "count": len(receivables),
        "receivables": receivables,
    }
