from dataclasses import dataclass
from typing import Optional


@dataclass
class RecoveryDecision:
    transaction_id: str
    action: str
    confidence: float
    expected_recovery: float
    reason: str
    wait_minutes: Optional[int] = None
    max_retries: Optional[int] = None