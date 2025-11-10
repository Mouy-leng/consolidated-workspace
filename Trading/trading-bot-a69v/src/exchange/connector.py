"""
Exchange Connector Module
Handles connections to cryptocurrency exchanges via CCXT
"""
import ccxt
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ExchangeConnector:
    """Manages exchange connections and operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.exchange = None
        self.exchange_id = config.get('exchange_id', 'binance')
        self.testnet = config.get('testnet', True)
        
    async def initialize(self):
        """Initialize exchange connection"""
        try:
            # Get exchange class
            exchange_class = getattr(ccxt, self.exchange_id)
            
            # Configure exchange
            exchange_config = {
                'apiKey': self.config.get('api_key'),
                'secret': self.config.get('api_secret'),
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            }
            
            # Set testnet if enabled
            if self.testnet:
                exchange_config['options']['testnet'] = True
                if self.exchange_id == 'binance':
                    exchange_config['urls'] = {
                        'api': {
                            'public': 'https://testnet.binance.vision/api',
                            'private': 'https://testnet.binance.vision/api',
                        }
                    }
            
            self.exchange = exchange_class(exchange_config)
            
            # Load markets
            await self.exchange.load_markets()
            
            logger.info(f"Connected to {self.exchange_id} (testnet={self.testnet})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}", exc_info=True)
            return False
            
    async def get_balance(self, currency: Optional[str] = None) -> Dict[str, Any]:
        """Get account balance"""
        try:
            balance = await self.exchange.fetch_balance()
            
            if currency:
                return {
                    'currency': currency,
                    'free': balance.get(currency, {}).get('free', 0),
                    'used': balance.get(currency, {}).get('used', 0),
                    'total': balance.get(currency, {}).get('total', 0)
                }
            
            return balance
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}", exc_info=True)
            return {}
            
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker data"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'last': ticker.get('last'),
                'volume': ticker.get('volume'),
                'timestamp': ticker.get('timestamp')
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}", exc_info=True)
            return {}
            
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get orderbook"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit)
            return {
                'symbol': symbol,
                'bids': orderbook.get('bids', []),
                'asks': orderbook.get('asks', []),
                'timestamp': orderbook.get('timestamp')
            }
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}", exc_info=True)
            return {}
            
    async def get_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> List:
        """Get OHLCV candlestick data"""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}", exc_info=True)
            return []
            
    async def create_market_order(self, symbol: str, side: str, amount: float) -> Dict[str, Any]:
        """Create market order"""
        try:
            logger.info(f"Creating MARKET {side} order: {amount} {symbol}")
            
            order = await self.exchange.create_market_order(symbol, side, amount)
            
            logger.info(f"Order created: {order.get('id')} - Status: {order.get('status')}")
            
            return {
                'id': order.get('id'),
                'symbol': order.get('symbol'),
                'type': order.get('type'),
                'side': order.get('side'),
                'amount': order.get('amount'),
                'price': order.get('price'),
                'status': order.get('status'),
                'timestamp': order.get('timestamp'),
                'filled': order.get('filled'),
                'remaining': order.get('remaining')
            }
            
        except Exception as e:
            logger.error(f"Error creating market order: {e}", exc_info=True)
            return {'error': str(e)}
            
    async def create_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Dict[str, Any]:
        """Create limit order"""
        try:
            logger.info(f"Creating LIMIT {side} order: {amount} {symbol} @ {price}")
            
            order = await self.exchange.create_limit_order(symbol, side, amount, price)
            
            logger.info(f"Order created: {order.get('id')} - Status: {order.get('status')}")
            
            return {
                'id': order.get('id'),
                'symbol': order.get('symbol'),
                'type': order.get('type'),
                'side': order.get('side'),
                'amount': order.get('amount'),
                'price': order.get('price'),
                'status': order.get('status'),
                'timestamp': order.get('timestamp'),
                'filled': order.get('filled'),
                'remaining': order.get('remaining')
            }
            
        except Exception as e:
            logger.error(f"Error creating limit order: {e}", exc_info=True)
            return {'error': str(e)}
            
    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            result = await self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order {order_id} cancelled")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}", exc_info=True)
            return {'error': str(e)}
            
    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        try:
            order = await self.exchange.fetch_order(order_id, symbol)
            return {
                'id': order.get('id'),
                'status': order.get('status'),
                'filled': order.get('filled'),
                'remaining': order.get('remaining'),
                'price': order.get('price'),
                'average': order.get('average')
            }
        except Exception as e:
            logger.error(f"Error fetching order status: {e}", exc_info=True)
            return {'error': str(e)}
            
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        try:
            orders = await self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}", exc_info=True)
            return []
            
    async def close(self):
        """Close exchange connection"""
        if self.exchange:
            await self.exchange.close()
            logger.info("Exchange connection closed")
