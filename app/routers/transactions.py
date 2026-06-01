from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.exceptions import ForbiddenError
from app.schemas.transaction import (
    CreateTransactionRequest,
    ListTransactionsResponse,
    TransactionResponse,
)
from app.services import account_service, transaction_service

router = APIRouter(
    prefix="/v1/accounts/{accountNumber}/transactions",
    tags=["transactions"],
)


async def _get_owned_account(
    accountNumber: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    """Shared dependency: resolve account and verify ownership."""
    account = await account_service.get_account(db, accountNumber)
    if account.user_id != current_user_id:
        raise ForbiddenError("You do not have permission to access this account")
    return account


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    body: CreateTransactionRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
    account=Depends(_get_owned_account),
):
    txn = await transaction_service.create_transaction(db, account, current_user_id, body)
    return TransactionResponse.from_orm(txn)


@router.get("", response_model=ListTransactionsResponse)
async def list_transactions(
    account=Depends(_get_owned_account),
    db: AsyncSession = Depends(get_db),
):
    txns = await transaction_service.list_transactions(db, account.account_number)
    return ListTransactionsResponse(
        transactions=[TransactionResponse.from_orm(t) for t in txns]
    )


@router.get("/{transactionId}", response_model=TransactionResponse)
async def get_transaction(
    transactionId: str,
    account=Depends(_get_owned_account),
    db: AsyncSession = Depends(get_db),
):
    txn = await transaction_service.get_transaction(db, account.account_number, transactionId)
    return TransactionResponse.from_orm(txn)
