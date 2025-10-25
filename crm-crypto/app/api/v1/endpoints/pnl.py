"""
P&L endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.pnl import PnLRecord, PnLPeriod
from app.models.client import Client
from app.schemas.pnl import PnL as PnLSchema, PnLSummary
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[PnLSchema])
async def list_pnl_records(
    skip: int = 0,
    limit: int = 100,
    client_id: int = None,
    period: PnLPeriod = None,
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List P&L records with filters
    """
    query = select(PnLRecord)
    
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
        
        query = query.where(PnLRecord.client_id == client_id)
    elif current_user.role == UserRole.MANAGER:
        # Managers see only their clients' P&L
        client_ids = await db.execute(
            select(Client.id).where(Client.manager_id == current_user.id)
        )
        client_id_list = [cid[0] for cid in client_ids.all()]
        query = query.where(PnLRecord.client_id.in_(client_id_list))
    
    # Filter by period
    if period:
        query = query.where(PnLRecord.period == period)
    
    # Filter by date range
    if start_date:
        query = query.where(PnLRecord.period_start >= start_date)
    if end_date:
        query = query.where(PnLRecord.period_end <= end_date)
    
    query = query.order_by(PnLRecord.period_end.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    pnl_records = result.scalars().all()
    
    return pnl_records


@router.get("/summary", response_model=List[PnLSummary])
async def get_pnl_summary(
    period: PnLPeriod = PnLPeriod.MONTHLY,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get P&L summary for dashboard
    """
    # Get clients based on user role
    if current_user.role == UserRole.MANAGER:
        clients_result = await db.execute(
            select(Client).where(Client.manager_id == current_user.id)
        )
    else:
        clients_result = await db.execute(select(Client))
    
    clients = clients_result.scalars().all()
    
    summaries = []
    for client in clients:
        # Get latest P&L for the period
        pnl_result = await db.execute(
            select(PnLRecord)
            .where(
                and_(
                    PnLRecord.client_id == client.id,
                    PnLRecord.period == period
                )
            )
            .order_by(PnLRecord.period_end.desc())
            .limit(1)
        )
        pnl = pnl_result.scalar_one_or_none()
        
        if pnl:
            summaries.append(
                PnLSummary(
                    client_id=client.id,
                    client_name=client.full_name,
                    total_pnl=pnl.total_pnl,
                    roi_percentage=pnl.roi_percentage,
                    current_aum=client.current_aum,
                    total_trades=pnl.total_trades,
                    win_rate=pnl.win_rate
                )
            )
    
    return summaries


@router.get("/{pnl_id}", response_model=PnLSchema)
async def get_pnl_record(
    pnl_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get P&L record by ID
    """
    result = await db.execute(select(PnLRecord).where(PnLRecord.id == pnl_id))
    pnl_record = result.scalar_one_or_none()
    
    if not pnl_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="P&L record not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.MANAGER:
        client_result = await db.execute(
            select(Client).where(Client.id == pnl_record.client_id)
        )
        client = client_result.scalar_one_or_none()
        
        if not client or client.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return pnl_record

