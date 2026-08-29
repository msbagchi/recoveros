from backend.app.decision.rules import (
    CUSTOMER_ACTION_FAILURES,
    calculate_recovery_score,
    choose_action,
)

from backend.app.decision.schemas import (
    RecoveryDecision,
)


def decide_recovery(
    transaction_id: str,
    amount: float,
    previous_failures: int,
    customer_recovery_rate: float,
    payment_degradation: float,
    previous_retry_success: bool,
    failure_reason: str | None = None,
    is_recoverable: bool = True,
    requires_review: bool = False,
) -> RecoveryDecision:

    score = calculate_recovery_score(
        previous_failures=(
            previous_failures
        ),
        customer_recovery_rate=(
            customer_recovery_rate
        ),
        payment_degradation=(
            payment_degradation
        ),
        previous_retry_success=(
            previous_retry_success
        ),
    )

    action = choose_action(
        score=score,
        previous_failures=(
            previous_failures
        ),
        failure_reason=(
            failure_reason
        ),
        is_recoverable=(
            is_recoverable
        ),
        requires_review=(
            requires_review
        ),
    )

    # =========================================
    # DECISION EXPLANATION
    # =========================================

    if requires_review:

        wait_minutes = None
        max_retries = None

        reason = (
            "This transaction has been flagged "
            "for manual review. RecoverOS has "
            "blocked automatic recovery and "
            "escalated it to an operator."
        )

    elif not is_recoverable:

        wait_minutes = None
        max_retries = None

        reason = (
            "This transaction is not currently "
            "classified as recoverable. "
            "Automatic recovery has therefore "
            "been blocked."
        )

    elif (
        failure_reason
        in CUSTOMER_ACTION_FAILURES
    ):

        wait_minutes = None
        max_retries = None

        reason = (
            f"The payment failed because of "
            f"'{failure_reason}'. The customer "
            "must resolve the payment issue "
            "before another automatic attempt."
        )

    elif previous_failures >= 3:

        wait_minutes = None
        max_retries = None

        reason = (
            "The customer has reached the "
            "maximum safe failure threshold. "
            "RecoverOS recommends manual "
            "review instead of another "
            "automatic recovery attempt."
        )

    elif action == "RETRY":

        wait_minutes = 30
        max_retries = 2

        reason = (
            "The transaction is eligible for "
            "recovery and customer history "
            "supports a controlled retry."
        )

    elif action == "REMIND":

        wait_minutes = None
        max_retries = None

        reason = (
            "Recovery probability is moderate. "
            "A customer reminder is safer than "
            "immediately attempting another "
            "payment."
        )

    else:

        wait_minutes = None
        max_retries = None

        reason = (
            "The transaction does not currently "
            "meet the safety criteria for an "
            "automatic recovery attempt."
        )

    expected_recovery = round(
        amount * score,
        2,
    )

    return RecoveryDecision(
        transaction_id=(
            transaction_id
        ),
        action=action,
        confidence=round(
            score,
            2,
        ),
        expected_recovery=(
            expected_recovery
        ),
        reason=reason,
        wait_minutes=(
            wait_minutes
        ),
        max_retries=(
            max_retries
        ),
    )