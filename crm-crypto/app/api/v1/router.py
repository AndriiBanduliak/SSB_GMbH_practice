"""
API v1 router aggregator
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, clients, transactions, pnl, pipelines, tasks

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(pnl.router, prefix="/pnl", tags=["P&L"])
api_router.include_router(pipelines.router, prefix="/pipelines", tags=["Pipelines"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

