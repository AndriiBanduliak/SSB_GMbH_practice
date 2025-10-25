"""
Coinbase exchange integration
"""
from typing import List, Dict, Optional
from datetime import datetime
from coinbase.wallet.client import Client as CoinbaseClient
from coinbase.wallet.error import CoinbaseError
import logging

logger = logging.getLogger(__name__)


class CoinbaseIntegration:
    """Coinbase exchange integration for fetching account data"""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize Coinbase client"""
        try:
            self.client = CoinbaseClient(api_key, api_secret)
            self.exchange = "coinbase"
        except Exception as e:
            logger.error(f"Failed to initialize Coinbase client: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test API key validity"""
        try:
            self.client.get_current_user()
            return True
        except CoinbaseError as e:
            logger.error(f"Coinbase API error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Coinbase connection error: {str(e)}")
            return False
    
    def get_balances(self) -> List[Dict]:
        """Get all accounts with non-zero balance"""
        try:
            accounts = self.client.get_accounts()
            balances = []
            
            for account in accounts.data:
                balance = float(account.balance.amount)
                
                if balance > 0:
                    balances.append({
                        'asset': account.currency.code,
                        'free': balance,
                        'locked': 0.0,  # Coinbase doesn't provide locked balance
                        'total': balance,
                        'account_id': account.id
                    })
            
            return balances
        except Exception as e:
            logger.error(f"Failed to get Coinbase balances: {str(e)}")
            raise
    
    def get_total_balance_usdt(self) -> float:
        """Get total account balance in USD equivalent"""
        try:
            balances = self.get_balances()
            total_usd = 0.0
            
            for balance in balances:
                asset = balance['asset']
                total = balance['total']
                
                if asset == 'USD' or asset == 'USDC':
                    total_usd += total
                else:
                    # Get spot price
                    try:
                        price_data = self.client.get_spot_price(currency_pair=f"{asset}-USD")
                        price = float(price_data.amount)
                        total_usd += total * price
                    except:
                        logger.warning(f"Could not get price for {asset}")
            
            return total_usd
        except Exception as e:
            logger.error(f"Failed to calculate total Coinbase balance: {str(e)}")
            raise
    
    def get_trades(self, account_id: Optional[str] = None, start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None, limit: int = 100) -> List[Dict]:
        """Get transaction history"""
        try:
            trades = []
            
            if account_id:
                # Get transactions for specific account
                account = self.client.get_account(account_id)
                transactions = account.get_transactions(limit=limit)
                
                for tx in transactions.data:
                    if tx.type in ['buy', 'sell']:
                        trade_data = self._format_transaction(tx, account.currency.code)
                        if trade_data:
                            trades.append(trade_data)
            else:
                # Get all accounts and their transactions
                accounts = self.client.get_accounts()
                
                for account in accounts.data:
                    try:
                        transactions = account.get_transactions(limit=limit)
                        
                        for tx in transactions.data:
                            if tx.type in ['buy', 'sell']:
                                trade_data = self._format_transaction(tx, account.currency.code)
                                if trade_data:
                                    trades.append(trade_data)
                    except:
                        continue
            
            # Filter by date if provided
            if start_date:
                trades = [t for t in trades if t['executed_at'] >= start_date]
            if end_date:
                trades = [t for t in trades if t['executed_at'] <= end_date]
            
            return trades
        except Exception as e:
            logger.error(f"Failed to get Coinbase trades: {str(e)}")
            raise
    
    def _format_transaction(self, tx, asset: str) -> Optional[Dict]:
        """Format transaction data"""
        try:
            if not tx.amount or not tx.native_amount:
                return None
            
            quantity = abs(float(tx.amount.amount))
            total_amount = abs(float(tx.native_amount.amount))
            price = total_amount / quantity if quantity > 0 else 0
            
            return {
                'exchange_order_id': tx.id,
                'symbol': f"{asset}/USD",
                'side': tx.type,
                'quantity': quantity,
                'price': price,
                'total_amount': total_amount,
                'fee': 0.0,  # Coinbase fee is usually included in the price
                'fee_currency': 'USD',
                'executed_at': datetime.fromisoformat(tx.created_at.replace('Z', '+00:00')),
                'status': 'completed'
            }
        except Exception as e:
            logger.warning(f"Failed to format transaction: {str(e)}")
            return None
    
    def get_buys_and_sells(self) -> List[Dict]:
        """Get all buy and sell orders"""
        try:
            accounts = self.client.get_accounts()
            orders = []
            
            for account in accounts.data:
                try:
                    # Get buys
                    buys = account.get_buys()
                    for buy in buys.data:
                        orders.append({
                            'order_id': buy.id,
                            'type': 'buy',
                            'asset': account.currency.code,
                            'amount': float(buy.amount.amount),
                            'total': float(buy.total.amount),
                            'status': buy.status,
                            'created_at': datetime.fromisoformat(buy.created_at.replace('Z', '+00:00'))
                        })
                    
                    # Get sells
                    sells = account.get_sells()
                    for sell in sells.data:
                        orders.append({
                            'order_id': sell.id,
                            'type': 'sell',
                            'asset': account.currency.code,
                            'amount': float(sell.amount.amount),
                            'total': float(sell.total.amount),
                            'status': sell.status,
                            'created_at': datetime.fromisoformat(sell.created_at.replace('Z', '+00:00'))
                        })
                except:
                    continue
            
            return orders
        except Exception as e:
            logger.error(f"Failed to get Coinbase orders: {str(e)}")
            raise

