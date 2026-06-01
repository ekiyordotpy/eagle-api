from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.account import BankAccount
from app.schemas.account import CreateBankAccountRequest, UpdateBankAccountRequest


async def create_account(
    db: AsyncSession, user_id: str, body: CreateBankAccountRequest
) -> BankAccount:
    # Retry on the rare chance of account number collision
    for _ in range(5):
        account = BankAccount(
            name=body.name,
            account_type=body.accountType,
            user_id=user_id,
        )
        db.add(account)
        try:
            await db.commit()
            await db.refresh(account)
            return account
        except Exception as exc:
            await db.rollback()
            # Unique violation on account_number — retry
            if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
                continue
            raise

    raise ConflictError("Could not generate a unique account number")


async def list_accounts(db: AsyncSession, user_id: str) -> list[BankAccount]:
    result = await db.execute(
        select(BankAccount).where(BankAccount.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_account(db: AsyncSession, account_number: str) -> BankAccount:
    result = await db.execute(
        select(BankAccount).where(BankAccount.account_number == account_number)
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise NotFoundError("Account not found")
    return account


async def update_account(
    db: AsyncSession, account: BankAccount, body: UpdateBankAccountRequest
) -> BankAccount:
    if body.name is not None:
        account.name = body.name
    if body.accountType is not None:
        account.account_type = body.accountType

    await db.commit()
    await db.refresh(account)
    return account


async def delete_account(db: AsyncSession, account: BankAccount) -> None:
    await db.refresh(account, ["transactions"])
    if account.transactions:
        raise ConflictError("Cannot delete an account with existing transactions")
    await db.delete(account)
    await db.commit()
