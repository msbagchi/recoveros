"""
Seed synthetic data for promise_to_pay, batch_runs, and escalations tables.
Run with: python -m backend.app.db.seed_new_tables
"""
import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy import text

from backend.app.db.database import engine

MERCHANT_IDS = [f"MER-{1001 + i}" for i in range(5)]
CUSTOMER_IDS = [f"CUST-{100000 + i}" for i in range(50)]
TRANSACTION_IDS = [f"TXN-{1000000 + i}" for i in range(200)]

NOW = datetime.now()


def rand_date(days_back=90):
    return NOW - timedelta(days=random.randint(0, days_back))


def rand_future(days_ahead=30):
    return NOW + timedelta(days=random.randint(1, days_ahead))


# ---------------------------------------------------------------------------
# promises (promise_to_pay)
# ---------------------------------------------------------------------------

PROMISE_STATUSES = ["PENDING", "KEPT", "BROKEN", "PENDING", "KEPT"]  # weighted


def build_promises(n=120):
    seen_txns = set()
    rows = []
    for i in range(n):
        txn = random.choice(TRANSACTION_IDS)
        # avoid exact duplicates on (promise_id) — unique col
        promise_id = f"PTP-{uuid.uuid4().hex[:10].upper()}"
        status = random.choice(PROMISE_STATUSES)
        created = rand_date(60)
        promise_date = created + timedelta(days=random.randint(3, 21))
        rows.append(
            {
                "promise_id": promise_id,
                "merchant_id": random.choice(MERCHANT_IDS),
                "customer_id": random.choice(CUSTOMER_IDS),
                "transaction_id": txn,
                "promised_amount": round(random.uniform(50, 5000), 2),
                "promise_date": promise_date,
                "status": status,
                "created_at": created,
                "updated_at": created + timedelta(hours=random.randint(1, 48)),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# batch_runs
# ---------------------------------------------------------------------------

def build_batch_runs(n=60):
    rows = []
    for i in range(n):
        started = rand_date(90)
        attempted = random.randint(10, 500)
        executed = random.randint(0, attempted)
        blocked = random.randint(0, attempted - executed)
        skipped = attempted - executed - blocked
        completed = started + timedelta(minutes=random.randint(2, 60))
        rows.append(
            {
                "run_id": f"BATCH-{uuid.uuid4().hex[:10].upper()}",
                "merchant_id": random.choice(MERCHANT_IDS + [None, None]),
                "started_at": started,
                "completed_at": completed,
                "attempted": attempted,
                "executed": executed,
                "blocked": blocked,
                "skipped": max(0, skipped),
                "potential_amount": round(random.uniform(500, 50000), 2),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# escalations
# ---------------------------------------------------------------------------

ESCALATION_REASONS = [
    "High-value transaction exceeds auto-recovery threshold",
    "Multiple failed recovery attempts — manual review required",
    "Customer dispute flagged",
    "Chargeback risk detected",
    "Mandate expired — re-authorization needed",
    "Suspicious activity pattern",
    "Repeated NSF failures",
    "B2B invoice overdue >60 days",
]

ESCALATION_STATUSES = ["PENDING", "PENDING", "RESOLVED", "IN_REVIEW"]


def build_escalations(n=80):
    rows = []
    for i in range(n):
        status = random.choice(ESCALATION_STATUSES)
        created = rand_date(60)
        resolved_at = (
            created + timedelta(days=random.randint(1, 14))
            if status == "RESOLVED"
            else None
        )
        rows.append(
            {
                "escalation_id": f"ESC-{uuid.uuid4().hex[:10].upper()}",
                "transaction_id": random.choice(TRANSACTION_IDS),
                "merchant_id": random.choice(MERCHANT_IDS),
                "reason": random.choice(ESCALATION_REASONS),
                "status": status,
                "created_at": created,
                "resolved_at": resolved_at,
                "notes": (
                    random.choice(
                        [
                            "Contacted customer via phone.",
                            "Waiting on customer response.",
                            "Escalated to collections team.",
                            "Partial payment arrangement made.",
                            None,
                        ]
                    )
                ),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# insert helpers
# ---------------------------------------------------------------------------

def upsert_table(conn, table, rows, conflict_col):
    if not rows:
        return
    cols = list(rows[0].keys())
    placeholders = ", ".join(f":{c}" for c in cols)
    col_list = ", ".join(cols)
    stmt = text(
        f"""
        INSERT INTO {table} ({col_list})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_col}) DO NOTHING
        """
    )
    conn.execute(stmt, rows)
    print(f"   [OK] Upserted {len(rows)} rows into {table}")


def seed():
    print("\n===================================")
    print("  RecoverOS - New Tables Seed")
    print("===================================\n")

    promises = build_promises(120)
    batch_runs = build_batch_runs(60)
    escalations = build_escalations(80)

    with engine.begin() as conn:
        upsert_table(conn, "promise_to_pay", promises, "promise_id")
        upsert_table(conn, "batch_runs", batch_runs, "run_id")
        upsert_table(conn, "escalations", escalations, "escalation_id")

    print("\n===================================")
    print("  Seeding complete!")
    print("===================================\n")


if __name__ == "__main__":
    seed()
