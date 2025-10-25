"""
Transaction endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.transaction import Transaction
from app.models.client import Client
from app.schemas.transaction import Transaction as TransactionSchema
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[TransactionSchema])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    client_id: int = None,
    exchange: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List transactions with filters
    """
    query = select(Transaction)
    
    # Filter by client
    if client_id:
        # Check client access
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        if current_user.role == UserRole.MANAGER and client.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        query = query.where(Transaction.client_id == client_id)
    elif current_user.role == UserRole.MANAGER:
        # Managers see only their clients' transactions
        client_ids = await db.execute(
            select(Client.id).where(Client.manager_id == current_user.id)
        )
        client_id_list = [cid[0] for cid in client_ids.all()]
        query = query.where(Transaction.client_id.in_(client_id_list))
    
    # Filter by exchange
    if exchange:
        query = query.where(Transaction.exchange == exchange)
    
    # Filter by date range
    if start_date:
        query = query.where(Transaction.executed_at >= start_date)
    if end_date:
        query = query.where(Transaction.executed_at <= end_date)
    
    query = query.order_by(Transaction.executed_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return transactions


@router.get("/{transaction_id}", response_model=TransactionSchema)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get transaction by ID
    """
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.MANAGER:
        client_result = await db.execute(
            select(Client).where(Client.id == transaction.client_id)
        )
        client = client_result.scalar_one_or_none()
        
        if not client or client.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return transaction

