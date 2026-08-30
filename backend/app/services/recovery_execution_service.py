from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.recovery import RecoveryAction
from backend.app.services.recovery_service import analyze_transaction


ALLOWED_AUTOMATED_ACTIONS = {
    "RETRY",
    "REMIND",
}


def execute_recovery_action(
    db: Session,
    transaction_id: str,
):
    """
    Execute a recovery action in simulation mode.

    No real payment or customer communication
    occurs. RecoverOS stores an audit record
    representing the simulated action.
    """

    analysis = analyze_transaction(
        db,
        transaction_id,
    )

    if not analysis:
        return {
            "success": False,
            "status": "not_found",
            "message": "Transaction not found.",
        }

    decision = analysis["decision"]
    transaction = analysis["transaction"]

    recommended_action = decision.action

    is_recoverable = bool(
        transaction.get(
            "is_recoverable",
            False,
        )
    )

    requires_review = bool(
        transaction.get(
            "requires_review",
            False,
        )
    )

    # =========================================
    # GUARDRAIL 1
    # ALREADY RECOVERED
    # =========================================

    successful_recovery = (
        db.query(RecoveryAction)
        .filter(
            RecoveryAction.transaction_id
            == transaction_id,
            RecoveryAction.status
            == "recovered",
        )
        .first()
    )

    if successful_recovery:
        return {
            "success": False,
            "status": "blocked",
            "transaction_id": transaction_id,
            "recommended_action": recommended_action,
            "guardrail": "already_recovered",
            "message": (
                "Automatic execution blocked "
                "because this transaction has "
                "already been successfully recovered."
            ),
            "reason": (
                "A successful recovery record already "
                "exists for this transaction."
            ),
        }

    # =========================================
    # GUARDRAIL 2
    # MANUAL REVIEW
    # =========================================

    if requires_review:
        return {
            "success": False,
            "status": "blocked",
            "transaction_id": transaction_id,
            "recommended_action": recommended_action,
            "guardrail": "manual_review_required",
            "message": (
                "Automatic execution blocked "
                "because this transaction "
                "requires manual review."
            ),
            "reason": decision.reason,
        }

    # =========================================
    # GUARDRAIL 3
    # RECOVERABILITY
    # =========================================

    if not is_recoverable:
        return {
            "success": False,
            "status": "blocked",
            "transaction_id": transaction_id,
            "recommended_action": recommended_action,
            "guardrail": "not_recoverable",
            "message": (
                "Automatic execution blocked "
                "because this transaction is "
                "not classified as recoverable."
            ),
            "reason": decision.reason,
        }

    # =========================================
    # GUARDRAIL 4
    # ACTION ALLOWLIST
    # =========================================

    if recommended_action not in ALLOWED_AUTOMATED_ACTIONS:
        return {
            "success": False,
            "status": "blocked",
            "transaction_id": transaction_id,
            "recommended_action": recommended_action,
            "guardrail": "action_not_automatable",
            "message": (
                "Automatic execution blocked "
                "by RecoverOS action guardrails."
            ),
            "reason": decision.reason,
        }

    # =========================================
    # CREATE SIMULATION AUDIT RECORD
    # =========================================

    recovery_id = (
        f"SIM-{uuid4().hex[:10].upper()}"
    )

    if recommended_action == "RETRY":
        stored_action = "delayed_retry"
    else:
        stored_action = "customer_reminder"

    recovery_action = RecoveryAction(
        recovery_id=recovery_id,
        transaction_id=transaction_id,
        action=stored_action,
        status="executed",
        amount_recovered=0.0,
        executed_at=datetime.now(),
    )

    db.add(recovery_action)
    db.commit()
    db.refresh(recovery_action)

    return {
        "success": True,
        "status": "executed",
        "recovery_id": recovery_action.recovery_id,
        "transaction_id": transaction_id,
        "action": recovery_action.action,
        "recommended_action": recommended_action,
        "executed_at": recovery_action.executed_at.isoformat(),
        "message": (
            "Recovery action executed in "
            "RecoverOS simulation mode."
        ),
    }