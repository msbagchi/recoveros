from sqlalchemy.orm import Session

from backend.app.decision.engine import (
    decide_recovery,
)
from backend.app.services.explainability_service import (
    build_prediction_explanation,
)
from backend.app.services.recovery_features import (
    get_transaction_features,
)
from ml.predict import (
    predict_recovery_probability,
)


def analyze_transaction(
    db: Session,
    transaction_id: str,
):
    features = get_transaction_features(
        db,
        transaction_id,
    )

    if not features:
        return None

    # =========================================
    # CUSTOMER HISTORY
    # =========================================

    successful_payments = int(
        features.get(
            "successful_payments",
            0,
        )
        or 0
    )

    previous_recoveries = int(
        features.get(
            "previous_recoveries",
            0,
        )
        or 0
    )

    previous_failures = int(
        features.get(
            "previous_failures",
            0,
        )
        or 0
    )

    is_recoverable = bool(
        features.get(
            "is_recoverable",
            False,
        )
    )

    requires_review = bool(
        features.get(
            "requires_review",
            False,
        )
    )

    # =========================================
    # HISTORICAL RECOVERY RATE
    # =========================================

    historical_outcomes = (
        successful_payments
        + previous_recoveries
    )

    if historical_outcomes > 0:

        recovery_rate = (
            previous_recoveries
            / historical_outcomes
        )

    else:

        recovery_rate = 0.0

    # =========================================
    # PAYMENT DEGRADATION
    # =========================================

    payment_degradation = min(
        previous_failures / 5,
        1.0,
    )

    previous_retry_success = (
        previous_recoveries > 0
    )

    # =========================================
    # ML PREDICTION
    # =========================================

    ml_probability = (
        predict_recovery_probability(
            features
        )
    )

    # =========================================
    # SIGNALS
    # =========================================

    signals = {
        "customer_recovery_rate":
            round(
                recovery_rate,
                4,
            ),

        "previous_recoveries":
            previous_recoveries,

        "previous_failures":
            previous_failures,

        "previous_retry_success":
            previous_retry_success,

        "payment_degradation":
            round(
                payment_degradation,
                4,
            ),

        "is_recoverable":
            is_recoverable,

        "requires_review":
            requires_review,
    }

    # =========================================
    # BUSINESS DECISION
    # =========================================

    decision = decide_recovery(
        transaction_id=features[
            "transaction_id"
        ],

        amount=float(
            features["amount"]
        ),

        previous_failures=(
            previous_failures
        ),

        customer_recovery_rate=(
            recovery_rate
        ),

        payment_degradation=(
            payment_degradation
        ),

        previous_retry_success=(
            previous_retry_success
        ),

        failure_reason=features.get(
            "failure_reason"
        ),

        is_recoverable=(
            is_recoverable
        ),

        requires_review=(
            requires_review
        ),
    )

    # =========================================
    # EXPLAINABILITY
    # =========================================

    explanation = (
        build_prediction_explanation(
            features=features,
            ml_probability=(
                ml_probability
            ),
            signals=signals,
        )
    )

    # =========================================
    # FINAL RESPONSE
    # =========================================

    return {
        "transaction":
            features,

        "decision":
            decision,

        "ml_probability":
            ml_probability,

        "signals":
            signals,

        "explanation":
            explanation,
    }