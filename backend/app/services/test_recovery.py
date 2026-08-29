from sqlalchemy import text

from backend.app.db.database import SessionLocal
from backend.app.services.recovery_service import analyze_transaction


db = SessionLocal()

try:
    # Find an actual failed transaction from PostgreSQL.
    query = text(
        """
        SELECT transaction_id
        FROM transactions
        WHERE status = 'failed'
        ORDER BY amount DESC
        LIMIT 1
        """
    )

    result = db.execute(query).scalar_one_or_none()

    if not result:
        print("No failed transactions were found.")
    else:
        transaction_id = result

        print()
        print("======================================")
        print("       RECOVEROS REAL ANALYSIS")
        print("======================================")
        print(f"Selected transaction: {transaction_id}")
        print()

        analysis = analyze_transaction(
            db,
            transaction_id,
        )

        if analysis is None:
            print("Transaction could not be analyzed.")
        else:
            transaction = analysis["transaction"]
            decision = analysis["decision"]

            print(
                f"Customer:            "
                f"{transaction['customer_id']}"
            )

            print(
                f"Amount:              "
                f"Rs {transaction['amount']}"
            )

            print(
                f"Status:              "
                f"{transaction['status']}"
            )

            print(
                f"Failure reason:      "
                f"{transaction['failure_reason']}"
            )

            print(
                f"Previous failures:   "
                f"{transaction['previous_failures']}"
            )

            print()
            print("--------- DECISION ---------")

            print(
                f"Action:              "
                f"{decision.action}"
            )

            print(
                f"Confidence:          "
                f"{decision.confidence * 100:.0f}%"
            )

            print(
                f"Expected recovery:   "
                f"Rs {decision.expected_recovery}"
            )

            if decision.wait_minutes:
                print(
                    f"Wait:                "
                    f"{decision.wait_minutes} minutes"
                )

            if decision.max_retries:
                print(
                    f"Max retries:         "
                    f"{decision.max_retries}"
                )

            print(
                f"Reason:              "
                f"{decision.reason}"
            )

            print("======================================")
            print()

finally:
    db.close()