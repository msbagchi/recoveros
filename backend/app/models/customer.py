from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    customer_id: Mapped[str] = mapped_column(
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

    segment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    successful_payments: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    lifetime_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    previous_recoveries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    preferred_payment_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )