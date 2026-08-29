from backend.app.db.database import SessionLocal
from backend.app.services.recovery_features import (
    get_transaction_features,
)

from ml.predict import (
    predict_recovery_probability,
)


db = SessionLocal()

try:

    from sqlalchemy import text

    transaction_id = db.execute(
        text(
            """
            SELECT transaction_id
            FROM transactions
            WHERE status = 'failed'
            ORDER BY amount DESC
            LIMIT 1
            """
        )
    ).scalar_one()

    transaction = get_transaction_features(
        db,
        transaction_id,
    )

    probability = predict_recovery_probability(
        transaction
    )

    print()
    print("======================================")
    print("       RECOVEROS ML PREDICTION")
    print("======================================")

    print(
        f"Transaction:        {transaction_id}"
    )

    print(
        f"Amount:             Rs "
        f"{transaction['amount']}"
    )

    print(
        f"Failure reason:     "
        f"{transaction['failure_reason']}"
    )

    print()

    print(
        f"Recovery probability: "
        f"{probability * 100:.2f}%"
    )

    print("======================================")
    print()

finally:
    db.close()