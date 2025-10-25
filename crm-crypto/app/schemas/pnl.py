"""
P&L Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.pnl import PnLPeriod
from app.models.client import ExchangeType


class PnLBase(BaseModel):
    period: PnLPeriod
    period_start: datetime
    period_end: datetime
    starting_balance: float
    ending_balance: float
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_pnl: float = 0.0
    roi_percentage: float = 0.0
    total_fees: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_percentage: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0


class PnLCreate(PnLBase):
    client_id: int
    exchange: Optional[ExchangeType] = None


class PnL(PnLBase):
    id: int
    client_id: int
    exchange: Optional[ExchangeType] = None
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class PnLSummary(BaseModel):
    """Summary P&L for dashboard"""
    client_id: int
    client_name: str
    total_pnl: float
    roi_percentage: float
    current_aum: float
    total_trades: int
    win_rate: float

