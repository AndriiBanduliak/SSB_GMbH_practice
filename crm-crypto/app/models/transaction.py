"""
Transaction model for trade history
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base
from app.models.client import ExchangeType


class TransactionSide(str, enum.Enum):
    """Transaction side"""
    BUY = "buy"
    SELL = "sell"


class TransactionStatus(str, enum.Enum):
    """Transaction status"""
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transaction(Base):
    """Transaction/Trade model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Exchange info
    exchange = Column(SQLEnum(ExchangeType), nullable=False)
    exchange_order_id = Column(String, index=True, nullable=False)
    
    # Trade details
    symbol = Column(String, nullable=False)  # BTC/USDT, ETH/USDT, etc.
    side = Column(SQLEnum(TransactionSide), nullable=False)
    
    # Amounts
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)  # quantity * price
    
    # Fees
    fee = Column(Float, default=0.0)
    fee_currency = Column(String, nullable=True)
    
    # Status
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.COMPLETED)
    
    # Timestamps
    executed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.side} {self.quantity} {self.symbol} @ {self.price}>"

