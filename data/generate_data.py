import random
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 42

random.seed(SEED)
np.random.seed(SEED)

NUM_MERCHANTS = 5
NUM_CUSTOMERS = 5000
NUM_TRANSACTIONS = 20000

OUTPUT_DIR = Path(__file__).resolve().parent / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------

PAYMENT_METHODS = [
    "upi",
    "card",
    "netbanking",
    "wallet",
]

PAYMENT_METHOD_WEIGHTS = [
    0.50,
    0.30,
    0.12,
    0.08,
]

TRANSACTION_TYPES = [
    "one_time",
    "subscription",
]

FAILURE_REASONS = [
    "temporary_network",
    "bank_declined",
    "insufficient_balance",
    "expired_card",
    "authentication_failed",
    "gateway_timeout",
]

CUSTOMER_SEGMENTS = [
    "new",
    "returning",
    "loyal",
    "high_value",
]


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def random_timestamp(days=90):
    start = datetime.now() - timedelta(days=days)
    seconds = random.randint(0, days * 24 * 60 * 60)

    return start + timedelta(seconds=seconds)


def random_amount():
    """
    Generate realistic Indian transaction amounts.
    Most transactions are small, while a smaller number
    are high-value.
    """

    amount = np.random.lognormal(
        mean=np.log(1200),
        sigma=0.9,
    )

    amount = max(99, min(amount, 75000))

    return round(amount, 2)


def choose_customer_segment():
    return random.choices(
        CUSTOMER_SEGMENTS,
        weights=[0.25, 0.40, 0.25, 0.10],
        k=1,
    )[0]


# ---------------------------------------------------------
# Generate merchants
# ---------------------------------------------------------

def generate_merchants():

    merchants = []

    merchant_names = [
        "Acme Fashion",
        "DailyKart",
        "Nova Electronics",
        "FreshBasket",
        "UrbanFit",
    ]

    for i in range(NUM_MERCHANTS):

        merchant_id = f"MER-{1001 + i}"

        merchants.append(
            {
                "merchant_id": merchant_id,
                "merchant_name": merchant_names[i],
                "industry": random.choice(
                    [
                        "fashion",
                        "electronics",
                        "grocery",
                        "fitness",
                        "lifestyle",
                    ]
                ),
                "monthly_volume": random.randint(
                    50000,
                    500000,
                ),
            }
        )

    return pd.DataFrame(merchants)


# ---------------------------------------------------------
# Generate customers
# ---------------------------------------------------------

def generate_customers(merchants):

    customers = []

    for i in range(NUM_CUSTOMERS):

        merchant = random.choice(
            merchants["merchant_id"].tolist()
        )

        segment = choose_customer_segment()

        if segment == "new":
            successful_payments = random.randint(0, 2)

        elif segment == "returning":
            successful_payments = random.randint(3, 10)

        elif segment == "loyal":
            successful_payments = random.randint(10, 30)

        else:
            successful_payments = random.randint(15, 50)

        customers.append(
            {
                "customer_id": f"CUST-{100000 + i}",
                "merchant_id": merchant,
                "segment": segment,
                "successful_payments": successful_payments,
                "lifetime_value": round(
                    random.uniform(500, 50000),
                    2,
                ),
                "previous_recoveries": random.randint(
                    0,
                    5,
                ),
                "preferred_payment_method": random.choices(
                    PAYMENT_METHODS,
                    weights=PAYMENT_METHOD_WEIGHTS,
                    k=1,
                )[0],
            }
        )

    return pd.DataFrame(customers)


# ---------------------------------------------------------
# Determine transaction outcome
# ---------------------------------------------------------

def generate_transaction_status(
    customer,
    payment_method,
    transaction_type,
):
    """
    Generate realistic payment outcomes.

    We intentionally create patterns that our future
    ML model can learn.
    """

    base_failure_probability = 0.10

    # Loyal customers tend to have slightly better
    # successful payment behaviour.
    if customer["segment"] == "loyal":
        base_failure_probability -= 0.03

    if customer["segment"] == "high_value":
        base_failure_probability -= 0.02

    # Different payment methods have slightly different
    # synthetic failure rates.
    if payment_method == "upi":
        base_failure_probability += 0.01

    elif payment_method == "netbanking":
        base_failure_probability += 0.03

    elif payment_method == "card":
        base_failure_probability += 0.02

    # Subscription payments get a small additional risk.
    if transaction_type == "subscription":
        base_failure_probability += 0.03

    base_failure_probability = max(
        0.02,
        min(base_failure_probability, 0.35),
    )

    if random.random() > base_failure_probability:

        return "success", None

    failure_reason = random.choices(
        FAILURE_REASONS,
        weights=[
            0.25,
            0.20,
            0.18,
            0.08,
            0.14,
            0.15,
        ],
        k=1,
    )[0]

    return "failed", failure_reason


# ---------------------------------------------------------
# Recovery classification
# ---------------------------------------------------------

