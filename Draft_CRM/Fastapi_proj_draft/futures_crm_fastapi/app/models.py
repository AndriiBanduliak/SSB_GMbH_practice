from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base
from datetime import datetime

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    symbol = Column(String, index=True)
    type = Column(String, index=True)  # LONG/SHORT
    entry_price = Column(Numeric(15, 2))
    current_price = Column(Numeric(15, 2), nullable=True)
    quantity = Column(Numeric(20, 8))
    leverage = Column(Integer, default=1)
    pnl = Column(Numeric(15, 2), default=0)
    pnl_percentage = Column(Numeric(5, 2), default=0)
    status = Column(String, default="OPEN")  # OPEN/CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Trade {self.symbol} {self.type}>"
