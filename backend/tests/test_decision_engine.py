import pytest

from backend.app.decision.engine import decide_recovery
from backend.app.decision.schemas import RecoveryDecision


def make_decision(**overrides):
    values = {
        "transaction_id": "TXN-TEST-001",
        "amount": 1000.0,
        "previous_failures": 0,
        "customer_recovery_rate": 0.90,
        "payment_degradation": 0.10,
        "previous_retry_success": True,
        "failure_reason": "network_error",
        "is_recoverable": True,
        "requires_review": False,
    }
    values.update(overrides)
    return decide_recovery(**values)


def test_decide_recovery_returns_schema():
    decision = make_decision()
    assert isinstance(decision, RecoveryDecision)
    assert decision.transaction_id == "TXN-TEST-001"


def test_retry_decision_metadata():
    decision = make_decision()

    assert decision.action == "RETRY"
    assert decision.confidence == pytest.approx(0.96)
    assert decision.expected_recovery == pytest.approx(960.0)
    assert decision.wait_minutes == 30
    assert decision.max_retries == 2
    assert "controlled retry" in decision.reason.lower()


def test_remind_decision_metadata():
    decision = make_decision(
        customer_recovery_rate=0.625,
        payment_degradation=0.70,
        previous_retry_success=False,
        previous_failures=0,
    )

    assert decision.action == "REMIND"
    assert decision.confidence == pytest.approx(0.45)
    assert decision.wait_minutes is None
    assert decision.max_retries is None


def test_customer_action_decision():
    decision = make_decision(
        failure_reason="expired_card",
    )

    assert decision.action == "CUSTOMER_ACTION"
    assert decision.wait_minutes is None
    assert decision.max_retries is None
    assert "customer" in decision.reason.lower()


def test_manual_review_decision():
    decision = make_decision(
        requires_review=True,
    )

    assert decision.action == "ESCALATE"
    assert decision.wait_minutes is None
    assert decision.max_retries is None
    assert "manual review" in decision.reason.lower()


def test_non_recoverable_decision():
    decision = make_decision(
        is_recoverable=False,
    )

    assert decision.action == "ESCALATE"
    assert "not currently" in decision.reason.lower()
    assert decision.wait_minutes is None
    assert decision.max_retries is None


def test_failure_limit_decision():
    decision = make_decision(
        previous_failures=3,
        customer_recovery_rate=1.0,
        payment_degradation=0.0,
        previous_retry_success=True,
    )

    assert decision.action == "ESCALATE"
    assert "maximum safe failure threshold" in decision.reason.lower()


def test_expected_recovery_uses_score_even_when_escalated():
    decision = make_decision(
        amount=2500.0,
        requires_review=True,
    )

    assert decision.action == "ESCALATE"
    assert decision.expected_recovery == pytest.approx(
        2500.0 * decision.confidence,
        abs=25.0,
    )
