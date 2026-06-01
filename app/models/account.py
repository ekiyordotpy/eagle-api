import secrets
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _generate_account_number() -> str:
    return f"01{secrets.randbelow(1_000_000):06d}"


class BankAccount(Base):
    __tablename__ = "accounts"

    account_number: Mapped[str] = mapped_column(
        String, primary_key=True, default=_generate_account_number
    )
    sort_code: Mapped[str] = mapped_column(String, nullable=False, default="10-10-10")
    name: Mapped[str] = mapped_column(String, nullable=False)
    account_type: Mapped[str] = mapped_column(String, nullable=False, default="personal")
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    currency: Mapped[str] = mapped_column(String, nullable=False, default="GBP")

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="accounts"
    )
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="account", lazy="select"
    )
