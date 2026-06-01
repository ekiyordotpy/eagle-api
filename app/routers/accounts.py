from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.exceptions import ForbiddenError
from app.schemas.account import (
    BankAccountResponse,
    CreateBankAccountRequest,
    ListBankAccountsResponse,
    UpdateBankAccountRequest,
)
from app.services import account_service

router = APIRouter(prefix="/v1/accounts", tags=["accounts"])


@router.post("", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    body: CreateBankAccountRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    account = await account_service.create_account(db, current_user_id, body)
    return BankAccountResponse.from_orm(account)


@router.get("", response_model=ListBankAccountsResponse)
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    accounts = await account_service.list_accounts(db, current_user_id)
    return ListBankAccountsResponse(
        accounts=[BankAccountResponse.from_orm(a) for a in accounts]
    )


@router.get("/{accountNumber}", response_model=BankAccountResponse)
async def get_account(
    accountNumber: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    account = await account_service.get_account(db, accountNumber)
    if account.user_id != current_user_id:
        raise ForbiddenError("You do not have permission to access this account")
    return BankAccountResponse.from_orm(account)


@router.patch("/{accountNumber}", response_model=BankAccountResponse)
async def update_account(
    accountNumber: str,
    body: UpdateBankAccountRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    account = await account_service.get_account(db, accountNumber)
    if account.user_id != current_user_id:
        raise ForbiddenError("You do not have permission to update this account")
    updated = await account_service.update_account(db, account, body)
    return BankAccountResponse.from_orm(updated)


@router.delete("/{accountNumber}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    accountNumber: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    account = await account_service.get_account(db, accountNumber)
    if account.user_id != current_user_id:
        raise ForbiddenError("You do not have permission to delete this account")
    await account_service.delete_account(db, account)
