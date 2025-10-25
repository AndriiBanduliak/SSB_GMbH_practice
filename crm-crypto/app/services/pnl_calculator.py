"""
P&L calculation service
"""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import logging

from app.models.transaction import Transaction
from app.models.pnl import PnLRecord, PnLPeriod
from app.models.client import Client

logger = logging.getLogger(__name__)


class PnLCalculator:
    """Calculate P&L metrics for clients"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_pnl(
        self,
        client_id: int,
        period: PnLPeriod,
        period_start: datetime,
        period_end: datetime,
        exchange: str = None
    ) -> Dict:
        """
        Calculate P&L for a specific period
        """
        try:
            # Get all transactions in the period
            query = select(Transaction).where(
                and_(
                    Transaction.client_id == client_id,
                    Transaction.executed_at >= period_start,
                    Transaction.executed_at <= period_end,
                    Transaction.status == 'completed'
                )
            )
            
            if exchange:
                query = query.where(Transaction.exchange == exchange)
            
            result = await self.db.execute(query)
            transactions = result.scalars().all()
            
            if not transactions:
                return self._empty_pnl_record(client_id, period, period_start, period_end, exchange)
            
            # Calculate metrics
            total_buy = sum(t.total_amount for t in transactions if t.side == 'buy')
            total_sell = sum(t.total_amount for t in transactions if t.side == 'sell')
            total_fees = sum(t.fee for t in transactions)
            
            # Calculate P&L
            realized_pnl = total_sell - total_buy - total_fees
            
            # Get starting and ending balance (simplified - in production you'd query actual balances)
            starting_balance = total_buy
            ending_balance = total_sell
            
            # Calculate ROI
            roi_percentage = (realized_pnl / starting_balance * 100) if starting_balance > 0 else 0
            
            # Calculate trade statistics
            total_trades = len(transactions)
            winning_trades = sum(1 for t in transactions if t.side == 'sell' and t.total_amount > 0)
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate drawdown (simplified - would need portfolio value history for accurate calculation)
            max_drawdown, max_drawdown_pct = await self._calculate_drawdown(
                client_id, period_start, period_end, exchange
            )
            
            return {
                'client_id': client_id,
                'exchange': exchange,
                'period': period,
                'period_start': period_start,
                'period_end': period_end,
                'starting_balance': starting_balance,
                'ending_balance': ending_balance,
                'realized_pnl': realized_pnl,
                'unrealized_pnl': 0.0,  # Would need current positions
                'total_pnl': realized_pnl,
                'roi_percentage': roi_percentage,
                'total_fees': total_fees,
                'max_drawdown': max_drawdown,
                'max_drawdown_percentage': max_drawdown_pct,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate
            }
        except Exception as e:
            logger.error(f"Failed to calculate P&L: {str(e)}")
            raise
    
    async def _calculate_drawdown(
        self,
        client_id: int,
        start_date: datetime,
        end_date: datetime,
        exchange: str = None
    ) -> Tuple[float, float]:
        """
        Calculate maximum drawdown
        Simplified version - in production would use daily portfolio values
        """
        try:
            query = select(Transaction).where(
                and_(
                    Transaction.client_id == client_id,
                    Transaction.executed_at >= start_date,
                    Transaction.executed_at <= end_date
                )
            )
            
            if exchange:
                query = query.where(Transaction.exchange == exchange)
            
            query = query.order_by(Transaction.executed_at)
            result = await self.db.execute(query)
            transactions = result.scalars().all()
            
            if not transactions:
                return 0.0, 0.0
            
            # Calculate running balance
            peak = 0.0
            max_drawdown = 0.0
            current_balance = 0.0
            
            for tx in transactions:
                if tx.side == 'buy':
                    current_balance -= tx.total_amount
                else:
                    current_balance += tx.total_amount
                
                if current_balance > peak:
                    peak = current_balance
                
                drawdown = peak - current_balance
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            max_drawdown_pct = (max_drawdown / peak * 100) if peak > 0 else 0
            
            return max_drawdown, max_drawdown_pct
        except Exception as e:
            logger.error(f"Failed to calculate drawdown: {str(e)}")
            return 0.0, 0.0
    
    def _empty_pnl_record(
        self,
        client_id: int,
        period: PnLPeriod,
        period_start: datetime,
        period_end: datetime,
        exchange: str = None
    ) -> Dict:
        """Return empty P&L record when no transactions"""
        return {
            'client_id': client_id,
            'exchange': exchange,
            'period': period,
            'period_start': period_start,
            'period_end': period_end,
            'starting_balance': 0.0,
            'ending_balance': 0.0,
            'realized_pnl': 0.0,
            'unrealized_pnl': 0.0,
            'total_pnl': 0.0,
            'roi_percentage': 0.0,
            'total_fees': 0.0,
            'max_drawdown': 0.0,
            'max_drawdown_percentage': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0
        }
    
    async def save_pnl_record(self, pnl_data: Dict) -> PnLRecord:
        """Save P&L record to database"""
        try:
            pnl_record = PnLRecord(**pnl_data)
            self.db.add(pnl_record)
            await self.db.commit()
            await self.db.refresh(pnl_record)
            return pnl_record
        except Exception as e:
            logger.error(f"Failed to save P&L record: {str(e)}")
            await self.db.rollback()
            raise
    
    @staticmethod
    def get_period_dates(period: PnLPeriod, reference_date: datetime = None) -> Tuple[datetime, datetime]:
        """Get start and end dates for a period"""
        if reference_date is None:
            reference_date = datetime.utcnow()
        
        if period == PnLPeriod.DAILY:
            start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1) - timedelta(microseconds=1)
        elif period == PnLPeriod.WEEKLY:
            start = reference_date - timedelta(days=reference_date.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7) - timedelta(microseconds=1)
        elif period == PnLPeriod.MONTHLY:
            start = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = start + timedelta(days=32)
            end = next_month.replace(day=1) - timedelta(microseconds=1)
        elif period == PnLPeriod.YEARLY:
            start = reference_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=start.year + 1) - timedelta(microseconds=1)
        else:  # ALL_TIME
            start = datetime(2020, 1, 1)  # Arbitrary start date
            end = datetime.utcnow()
        
        return start, end

