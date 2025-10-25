"""
Client management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.db.session import get_db
from app.core.security import encrypt_api_key
from app.models.user import User, UserRole
from app.models.client import Client, ClientAPIKey
from app.schemas.client import (
    Client as ClientSchema,
    ClientCreate,
    ClientUpdate,
    APIKey as APIKeySchema,
    APIKeyCreate,
    APIKeyUpdate
)
from app.api.deps import get_current_user, get_current_manager_or_admin

router = APIRouter()


@router.get("/", response_model=List[ClientSchema])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List clients
    - Managers see only their clients
    - Admins see all clients
    - Analysts see all clients (read-only)
    """
    query = select(Client)
    
    # Filter by manager if not admin
    if current_user.role == UserRole.MANAGER:
        query = query.where(Client.manager_id == current_user.id)
    
    # Filter by status if provided
    if status:
        query = query.where(Client.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    clients = result.scalars().all()
    
    return clients


@router.post("/", response_model=ClientSchema, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_in: ClientCreate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new client
    """
    # Check if email exists
    result = await db.execute(select(Client).where(Client.email == client_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this email already exists"
        )
    
    # If no manager assigned and user is manager, assign to self
    manager_id = client_in.manager_id
    if not manager_id and current_user.role == UserRole.MANAGER:
        manager_id = current_user.id
    
    # Create client
    client_data = client_in.model_dump()
    client_data['manager_id'] = manager_id
    
    client = Client(**client_data)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    return client


@router.get("/{client_id}", response_model=ClientSchema)
async def get_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get client by ID
    """
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.MANAGER and client.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientSchema)
async def update_client(
    client_id: int,
    client_in: ClientUpdate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update client
    """
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.MANAGER and client.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update fields
    update_data = client_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    await db.commit()
    await db.refresh(client)
    
    return client


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete client
    """
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.MANAGER and client.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete(client)
    await db.commit()
    
    return {"message": "Client deleted successfully"}


# API Keys endpoints
@router.get("/{client_id}/api-keys", response_model=List[APIKeySchema])
async def list_client_api_keys(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List client API keys (encrypted keys are not returned)
    """
    # Check client access
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if current_user.role == UserRole.MANAGER and client.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    result = await db.execute(
        select(ClientAPIKey).where(ClientAPIKey.client_id == client_id)
    )
    api_keys = result.scalars().all()
    
    return api_keys


@router.post("/{client_id}/api-keys", response_model=APIKeySchema, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    client_id: int,
    api_key_in: APIKeyCreate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Add API key for client (keys will be encrypted)
    """
    # Check client exists and access
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if current_user.role == UserRole.MANAGER and client.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if API key for this exchange already exists
    result = await db.execute(
        select(ClientAPIKey).where(
            ClientAPIKey.client_id == client_id,
            ClientAPIKey.exchange == api_key_in.exchange
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key for {api_key_in.exchange} already exists"
        )
    
    # Encrypt keys
    encrypted_key = encrypt_api_key(api_key_in.api_key)
    encrypted_secret = encrypt_api_key(api_key_in.api_secret)
    
    # Create API key
    api_key = ClientAPIKey(
        client_id=client_id,
        exchange=api_key_in.exchange,
        key_type=api_key_in.key_type,
        encrypted_api_key=encrypted_key,
        encrypted_api_secret=encrypted_secret
    )
    
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    return api_key


@router.put("/{client_id}/api-keys/{key_id}", response_model=APIKeySchema)
async def update_api_key(
    client_id: int,
    key_id: int,
    api_key_in: APIKeyUpdate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update API key (e.g., activate/deactivate)
    """
    result = await db.execute(
        select(ClientAPIKey).where(
            ClientAPIKey.id == key_id,
            ClientAPIKey.client_id == client_id
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check permissions
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if current_user.role == UserRole.MANAGER and client.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update fields
    update_data = api_key_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(api_key, field, value)
    
    await db.commit()
    await db.refresh(api_key)
    
    return api_key


@router.delete("/{client_id}/api-keys/{key_id}")
async def delete_api_key(
    client_id: int,
    key_id: int,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete API key
    """
    result = await db.execute(
        select(ClientAPIKey).where(
            ClientAPIKey.id == key_id,
            ClientAPIKey.client_id == client_id
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check permissions
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if current_user.role == UserRole.MANAGER and client.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete(api_key)
    await db.commit()
    
    return {"message": "API key deleted successfully"}

