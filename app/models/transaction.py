import secrets
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _generate_transaction_id() -> str:
    return f"tan-{secrets.token_hex(4)}"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=_generate_transaction_id
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="GBP")
    type: Mapped[str] = mapped_column(String, nullable=False)  # "deposit" | "withdrawal"
    reference: Mapped[str | None] = mapped_column(String, nullable=True)

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    account_number: Mapped[str] = mapped_column(
        String,
        ForeignKey("accounts.account_number", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="transactions"
    )
    account: Mapped["BankAccount"] = relationship(  # noqa: F821
        "BankAccount", back_populates="transactions"
    )
