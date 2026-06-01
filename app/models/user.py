import secrets
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _generate_user_id() -> str:
    return f"usr-{secrets.token_hex(4)}"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=_generate_user_id
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    # Flat address columns
    address_line1: Mapped[str] = mapped_column(String, nullable=False)
    address_line2: Mapped[str | None] = mapped_column(String, nullable=True)
    address_line3: Mapped[str | None] = mapped_column(String, nullable=True)
    address_town: Mapped[str] = mapped_column(String, nullable=False)
    address_county: Mapped[str] = mapped_column(String, nullable=False)
    address_postcode: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    accounts: Mapped[list["BankAccount"]] = relationship(  # noqa: F821
        "BankAccount", back_populates="user", lazy="select"
    )
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="user", lazy="select"
    )
