"""
Pipeline endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.pipeline import Pipeline, PipelineStage
from app.schemas.pipeline import (
    Pipeline as PipelineSchema,
    PipelineCreate,
    PipelineUpdate,
    PipelineStage as PipelineStageSchema,
    PipelineStageCreate,
    PipelineStageUpdate
)
from app.api.deps import get_current_user, get_current_admin

router = APIRouter()


@router.get("/", response_model=List[PipelineSchema])
async def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all pipelines
    """
    result = await db.execute(
        select(Pipeline)
        .where(Pipeline.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    pipelines = result.scalars().all()
    return pipelines


@router.post("/", response_model=PipelineSchema, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_in: PipelineCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new pipeline (Admin only)
    """
    pipeline = Pipeline(**pipeline_in.model_dump())
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)
    
    return pipeline


@router.get("/{pipeline_id}", response_model=PipelineSchema)
async def get_pipeline(
    pipeline_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pipeline by ID
    """
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )
    
    return pipeline


@router.put("/{pipeline_id}", response_model=PipelineSchema)
async def update_pipeline(
    pipeline_id: int,
    pipeline_in: PipelineUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update pipeline (Admin only)
    """
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )
    
    update_data = pipeline_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pipeline, field, value)
    
    await db.commit()
    await db.refresh(pipeline)
    
    return pipeline


# Pipeline Stages
@router.post("/{pipeline_id}/stages", response_model=PipelineStageSchema, status_code=status.HTTP_201_CREATED)
async def create_stage(
    pipeline_id: int,
    stage_in: PipelineStageCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new pipeline stage (Admin only)
    """
    # Check pipeline exists
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )
    
    stage_data = stage_in.model_dump()
    stage_data['pipeline_id'] = pipeline_id
    
    stage = PipelineStage(**stage_data)
    db.add(stage)
    await db.commit()
    await db.refresh(stage)
    
    return stage


@router.put("/stages/{stage_id}", response_model=PipelineStageSchema)
async def update_stage(
    stage_id: int,
    stage_in: PipelineStageUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update pipeline stage (Admin only)
    """
    result = await db.execute(select(PipelineStage).where(PipelineStage.id == stage_id))
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    update_data = stage_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stage, field, value)
    
    await db.commit()
    await db.refresh(stage)
    
    return stage


@router.delete("/stages/{stage_id}")
async def delete_stage(
    stage_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete pipeline stage (Admin only)
    """
    result = await db.execute(select(PipelineStage).where(PipelineStage.id == stage_id))
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    await db.delete(stage)
    await db.commit()
    
    return {"message": "Stage deleted successfully"}

