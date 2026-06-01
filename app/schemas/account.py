from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CreateBankAccountRequest(BaseModel):
    name: str
    accountType: Literal["personal"]


class UpdateBankAccountRequest(BaseModel):
    name: str | None = None
    accountType: Literal["personal"] | None = None


class BankAccountResponse(BaseModel):
    accountNumber: str
    sortCode: Literal["10-10-10"]
    name: str
    accountType: Literal["personal"]
    balance: Decimal = Field(ge=Decimal("0.00"), le=Decimal("10000.00"))
    currency: Literal["GBP"]
    createdTimestamp: datetime
    updatedTimestamp: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, account: object) -> "BankAccountResponse":
        return cls(
            accountNumber=account.account_number,  # type: ignore[attr-defined]
            sortCode=account.sort_code,  # type: ignore[attr-defined]
            name=account.name,  # type: ignore[attr-defined]
            accountType=account.account_type,  # type: ignore[attr-defined]
            balance=account.balance,  # type: ignore[attr-defined]
            currency=account.currency,  # type: ignore[attr-defined]
            createdTimestamp=account.created_at,  # type: ignore[attr-defined]
            updatedTimestamp=account.updated_at,  # type: ignore[attr-defined]
        )


class ListBankAccountsResponse(BaseModel):
    accounts: list[BankAccountResponse]
