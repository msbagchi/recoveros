from sqlalchemy import text
from sqlalchemy.orm import Session


def get_transaction_features(
    db: Session,
    transaction_id: str,
):
    query = text(
        """
        SELECT
            t.transaction_id,
            t.customer_id,
            t.amount,
            t.currency,
            t.payment_method,
            t.transaction_type,
            t.status,
            t.failure_reason,
            t.attempt_number,
            t.is_recoverable,
            t.requires_review,

            c.segment AS customer_segment,
            c.successful_payments,
            c.previous_recoveries,
            c.lifetime_value,
            c.preferred_payment_method,

            (
                SELECT COUNT(*)
                FROM transactions previous_t
                WHERE previous_t.customer_id = t.customer_id
                  AND previous_t.status = 'failed'
                  AND previous_t.timestamp < t.timestamp
            ) AS previous_failures,

            (
                SELECT COUNT(*)
                FROM recovery_actions r
                JOIN transactions rt
                    ON rt.transaction_id = r.transaction_id
                WHERE rt.customer_id = t.customer_id
                  AND r.status = 'recovered'
                  AND r.executed_at < t.timestamp
            ) AS successful_recoveries

        FROM transactions t

        JOIN customers c
            ON c.customer_id = t.customer_id

        WHERE t.transaction_id = :transaction_id
        """
    )

    result = db.execute(
        query,
        {"transaction_id": transaction_id},
    ).mappings().first()

    if not result:
        return None

    return dict(result)