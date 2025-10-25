"""
Task management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.task import Task
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[TaskSchema])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    assigned_to_me: bool = False,
    client_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List tasks
    """
    query = select(Task)
    
    # Filter by assigned user
    if assigned_to_me:
        query = query.where(Task.assigned_to_id == current_user.id)
    elif current_user.role == UserRole.ANALYST:
        # Analysts can only see their own tasks
        query = query.where(Task.assigned_to_id == current_user.id)
    
    # Filter by client
    if client_id:
        query = query.where(Task.client_id == client_id)
    
    query = query.order_by(Task.due_date.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return tasks


@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new task
    """
    task_data = task_in.model_dump()
    task_data['created_by_id'] = current_user.id
    
    task = Task(**task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return task


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get task by ID
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.ANALYST and task.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return task


@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update task
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.ANALYST and task.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update fields
    update_data = task_in.model_dump(exclude_unset=True)
    
    # Set completed_at if status is completed
    if update_data.get('status') == 'completed' and not task.completed_at:
        update_data['completed_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete task
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Only creator or admin can delete
    if task.created_by_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete(task)
    await db.commit()
    
    return {"message": "Task deleted successfully"}

