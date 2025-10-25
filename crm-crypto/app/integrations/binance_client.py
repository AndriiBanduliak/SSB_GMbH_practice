"""
Binance exchange integration
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException
import logging

logger = logging.getLogger(__name__)


class BinanceIntegration:
    """Binance exchange integration for fetching account data"""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize Binance client"""
        try:
            self.client = BinanceClient(api_key, api_secret)
            self.exchange = "binance"
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test API key validity"""
        try:
            self.client.get_account()
            return True
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Binance connection error: {str(e)}")
            return False
    
    def get_balances(self) -> List[Dict]:
        """Get all non-zero balances"""
        try:
            account = self.client.get_account()
            balances = []
            
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    balances.append({
                        'asset': balance['asset'],
                        'free': free,
                        'locked': locked,
                        'total': total
                    })
            
            return balances
        except Exception as e:
            logger.error(f"Failed to get Binance balances: {str(e)}")
            raise
    
    def get_total_balance_usdt(self) -> float:
        """Get total account balance in USDT equivalent"""
        try:
            balances = self.get_balances()
            total_usdt = 0.0
            
            for balance in balances:
                asset = balance['asset']
                total = balance['total']
                
                if asset == 'USDT':
                    total_usdt += total
                elif asset in ['USDC', 'BUSD', 'USD']:
                    # Stablecoins ~1:1 with USDT
                    total_usdt += total
                else:
                    # Get current price in USDT
                    try:
                        symbol = f"{asset}USDT"
                        ticker = self.client.get_symbol_ticker(symbol=symbol)
                        price = float(ticker['price'])
                        total_usdt += total * price
                    except:
                        # If pair doesn't exist, try with BTC or skip
                        try:
                            btc_symbol = f"{asset}BTC"
                            btc_ticker = self.client.get_symbol_ticker(symbol=btc_symbol)
                            btc_price = float(btc_ticker['price'])
                            
                            btc_usdt_ticker = self.client.get_symbol_ticker(symbol="BTCUSDT")
                            btc_usdt_price = float(btc_usdt_ticker['price'])
                            
                            total_usdt += total * btc_price * btc_usdt_price
                        except:
                            logger.warning(f"Could not convert {asset} to USDT")
            
            return total_usdt
        except Exception as e:
            logger.error(f"Failed to calculate total Binance balance: {str(e)}")
            raise
    
    def get_trades(self, symbol: Optional[str] = None, start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None, limit: int = 1000) -> List[Dict]:
        """Get trade history"""
        try:
            trades = []
            
            if symbol:
                # Get trades for specific symbol
                kwargs = {'symbol': symbol, 'limit': limit}
                
                if start_date:
                    kwargs['startTime'] = int(start_date.timestamp() * 1000)
                if end_date:
                    kwargs['endTime'] = int(end_date.timestamp() * 1000)
                
                symbol_trades = self.client.get_my_trades(**kwargs)
                
                for trade in symbol_trades:
                    trades.append(self._format_trade(trade, symbol))
            else:
                # Get all trades (iterate through all symbols with balances)
                balances = self.get_balances()
                
                for balance in balances:
                    asset = balance['asset']
                    if asset == 'USDT':
                        continue
                    
                    try:
                        symbol_pair = f"{asset}USDT"
                        kwargs = {'symbol': symbol_pair, 'limit': limit}
                        
                        if start_date:
                            kwargs['startTime'] = int(start_date.timestamp() * 1000)
                        if end_date:
                            kwargs['endTime'] = int(end_date.timestamp() * 1000)
                        
                        symbol_trades = self.client.get_my_trades(**kwargs)
                        
                        for trade in symbol_trades:
                            trades.append(self._format_trade(trade, symbol_pair))
                    except:
                        continue
            
            return trades
        except Exception as e:
            logger.error(f"Failed to get Binance trades: {str(e)}")
            raise
    
    def _format_trade(self, trade: Dict, symbol: str) -> Dict:
        """Format trade data"""
        return {
            'exchange_order_id': str(trade['orderId']),
            'symbol': symbol,
            'side': 'buy' if trade['isBuyer'] else 'sell',
            'quantity': float(trade['qty']),
            'price': float(trade['price']),
            'total_amount': float(trade['quoteQty']),
            'fee': float(trade['commission']),
            'fee_currency': trade['commissionAsset'],
            'executed_at': datetime.fromtimestamp(trade['time'] / 1000),
            'status': 'completed'
        }
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()
            
            formatted_orders = []
            for order in orders:
                formatted_orders.append({
                    'order_id': str(order['orderId']),
                    'symbol': order['symbol'],
                    'side': order['side'].lower(),
                    'type': order['type'],
                    'quantity': float(order['origQty']),
                    'price': float(order['price']) if order['price'] else None,
                    'executed_qty': float(order['executedQty']),
                    'status': order['status'].lower(),
                    'created_at': datetime.fromtimestamp(order['time'] / 1000)
                })
            
            return formatted_orders
        except Exception as e:
            logger.error(f"Failed to get Binance open orders: {str(e)}")
            raise

