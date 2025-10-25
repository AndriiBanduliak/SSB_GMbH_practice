"""
Transaction Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionSide, TransactionStatus
from app.models.client import ExchangeType


class TransactionBase(BaseModel):
    symbol: str
    side: TransactionSide
    quantity: float
    price: float
    total_amount: float
    fee: float = 0.0
    fee_currency: Optional[str] = None


class TransactionCreate(TransactionBase):
    client_id: int
    exchange: ExchangeType
    exchange_order_id: str
    executed_at: datetime
    status: TransactionStatus = TransactionStatus.COMPLETED


class Transaction(TransactionBase):
    id: int
    client_id: int
    exchange: ExchangeType
    exchange_order_id: str
    status: TransactionStatus
    executed_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

