from backend.app.decision.engine import decide_recovery


decision = decide_recovery(
    transaction_id="TXN_DEMO_001",
    amount=2499,
    previous_failures=1,
    customer_recovery_rate=0.78,
    payment_degradation=0.25,
    previous_retry_success=True,
)


print("\n========== RECOVEROS DECISION ==========")

print(f"Transaction:       {decision.transaction_id}")
print(f"Action:            {decision.action}")
print(f"Confidence:        {decision.confidence * 100:.0f}%")
print(f"Expected recovery: Rs {decision.expected_recovery}")

if decision.wait_minutes:
    print(f"Wait:              {decision.wait_minutes} minutes")

if decision.max_retries:
    print(f"Max retries:       {decision.max_retries}")

print(f"Reason:            {decision.reason}")

print("=========================================\n")