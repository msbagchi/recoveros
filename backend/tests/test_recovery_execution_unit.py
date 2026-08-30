from unittest.mock import patch

from backend.app.decision.schemas import RecoveryDecision
from backend.app.services.recovery_execution_service import (
    execute_recovery_action,
)


class FakeQuery:
    def __init__(self, recovered_record=None):
        self.recovered_record = recovered_record

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.recovered_record


class FakeRecoveredRecord:
    def __init__(self):
        self.status = "recovered"


class FakeDB:
    def __init__(self, recovered_record=None):
        self.added = []
        self.commits = 0
        self.refreshes = 0
        self.recovered_record = recovered_record

    def query(self, model):
        return FakeQuery(
            recovered_record=self.recovered_record
        )

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.commits += 1

    def refresh(self, value):
        self.refreshes += 1


def analysis_for(
    action,
    *,
    is_recoverable=True,
    requires_review=False,
):
    return {
        "transaction": {
            "transaction_id": "TXN-TEST-EXEC",
            "is_recoverable": is_recoverable,
            "requires_review": requires_review,
        },
        "decision": RecoveryDecision(
            transaction_id="TXN-TEST-EXEC",
            action=action,
            confidence=0.90,
            expected_recovery=900.0,
            reason="Test decision.",
            wait_minutes=30 if action == "RETRY" else None,
            max_retries=2 if action == "RETRY" else None,
        ),
    }


@patch(
    "backend.app.services.recovery_execution_service.analyze_transaction"
)
def test_execution_returns_not_found(mock_analyze):
    mock_analyze.return_value = None
    db = FakeDB()

    result = execute_recovery_action(
        db,
        "TXN-MISSING",
    )

    assert result["success"] is False
    assert result["status"] == "not_found"
    assert db.commits == 0


@patch(
    "backend.app.services.recovery_execution_service.analyze_transaction"
)
def test_execution_blocks_already_recovered(mock_analyze):
    mock_analyze.return_value = analysis_for(
        "RETRY",
    )

    db = FakeDB(
        recovered_record=FakeRecoveredRecord()
    )

    result = execute_recovery_action(
        db,
        "TXN-TEST-EXEC",
    )

    assert result["success"] is False
    assert result["status"] == "blocked"
    assert result["guardrail"] == "already_recovered"
    assert db.commits == 0
    assert not db.added


@patch(
    "backend.app.services.recovery_execution_service.analyze_transaction"
)
def test_execution_blocks_manual_review(mock_analyze):
    mock_analyze.return_value = analysis_for(
        "ESCALATE",
        requires_review=True,
    )

    db = FakeDB()

    result = execute_recovery_action(
        db,
        "TXN-TEST-EXEC",
    )

    assert result["success"] is False
    assert result["status"] == "blocked"
    assert result["guardrail"] == "manual_review_required"
    assert db.commits == 0
    assert not db.added


@patch(
    "backend.app.services.recovery_execution_service.analyze_transaction"
)
def test_execution_blocks_non_recoverable(mock_analyze):
    mock_analyze.return_value = analysis_for(
        "ESCALATE",
        is_recoverable=False,
    )

    db = FakeDB()

    result = execute_recovery_action(
        db,
        "TXN-TEST-EXEC",
    )

    assert result["success"] is False
    assert result["guardrail"] == "not_recoverable"
    assert db.commits == 0


@patch(
    "backend.app.services.recovery_execution_service.analyze_transaction"
)
def test_execution_blocks_non_automatable_action(mock_analyze):
    mock_analyze.return_value = analysis_for(
        "CUSTOMER_ACTION",
    )

    db = FakeDB()

    result = execute_recovery_action(
        db,
        "TXN-TEST-EXEC",
    )

    assert result["success"] is False
    assert result["guardrail"] == "action_not_automatable"
    assert db.commits == 0


@patch(
    "backend.app.services.recovery_execution_service.analyze_transaction"
)
def test_retry_execution_creates_simulated_audit(mock_analyze):
    mock_analyze.return_value = analysis_for(
        "RETRY"
    )

    db = FakeDB()

    result = execute_recovery_action(
        db,
        "TXN-TEST-EXEC",
    )

    assert result["success"] is True
    assert result["status"] == "executed"
    assert result["recommended_action"] == "RETRY"
    assert result["action"] == "delayed_retry"
    assert result["recovery_id"].startswith("SIM-")

    assert db.commits == 1
    assert db.refreshes == 1
    assert len(db.added) == 1
    assert db.added[0].action == "delayed_retry"


@patch(
    "backend.app.services.recovery_execution_service.analyze_transaction"
)
def test_remind_execution_creates_simulated_audit(mock_analyze):
    mock_analyze.return_value = analysis_for(
        "REMIND"
    )

    db = FakeDB()

    result = execute_recovery_action(
        db,
        "TXN-TEST-EXEC",
    )

    assert result["success"] is True
    assert result["recommended_action"] == "REMIND"
    assert result["action"] == "customer_reminder"

    assert db.commits == 1
    assert len(db.added) == 1
    assert db.added[0].action == "customer_reminder"