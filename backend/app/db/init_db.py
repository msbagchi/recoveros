from backend.app.db.database import Base, engine
from backend.app.models import (
    Merchant,
    Customer,
    Transaction,
    RecoveryAction,
    PromiseToPay,
    BatchRun,
    Escalation,
)


def init_database():
    print("Creating RecoverOS database tables...")

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")


if __name__ == "__main__":
    init_database()
    