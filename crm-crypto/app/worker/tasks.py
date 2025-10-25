"""
Celery tasks for background processing
"""
from celery import Task
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging

from app.worker.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.client import Client, ClientAPIKey, ExchangeType
from app.models.transaction import Transaction, TransactionStatus
from app.models.pnl import PnLPeriod
from app.core.security import decrypt_api_key
from app.integrations.binance_client import BinanceIntegration
from app.integrations.coinbase_client import CoinbaseIntegration
from app.services.pnl_calculator import PnLCalculator

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = AsyncSessionLocal()
        return self._db


@celery_app.task(bind=True, base=DatabaseTask)
def sync_client_exchange_data(self, client_id: int, exchange: str):
    """
    Sync data for a specific client and exchange
    """
    import asyncio
    return asyncio.run(async_sync_client_exchange_data(client_id, exchange))


async def async_sync_client_exchange_data(client_id: int, exchange: str):
    """
    Async function to sync client exchange data
    """
    async with AsyncSessionLocal() as db:
        try:
            logger.info(f"Starting sync for client {client_id} on {exchange}")
            
            # Get client and API key
            result = await db.execute(
                select(Client)
                .options(selectinload(Client.api_keys))
                .where(Client.id == client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                logger.error(f"Client {client_id} not found")
                return {"error": "Client not found"}
            
            # Get API key for the exchange
            api_key = None
            for key in client.api_keys:
                if key.exchange.value == exchange and key.is_active:
                    api_key = key
                    break
            
            if not api_key:
                logger.warning(f"No active API key for {exchange} for client {client_id}")
                return {"error": f"No API key for {exchange}"}
            
            # Decrypt keys
            decrypted_key = decrypt_api_key(api_key.encrypted_api_key)
            decrypted_secret = decrypt_api_key(api_key.encrypted_api_secret)
            
            # Initialize exchange client
            if exchange == 'binance':
                exchange_client = BinanceIntegration(decrypted_key, decrypted_secret)
            elif exchange == 'coinbase':
                exchange_client = CoinbaseIntegration(decrypted_key, decrypted_secret)
            else:
                logger.error(f"Unsupported exchange: {exchange}")
                return {"error": "Unsupported exchange"}
            
            # Test connection
            if not exchange_client.test_connection():
                error_msg = f"Failed to connect to {exchange}"
                api_key.sync_error = error_msg
                await db.commit()
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Sync balances
            try:
                total_balance = exchange_client.get_total_balance_usdt()
                client.current_aum = total_balance
                logger.info(f"Updated AUM for client {client_id}: ${total_balance:.2f}")
            except Exception as e:
                logger.error(f"Failed to sync balances: {str(e)}")
            
            # Sync trades (last 7 days)
            try:
                start_date = datetime.utcnow() - timedelta(days=7)
                trades = exchange_client.get_trades(start_date=start_date, limit=1000)
                
                synced_count = 0
                for trade in trades:
                    # Check if transaction already exists
                    result = await db.execute(
                        select(Transaction).where(
                            Transaction.client_id == client_id,
                            Transaction.exchange_order_id == trade['exchange_order_id'],
                            Transaction.exchange == exchange
                        )
                    )
                    existing = result.scalar_one_or_none()
                    
                    if not existing:
                        # Create new transaction
                        transaction = Transaction(
                            client_id=client_id,
                            exchange=exchange,
                            **trade
                        )
                        db.add(transaction)
                        synced_count += 1
                
                if synced_count > 0:
                    await db.commit()
                    logger.info(f"Synced {synced_count} new transactions for client {client_id}")
            except Exception as e:
                logger.error(f"Failed to sync trades: {str(e)}")
                api_key.sync_error = str(e)
            
            # Update sync timestamp
            api_key.last_sync = datetime.utcnow()
            api_key.sync_error = None
            await db.commit()
            
            return {
                "success": True,
                "client_id": client_id,
                "exchange": exchange,
                "synced_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error syncing client {client_id} on {exchange}: {str(e)}")
            await db.rollback()
            return {"error": str(e)}


@celery_app.task(bind=True)
def sync_all_clients(self, exchange: str):
    """
    Sync all clients for a specific exchange
    """
    import asyncio
    return asyncio.run(async_sync_all_clients(exchange))


async def async_sync_all_clients(exchange: str):
    """
    Async function to sync all clients
    """
    async with AsyncSessionLocal() as db:
        try:
            logger.info(f"Starting sync for all clients on {exchange}")
            
            # Get all active API keys for the exchange
            result = await db.execute(
                select(ClientAPIKey)
                .where(
                    ClientAPIKey.exchange == exchange,
                    ClientAPIKey.is_active == True
                )
            )
            api_keys = result.scalars().all()
            
            logger.info(f"Found {len(api_keys)} active API keys for {exchange}")
            
            # Sync each client
            results = []
            for api_key in api_keys:
                try:
                    result = await async_sync_client_exchange_data(api_key.client_id, exchange)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to sync client {api_key.client_id}: {str(e)}")
                    results.append({"error": str(e), "client_id": api_key.client_id})
            
            return {
                "success": True,
                "exchange": exchange,
                "total_clients": len(api_keys),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in sync_all_clients for {exchange}: {str(e)}")
            return {"error": str(e)}


@celery_app.task(bind=True)
def calculate_client_pnl(self, client_id: int, period: str):
    """
    Calculate P&L for a specific client
    """
    import asyncio
    return asyncio.run(async_calculate_client_pnl(client_id, period))


async def async_calculate_client_pnl(client_id: int, period: str):
    """
    Async function to calculate client P&L
    """
    async with AsyncSessionLocal() as db:
        try:
            logger.info(f"Calculating P&L for client {client_id}, period: {period}")
            
            calculator = PnLCalculator(db)
            period_enum = PnLPeriod(period)
            
            # Get period dates
            period_start, period_end = calculator.get_period_dates(period_enum)
            
            # Calculate P&L
            pnl_data = await calculator.calculate_pnl(
                client_id=client_id,
                period=period_enum,
                period_start=period_start,
                period_end=period_end
            )
            
            # Save P&L record
            pnl_record = await calculator.save_pnl_record(pnl_data)
            
            logger.info(f"P&L calculated for client {client_id}: ${pnl_data['total_pnl']:.2f}")
            
            return {
                "success": True,
                "client_id": client_id,
                "period": period,
                "total_pnl": pnl_data['total_pnl'],
                "roi_percentage": pnl_data['roi_percentage']
            }
        
        except Exception as e:
            logger.error(f"Error calculating P&L for client {client_id}: {str(e)}")
            await db.rollback()
            return {"error": str(e)}


@celery_app.task(bind=True)
def calculate_all_clients_pnl(self, period: str):
    """
    Calculate P&L for all clients
    """
    import asyncio
    return asyncio.run(async_calculate_all_clients_pnl(period))


async def async_calculate_all_clients_pnl(period: str):
    """
    Async function to calculate P&L for all clients
    """
    async with AsyncSessionLocal() as db:
        try:
            logger.info(f"Calculating P&L for all clients, period: {period}")
            
            # Get all active clients
            result = await db.execute(
                select(Client).where(Client.status == 'active')
            )
            clients = result.scalars().all()
            
            logger.info(f"Found {len(clients)} active clients")
            
            # Calculate P&L for each client
            results = []
            for client in clients:
                try:
                    result = await async_calculate_client_pnl(client.id, period)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to calculate P&L for client {client.id}: {str(e)}")
                    results.append({"error": str(e), "client_id": client.id})
            
            return {
                "success": True,
                "period": period,
                "total_clients": len(clients),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in calculate_all_clients_pnl: {str(e)}")
            return {"error": str(e)}

