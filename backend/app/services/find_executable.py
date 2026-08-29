from sqlalchemy import text

from backend.app.db.database import SessionLocal
from backend.app.services.recovery_service import (
    analyze_transaction,
)


def find_executable_transactions():
    db = SessionLocal()

    try:
        transaction_ids = (
            db.execute(
                text(
                    """
                    SELECT transaction_id
                    FROM transactions
                    WHERE status = 'failed'
                    ORDER BY amount DESC
                    LIMIT 1000
                    """
                )
            )
            .scalars()
            .all()
        )

        matches = []

        for transaction_id in transaction_ids:
            analysis = analyze_transaction(
                db,
                transaction_id,
            )

            if not analysis:
                continue

            decision = analysis["decision"]
            transaction = analysis["transaction"]
            probability = analysis[
                "ml_probability"
            ]

            if decision.action in {
                "RETRY",
                "REMIND",
            }:
                matches.append(
                    {
                        "transaction_id":
                            transaction_id,

                        "action":
                            decision.action,

                        "amount":
                            float(
                                transaction["amount"]
                            ),

                        "failure_reason":
                            transaction[
                                "failure_reason"
                            ],

                        "probability":
                            float(
                                probability
                            ),
                    }
                )

            if len(matches) >= 5:
                break

        print()
        print(
            "=========================================="
        )
        print(
            "   RECOVEROS EXECUTABLE TRANSACTIONS"
        )
        print(
            "=========================================="
        )

        if not matches:
            print(
                "No RETRY or REMIND transactions found."
            )

        else:
            for item in matches:
                print()
                print(
                    f"Transaction: "
                    f"{item['transaction_id']}"
                )

                print(
                    f"Action:      "
                    f"{item['action']}"
                )

                print(
                    f"Amount:      "
                    f"Rs {item['amount']:,.2f}"
                )

                print(
                    f"Failure:     "
                    f"{item['failure_reason']}"
                )

                print(
                    f"ML chance:   "
                    f"{item['probability'] * 100:.1f}%"
                )

        print()
        print(
            "=========================================="
        )

    finally:
        db.close()


if __name__ == "__main__":
    find_executable_transactions()