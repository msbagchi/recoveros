from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from backend.app.db.database import Base


class Escalation(Base):

    __tablename__ = "escalations"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    escalation_id = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    transaction_id = Column(
        String(50),
        index=True,
        nullable=False,
    )

    merchant_id = Column(
        String(50),
        index=True,
        nullable=True,
    )

    reason = Column(
        String(300),
        nullable=False,
    )

    status = Column(
        String(30),
        default="PENDING",
        index=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    resolved_at = Column(
        DateTime,
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )
