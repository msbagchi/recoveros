from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.services.recovery_service import (
    analyze_transaction,
)


def calculate_priority(
    ml_probability: float,
    expected_recovery: float,
    previous_failures: int,
) -> str:
    recovery_score = min(
        expected_recovery / 10000,
        1.0,
    )

    failure_penalty = min(
        previous_failures * 0.10,
        0.30,
    )

    opportunity_score = (
        ml_probability * 0.60
        + recovery_score * 0.40
        - failure_penalty
    )

    if opportunity_score >= 0.65:
        return "HIGH"

    if opportunity_score >= 0.40:
        return "MEDIUM"

    return "LOW"


def get_recovery_opportunities(
    db: Session,
    limit: int = 10,
    merchant_id: str | None = None,
):
    if merchant_id:
        query = text(
            """
            SELECT
                transaction_id
            FROM transactions
            WHERE status = 'failed'
              AND merchant_id = :merchant_id
            ORDER BY amount DESC
            LIMIT 100
            """
        )

        transactions = (
            db.execute(
                query,
                {
                    "merchant_id": merchant_id,
                },
            )
            .scalars()
            .all()
        )

    else:
        query = text(
            """
            SELECT
                transaction_id
            FROM transactions
            WHERE status = 'failed'
            ORDER BY amount DESC
            LIMIT 100
            """
        )

        transactions = (
            db.execute(query)
            .scalars()
            .all()
        )

    opportunities = []

    for transaction_id in transactions:
        analysis = analyze_transaction(
            db,
            transaction_id,
        )

        if not analysis:
            continue

        transaction = analysis[
            "transaction"
        ]

        decision = analysis[
            "decision"
        ]

        ml_probability = float(
            analysis["ml_probability"]
        )

        amount = float(
            transaction["amount"]
        )

        expected_recovery = (
            amount * ml_probability
        )

        previous_failures = int(
            transaction.get(
                "previous_failures",
                0,
            )
            or 0
        )

        priority = calculate_priority(
            ml_probability=ml_probability,
            expected_recovery=expected_recovery,
            previous_failures=previous_failures,
        )

        opportunities.append(
            {
                "transaction_id":
                    transaction_id,

                "merchant_id":
                    transaction.get(
                        "merchant_id"
                    ),

                "customer_id":
                    transaction[
                        "customer_id"
                    ],

                "amount":
                    amount,

                "failure_reason":
                    transaction[
                        "failure_reason"
                    ],

                "ml_probability":
                    round(
                        ml_probability,
                        4,
                    ),

                "expected_recovery":
                    round(
                        expected_recovery,
                        2,
                    ),

                "priority":
                    priority,

                "recommended_action":
                    decision.action,

                "confidence":
                    decision.confidence,

                "reason":
                    decision.reason,
            }
        )

    opportunities.sort(
        key=lambda item:
            item[
                "expected_recovery"
            ],
        reverse=True,
    )

    return opportunities[:limit]