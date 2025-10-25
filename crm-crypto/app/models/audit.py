"""
Audit log model for tracking critical actions
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class AuditLog(Base):
    """Audit log for tracking critical system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Action details
    action = Column(String, nullable=False)  # login, logout, create_client, update_api_key, etc.
    resource_type = Column(String, nullable=True)  # user, client, api_key, etc.
    resource_id = Column(Integer, nullable=True)
    
    # Details
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # Store before/after values
    
    # Request info
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action} by User {self.user_id}>"