def classify_recovery(
    status,
    failure_reason,
    customer,
    amount,
    attempt_number,
):
    """
    Create the ground truth label for our synthetic world.

    This is NOT the ML model.

    This represents the underlying simulated reality
    that our future model will attempt to discover.
    """

    if status == "success":
        return False, False, "not_required"

    # Permanent problems are generally not recoverable.
    if failure_reason in [
        "expired_card",
        "authentication_failed",
    ]:
        return False, False, "permanent_failure"

    # Too many attempts should eventually stop.
    if attempt_number >= 3:
        return False, True, "retry_limit_reached"

    # Very high-value transactions should receive
    # additional review rather than blind automation.
    if amount > 25000:
        return True, True, "high_value_review"

    # Strong customer history makes recovery more likely.
    if customer["successful_payments"] >= 5:
        return True, False, "historical_recovery_signal"

    # Temporary technical failures are good candidates.
    if failure_reason in [
        "temporary_network",
        "gateway_timeout",
    ]:
        return True, False, "temporary_failure"

    # Bank declines / insufficient balance can still
    # sometimes recover.
    if failure_reason in [
        "bank_declined",
        "insufficient_balance",
    ]:
        return random.random() < 0.45, False, "conditional_recovery"

    return False, False, "not_recoverable"


# ---------------------------------------------------------
# Generate transactions
# ---------------------------------------------------------

def generate_transactions(customers):

    transactions = []

    for i in range(NUM_TRANSACTIONS):

        customer = customers.iloc[
            random.randrange(len(customers))
        ]

        transaction_type = random.choices(
            TRANSACTION_TYPES,
            weights=[0.75, 0.25],
            k=1,
        )[0]

        payment_method = random.choices(
            PAYMENT_METHODS,
            weights=PAYMENT_METHOD_WEIGHTS,
            k=1,
        )[0]

        amount = random_amount()

        timestamp = random_timestamp()

        status, failure_reason = generate_transaction_status(
            customer,
            payment_method,
            transaction_type,
        )

        # Failed transactions get between 1 and 3 attempts.
        if status == "failed":
            attempt_number = random.randint(1, 3)
        else:
            attempt_number = 1

        is_recoverable, requires_review, recovery_reason = (
            classify_recovery(
                status,
                failure_reason,
                customer,
                amount,
                attempt_number,
            )
        )

        transactions.append(
            {
                "transaction_id": f"TXN-{1000000 + i}",
                "merchant_id": customer["merchant_id"],
                "customer_id": customer["customer_id"],
                "timestamp": timestamp.isoformat(),
                "amount": amount,
                "currency": "INR",
                "payment_method": payment_method,
                "transaction_type": transaction_type,
                "status": status,
                "failure_reason": failure_reason,
                "attempt_number": attempt_number,
                "is_recoverable": is_recoverable,
                "requires_review": requires_review,
                "recovery_reason": recovery_reason,
            }
        )

    return pd.DataFrame(transactions)


# ---------------------------------------------------------
# Generate recovery actions
# ---------------------------------------------------------

def generate_recovery_actions(transactions):

    actions = []

    for _, transaction in transactions.iterrows():

        if not transaction["is_recoverable"]:
            continue

        if transaction["requires_review"]:
            action = "human_review"

        elif transaction["failure_reason"] in [
            "temporary_network",
            "gateway_timeout",
        ]:
            action = "delayed_retry"

        elif transaction["failure_reason"] in [
            "bank_declined",
            "insufficient_balance",
        ]:
            action = "customer_reminder"

        else:
            action = "retry_payment"

        # Simulate recovery outcome.
        if action == "delayed_retry":
            recovery_probability = 0.68

        elif action == "retry_payment":
            recovery_probability = 0.55

        elif action == "customer_reminder":
            recovery_probability = 0.45

        else:
            recovery_probability = 0.60

        recovered = (
            random.random() < recovery_probability
        )

        actions.append(
            {
                "recovery_id": f"REC-{len(actions) + 1:06d}",
                "transaction_id": transaction["transaction_id"],
                "action": action,
                "status": "recovered" if recovered else "failed",
                "amount_recovered": (
                    transaction["amount"]
                    if recovered
                    else 0
                ),
                "executed_at": (
                    datetime.now().isoformat()
                ),
            }
        )

    return pd.DataFrame(actions)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("Generating RecoverOS synthetic payment world...")

    merchants = generate_merchants()

    customers = generate_customers(
        merchants
    )

    transactions = generate_transactions(
        customers
    )

    recovery_actions = generate_recovery_actions(
        transactions
    )

    merchants.to_csv(
        OUTPUT_DIR / "merchants.csv",
        index=False,
    )

    customers.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False,
    )

    transactions.to_csv(
        OUTPUT_DIR / "transactions.csv",
        index=False,
    )

    recovery_actions.to_csv(
        OUTPUT_DIR / "recovery_actions.csv",
        index=False,
    )

    print()
    print("Generation complete.")
    print()
    print(f"Merchants: {len(merchants):,}")
    print(f"Customers: {len(customers):,}")
    print(f"Transactions: {len(transactions):,}")
    print(f"Recovery actions: {len(recovery_actions):,}")
    print()

    failed = (
        transactions["status"] == "failed"
    ).sum()

    recoverable = (
        transactions["is_recoverable"]
    ).sum()

    recovered_amount = recovery_actions[
        "amount_recovered"
    ].sum()

    revenue_at_risk = transactions.loc[
        transactions["status"] == "failed",
        "amount",
    ].sum()

    print(
        f"Failed transactions: {failed:,}"
    )

    print(
        f"Potentially recoverable: {recoverable:,}"
    )

    print(
        f"Revenue at risk: ₹{revenue_at_risk:,.2f}"
    )

    print(
        f"Simulated recovered revenue: "
        f"₹{recovered_amount:,.2f}"
    )


if __name__ == "__main__":
    main()