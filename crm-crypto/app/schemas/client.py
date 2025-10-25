"""
Client Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.client import RiskLevel, ClientStatus, LeadSource, ExchangeType, APIKeyType


# Base schema
class ClientBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    status: ClientStatus = ClientStatus.LEAD
    lead_source: Optional[LeadSource] = None
    risk_level: RiskLevel = RiskLevel.MODERATE
    trading_strategy: Optional[str] = None
    notes: Optional[str] = None


# Create schema
class ClientCreate(ClientBase):
    manager_id: Optional[int] = None
    pipeline_stage_id: Optional[int] = None


# Update schema
class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[ClientStatus] = None
    lead_source: Optional[LeadSource] = None
    risk_level: Optional[RiskLevel] = None
    trading_strategy: Optional[str] = None
    notes: Optional[str] = None
    manager_id: Optional[int] = None
    pipeline_stage_id: Optional[int] = None
    current_aum: Optional[float] = None


# Response schema
class Client(ClientBase):
    id: int
    current_aum: float
    manager_id: Optional[int] = None
    pipeline_stage_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contact: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# API Key schemas
class APIKeyBase(BaseModel):
    exchange: ExchangeType
    key_type: APIKeyType = APIKeyType.READ_ONLY


class APIKeyCreate(APIKeyBase):
    api_key: str
    api_secret: str


class APIKeyUpdate(BaseModel):
    is_active: Optional[bool] = None


class APIKey(APIKeyBase):
    id: int
    client_id: int
    is_active: bool
    last_sync: Optional[datetime] = None
    sync_error: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

