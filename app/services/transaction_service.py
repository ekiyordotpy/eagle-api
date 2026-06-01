from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError, UnprocessableError
from app.models.account import BankAccount
from app.models.transaction import Transaction
from app.schemas.transaction import CreateTransactionRequest


async def create_transaction(
    db: AsyncSession,
    account: BankAccount,
    user_id: str,
    body: CreateTransactionRequest,
) -> Transaction:
    # Lock the account row for the duration of this transaction to prevent race conditions
    result = await db.execute(
        select(BankAccount)
        .where(BankAccount.account_number == account.account_number)
        .with_for_update()
    )
    locked_account = result.scalar_one()

    if body.type == "withdrawal":
        new_balance = locked_account.balance - body.amount
        if new_balance < Decimal("0.00"):
            raise UnprocessableError("Insufficient funds to process transaction")
        locked_account.balance = new_balance
    else:
        new_balance = locked_account.balance + body.amount
        if new_balance > Decimal("10000.00"):
            raise UnprocessableError("Transaction would exceed maximum account balance of 10000.00")
        locked_account.balance = new_balance

    txn = Transaction(
        amount=body.amount,
        currency=body.currency,
        type=body.type,
        reference=body.reference,
        user_id=user_id,
        account_number=locked_account.account_number,
    )
    db.add(txn)
    await db.commit()
    await db.refresh(txn)
    return txn


async def list_transactions(db: AsyncSession, account_number: str) -> list[Transaction]:
    result = await db.execute(
        select(Transaction).where(Transaction.account_number == account_number)
    )
    return list(result.scalars().all())


async def get_transaction(
    db: AsyncSession, account_number: str, transaction_id: str
) -> Transaction:
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.account_number == account_number,
        )
    )
    txn = result.scalar_one_or_none()
    if txn is None:
        raise NotFoundError("Transaction not found")
    return txn
