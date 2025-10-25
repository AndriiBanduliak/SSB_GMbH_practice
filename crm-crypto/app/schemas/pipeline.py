"""
Pipeline Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Pipeline Stage
class PipelineStageBase(BaseModel):
    name: str
    description: Optional[str] = None
    order: int
    probability: int = 0


class PipelineStageCreate(PipelineStageBase):
    pipeline_id: int


class PipelineStageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    probability: Optional[int] = None


class PipelineStage(PipelineStageBase):
    id: int
    pipeline_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Pipeline
class PipelineBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False
    is_active: bool = True


class PipelineCreate(PipelineBase):
    pass


class PipelineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class Pipeline(PipelineBase):
    id: int
    created_at: datetime
    stages: List[PipelineStage] = []
    
    class Config:
        from_attributes = True

