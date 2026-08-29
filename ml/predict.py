import os

import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "recovery_model.joblib",
)


model = joblib.load(MODEL_PATH)


def predict_recovery_probability(
    transaction: dict,
) -> float:

    row = {
        "amount": float(
            transaction["amount"]
        ),
        "currency": transaction["currency"],
        "payment_method": transaction[
            "payment_method"
        ],
        "transaction_type": transaction[
            "transaction_type"
        ],
        "failure_reason": transaction[
            "failure_reason"
        ],
        "attempt_number": int(
            transaction["attempt_number"]
        ),
        "is_recoverable": transaction[
            "is_recoverable"
        ],
        "requires_review": transaction[
            "requires_review"
        ],
        "customer_segment": transaction[
            "customer_segment"
        ],
        "successful_payments": int(
            transaction["successful_payments"]
        ),
        "lifetime_value": float(
            transaction["lifetime_value"]
        ),
        "previous_recoveries": int(
            transaction["previous_recoveries"]
        ),
        "preferred_payment_method": transaction[
            "preferred_payment_method"
        ],
    }

    df = pd.DataFrame([row])

    probability = model.predict_proba(
        df
    )[0][1]

    return float(probability)