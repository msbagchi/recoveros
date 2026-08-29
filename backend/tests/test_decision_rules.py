import pytest

from backend.app.decision.rules import (
    calculate_recovery_score,
    choose_action,
)


def test_recovery_score_high_case():
    score = calculate_recovery_score(
        previous_failures=0,
        customer_recovery_rate=0.90,
        payment_degradation=0.10,
        previous_retry_success=True,
    )
    assert score == pytest.approx(0.96)


def test_recovery_score_is_capped_at_one():
    score = calculate_recovery_score(
        previous_failures=0,
        customer_recovery_rate=2.0,
        payment_degradation=0.10,
        previous_retry_success=True,
    )
    assert score == 1.0


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.70, "RETRY"),
        (0.95, "RETRY"),
        (0.45, "REMIND"),
        (0.69, "REMIND"),
        (0.44, "ESCALATE"),
        (0.10, "ESCALATE"),
    ],
)
def test_action_thresholds(score, expected):
    assert choose_action(
        score=score,
        previous_failures=0,
    ) == expected


@pytest.mark.parametrize(
    "failure_reason",
    [
        "expired_card",
        "invalid_card",
        "authentication_required",
        "insufficient_funds",
    ],
)
def test_customer_action_failures(failure_reason):
    assert choose_action(
        score=0.99,
        previous_failures=0,
        failure_reason=failure_reason,
    ) == "CUSTOMER_ACTION"


def test_manual_review_overrides_high_score():
    assert choose_action(
        score=0.99,
        previous_failures=0,
        requires_review=True,
    ) == "ESCALATE"


def test_non_recoverable_overrides_high_score():
    assert choose_action(
        score=0.99,
        previous_failures=0,
        is_recoverable=False,
    ) == "ESCALATE"


def test_failure_limit_overrides_retry():
    assert choose_action(
        score=0.99,
        previous_failures=3,
    ) == "ESCALATE"


def test_manual_review_has_priority_over_customer_action():
    assert choose_action(
        score=0.99,
        previous_failures=0,
        failure_reason="expired_card",
        requires_review=True,
    ) == "ESCALATE"


def test_non_recoverable_has_priority_over_customer_action():
    assert choose_action(
        score=0.99,
        previous_failures=0,
        failure_reason="expired_card",
        is_recoverable=False,
    ) == "ESCALATE"
