from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class PromiseToPay(Base):
    __tablename__ = "promise_to_pay"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    promise_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    merchant_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("merchants.merchant_id"),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("customers.customer_id"),
        nullable=False,
        index=True,
    )

    transaction_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("transactions.transaction_id"),
        nullable=False,
        index=True,
    )

    promised_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    promise_date: Mapped[datetime] = mapped_column(
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )