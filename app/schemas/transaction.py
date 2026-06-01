from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CreateTransactionRequest(BaseModel):
    amount: Decimal = Field(gt=Decimal("0.00"), le=Decimal("10000.00"))
    currency: Literal["GBP"]
    type: Literal["deposit", "withdrawal"]
    reference: str | None = None


class TransactionResponse(BaseModel):
    id: str
    amount: Decimal
    currency: Literal["GBP"]
    type: Literal["deposit", "withdrawal"]
    reference: str | None = None
    userId: str | None = None
    createdTimestamp: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, txn: object) -> "TransactionResponse":
        return cls(
            id=txn.id,  # type: ignore[attr-defined]
            amount=txn.amount,  # type: ignore[attr-defined]
            currency=txn.currency,  # type: ignore[attr-defined]
            type=txn.type,  # type: ignore[attr-defined]
            reference=txn.reference,  # type: ignore[attr-defined]
            userId=txn.user_id,  # type: ignore[attr-defined]
            createdTimestamp=txn.created_at,  # type: ignore[attr-defined]
        )


class ListTransactionsResponse(BaseModel):
    transactions: list[TransactionResponse]
