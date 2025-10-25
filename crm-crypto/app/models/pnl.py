"""
P&L (Profit and Loss) tracking model
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base
from app.models.client import ExchangeType


class PnLPeriod(str, enum.Enum):
    """P&L calculation period"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"


class PnLRecord(Base):
    """P&L record for client performance tracking"""
    __tablename__ = "pnl_records"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    exchange = Column(SQLEnum(ExchangeType), nullable=True)
    
    # Period
    period = Column(SQLEnum(PnLPeriod), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Portfolio values
    starting_balance = Column(Float, nullable=False)
    ending_balance = Column(Float, nullable=False)
    
    # P&L metrics
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    
    # Performance metrics
    roi_percentage = Column(Float, default=0.0)  # Return on Investment
    total_fees = Column(Float, default=0.0)
    
    # Risk metrics
    max_drawdown = Column(Float, default=0.0)
    max_drawdown_percentage = Column(Float, default=0.0)
    
    # Trade statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="pnl_records")
    
    def __repr__(self):
        return f"<PnLRecord {self.client_id} {self.period} PnL: {self.total_pnl}>"

