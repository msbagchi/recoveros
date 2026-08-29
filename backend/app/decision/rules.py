TEMPORARY_FAILURES = {
    "network_error",
    "timeout",
    "gateway_unavailable",
    "processing_error",
}

CUSTOMER_ACTION_FAILURES = {
    "expired_card",
    "invalid_card",
    "authentication_required",
    "insufficient_funds",
}


def calculate_recovery_score(
    previous_failures: int,
    customer_recovery_rate: float,
    payment_degradation: float,
    previous_retry_success: bool,
) -> float:

    score = 0.0

    score += (
        customer_recovery_rate
        * 0.40
    )

    if previous_failures == 0:
        score += 0.20

    elif previous_failures == 1:
        score += 0.15

    elif previous_failures == 2:
        score += 0.05

    if payment_degradation < 0.30:
        score += 0.20

    elif payment_degradation < 0.60:
        score += 0.10

    if previous_retry_success:
        score += 0.20

    return min(
        score,
        1.0,
    )


def choose_action(
    score: float,
    previous_failures: int,
    failure_reason: str | None = None,
    is_recoverable: bool = True,
    requires_review: bool = False,
) -> str:

    # =========================================
    # HARD GUARDRAILS
    # =========================================

    if requires_review:
        return "ESCALATE"

    if not is_recoverable:
        return "ESCALATE"

    # =========================================
    # CUSTOMER INTERVENTION
    # =========================================

    if (
        failure_reason
        in CUSTOMER_ACTION_FAILURES
    ):
        return "CUSTOMER_ACTION"

    # =========================================
    # FAILURE LIMIT
    # =========================================

    if previous_failures >= 3:
        return "ESCALATE"

    # =========================================
    # AUTOMATED DECISIONS
    # =========================================

    if score >= 0.70:
        return "RETRY"

    if score >= 0.45:
        return "REMIND"

    return "ESCALATE"