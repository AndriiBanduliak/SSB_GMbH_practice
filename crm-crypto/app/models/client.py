"""
Client and API Key models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class RiskLevel(str, enum.Enum):
    """Client risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class ClientStatus(str, enum.Enum):
    """Client status"""
    LEAD = "lead"
    PROSPECT = "prospect"
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"


class LeadSource(str, enum.Enum):
    """Source of lead"""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    COLD_CALL = "cold_call"
    CONFERENCE = "conference"
    OTHER = "other"


class Client(Base):
    """Client/Lead model"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    
    # CRM specific
    status = Column(SQLEnum(ClientStatus), default=ClientStatus.LEAD, nullable=False)
    lead_source = Column(SQLEnum(LeadSource), nullable=True)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.MODERATE)
    
    # Trading info
    current_aum = Column(Float, default=0.0)  # Assets Under Management
    trading_strategy = Column(String, nullable=True)
    
    # Manager assignment
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Pipeline
    pipeline_stage_id = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_contact = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    manager = relationship("User", back_populates="managed_clients", foreign_keys=[manager_id])
    api_keys = relationship("ClientAPIKey", back_populates="client", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="client", cascade="all, delete-orphan")
    pnl_records = relationship("PnLRecord", back_populates="client", cascade="all, delete-orphan")
    pipeline_stage = relationship("PipelineStage", back_populates="clients")
    tasks = relationship("Task", back_populates="client")
    
    def __repr__(self):
        return f"<Client {self.full_name} ({self.status})>"


class ExchangeType(str, enum.Enum):
    """Supported exchanges"""
    BINANCE = "binance"
    COINBASE = "coinbase"


class APIKeyType(str, enum.Enum):
    """API key access type"""
    READ_ONLY = "read_only"
    TRADING = "trading"


class ClientAPIKey(Base):
    """Client API keys for exchanges (encrypted)"""
    __tablename__ = "client_api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    exchange = Column(SQLEnum(ExchangeType), nullable=False)
    key_type = Column(SQLEnum(APIKeyType), default=APIKeyType.READ_ONLY)
    
    # Encrypted fields
    encrypted_api_key = Column(Text, nullable=False)
    encrypted_api_secret = Column(Text, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    sync_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey {self.exchange} for Client {self.client_id}>"

