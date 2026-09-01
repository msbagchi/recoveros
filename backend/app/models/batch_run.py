from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)

from backend.app.db.database import Base


class BatchRun(Base):

    __tablename__ = "batch_runs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    run_id = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    merchant_id = Column(
        String(50),
        nullable=True,
        index=True,
    )

    started_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    attempted = Column(
        Integer,
        default=0,
        nullable=False,
    )

    executed = Column(
        Integer,
        default=0,
        nullable=False,
    )

    blocked = Column(
        Integer,
        default=0,
        nullable=False,
    )

    skipped = Column(
        Integer,
        default=0,
        nullable=False,
    )

    potential_amount = Column(
        Float,
        default=0.0,
        nullable=False,
    )
