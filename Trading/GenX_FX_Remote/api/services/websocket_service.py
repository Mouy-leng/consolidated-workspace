"""
Enhanced WebSocket Service for GenX Trading Platform
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, List, Optional, Callable
import os
from datetime import datetime
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    bid: float = None
    ask: float = None
    high_24h: float = None
    low_24h: float = None
    change_24h: float = None

class WebSocketService:
    """Enhanced WebSocket service for real-time market data"""
    
    def __init__(self):
        self.connections = {}
        self.subscribers = {}
        self.running = False
        self.reconnect_interval = int(os.getenv("WEBSOCKET_RECONNECT_INTERVAL", "5"))
        self.max_retries = int(os.getenv("MAX_WEBSOCKET_RETRIES", "10"))
        
        # Exchange endpoints
        self.exchanges = {
            'bybit': {
                'url': 'wss://stream.bybit.com/v5/public/spot',
                'subscribe_format': self._bybit_subscribe_format,
                'parser': self._parse_bybit_data
            },
            'binance': {
                'url': 'wss://stream.binance.com:9443/ws/',
                'subscribe_format': self._binance_subscribe_format,
                'parser': self._parse_binance_data
            },
            'coinbase': {
                'url': 'wss://ws-feed.pro.coinbase.com',
                'subscribe_format': self._coinbase_subscribe_format,
                'parser': self._parse_coinbase_data
            }
        }
        
        # Data callbacks
        self.data_callbacks = []
        
    async def initialize(self):
        """Initialize WebSocket service"""
        try:
            logger.info("Initializing WebSocket service...")
            self.running = True
            
            # Start connection tasks for each exchange
            for exchange_name in self.exchanges.keys():
                asyncio.create_task(self._maintain_connection(exchange_name))
            
            logger.info("WebSocket service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket service: {e}")
            return False
    
    async def subscribe_to_symbol(self, exchange: str, symbol: str, callback: Callable = None):
        """Subscribe to real-time data for a symbol"""
        try:
            if exchange not in self.exchanges:
                raise ValueError(f"Unsupported exchange: {exchange}")
            
            if exchange not in self.subscribers:
                self.subscribers[exchange] = set()
            
            self.subscribers[exchange].add(symbol)
            
            if callback:
                self.data_callbacks.append(callback)
            
            # Send subscription message if connection exists
            if exchange in self.connections:
                await self._send_subscription(exchange, symbol)
            
            logger.info(f"Subscribed to {symbol} on {exchange}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to {symbol} on {exchange}: {e}")
    
    async def unsubscribe_from_symbol(self, exchange: str, symbol: str):
        """Unsubscribe from a symbol"""
        try:
            if exchange in self.subscribers:
                self.subscribers[exchange].discard(symbol)
            
            # Send unsubscription message if connection exists
            if exchange in self.connections:
                await self._send_unsubscription(exchange, symbol)
            
            logger.info(f"Unsubscribed from {symbol} on {exchange}")
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {symbol} on {exchange}: {e}")
    
    def add_data_callback(self, callback: Callable):
        """Add a callback for market data updates"""
        self.data_callbacks.append(callback)
    
    async def _maintain_connection(self, exchange: str):
        """Maintain WebSocket connection for an exchange"""
        retry_count = 0
        
        while self.running and retry_count < self.max_retries:
            try:
                exchange_config = self.exchanges[exchange]
                
                async with websockets.connect(exchange_config['url']) as websocket:
                    self.connections[exchange] = websocket
                    retry_count = 0  # Reset retry count on successful connection
                    
                    logger.info(f"Connected to {exchange} WebSocket")
                    
                    # Subscribe to existing symbols
                    if exchange in self.subscribers:
                        for symbol in self.subscribers[exchange]:
                            await self._send_subscription(exchange, symbol)
                    
                    # Listen for messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            market_data = exchange_config['parser'](data)
                            
                            if market_data:
                                # Call all registered callbacks
                                for callback in self.data_callbacks:
                                    try:
                                        await callback(market_data)
                                    except Exception as e:
                                        logger.error(f"Callback error: {e}")
                                        
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON from {exchange}: {message}")
                        except Exception as e:
                            logger.error(f"Message processing error for {exchange}: {e}")
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Connection to {exchange} closed")
            except Exception as e:
                logger.error(f"Connection error for {exchange}: {e}")
                retry_count += 1
                
            # Remove connection reference
            if exchange in self.connections:
                del self.connections[exchange]
                
            if self.running and retry_count < self.max_retries:
                logger.info(f"Reconnecting to {exchange} in {self.reconnect_interval} seconds...")
                await asyncio.sleep(self.reconnect_interval)
        
        if retry_count >= self.max_retries:
            logger.error(f"Max retries exceeded for {exchange}")
    
    async def _send_subscription(self, exchange: str, symbol: str):
        """Send subscription message to exchange"""
        try:
            websocket = self.connections.get(exchange)
            if not websocket:
                return
            
            exchange_config = self.exchanges[exchange]
            subscribe_msg = exchange_config['subscribe_format'](symbol)
            
            await websocket.send(json.dumps(subscribe_msg))
            logger.debug(f"Sent subscription for {symbol} to {exchange}")
            
        except Exception as e:
            logger.error(f"Failed to send subscription for {symbol} to {exchange}: {e}")
    
    async def _send_unsubscription(self, exchange: str, symbol: str):
        """Send unsubscription message to exchange"""
        try:
            websocket = self.connections.get(exchange)
            if not websocket:
                return
            
            exchange_config = self.exchanges[exchange]
            # Most exchanges use similar format for unsubscribe
            unsubscribe_msg = exchange_config['subscribe_format'](symbol)
            unsubscribe_msg['op'] = 'unsubscribe'  # Modify to unsubscribe
            
            await websocket.send(json.dumps(unsubscribe_msg))
            logger.debug(f"Sent unsubscription for {symbol} to {exchange}")
            
        except Exception as e:
            logger.error(f"Failed to send unsubscription for {symbol} to {exchange}: {e}")
    
    def _bybit_subscribe_format(self, symbol: str) -> Dict[str, Any]:
        """Format subscription message for Bybit"""
        return {
            "op": "subscribe",
            "args": [f"publicTrade.{symbol}"]
        }
    
    def _binance_subscribe_format(self, symbol: str) -> Dict[str, Any]:
        """Format subscription message for Binance"""
        return {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@trade"],
            "id": 1
        }
    
    def _coinbase_subscribe_format(self, symbol: str) -> Dict[str, Any]:
        """Format subscription message for Coinbase"""
        return {
            "type": "subscribe",
            "product_ids": [symbol],
            "channels": ["matches"]
        }
    
    def _parse_bybit_data(self, data: Dict[str, Any]) -> Optional[MarketData]:
        """Parse Bybit WebSocket data"""
        try:
            if data.get('topic', '').startswith('publicTrade'):
                trade_data = data.get('data', [])
                if trade_data:
                    trade = trade_data[0]
                    return MarketData(
                        symbol=trade['s'],
                        price=float(trade['p']),
                        volume=float(trade['v']),
                        timestamp=datetime.fromtimestamp(int(trade['T']) / 1000)
                    )
        except Exception as e:
            logger.error(f"Failed to parse Bybit data: {e}")
        return None
    
    def _parse_binance_data(self, data: Dict[str, Any]) -> Optional[MarketData]:
        """Parse Binance WebSocket data"""
        try:
            if 'e' in data and data['e'] == 'trade':
                return MarketData(
                    symbol=data['s'],
                    price=float(data['p']),
                    volume=float(data['q']),
                    timestamp=datetime.fromtimestamp(int(data['T']) / 1000)
                )
        except Exception as e:
            logger.error(f"Failed to parse Binance data: {e}")
        return None
    
    def _parse_coinbase_data(self, data: Dict[str, Any]) -> Optional[MarketData]:
        """Parse Coinbase WebSocket data"""
        try:
            if data.get('type') == 'match':
                return MarketData(
                    symbol=data['product_id'],
                    price=float(data['price']),
                    volume=float(data['size']),
                    timestamp=datetime.fromisoformat(data['time'].replace('Z', '+00:00'))
                )
        except Exception as e:
            logger.error(f"Failed to parse Coinbase data: {e}")
        return None
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all connections"""
        status = {}
        
        for exchange in self.exchanges.keys():
            is_connected = exchange in self.connections
            subscribed_symbols = list(self.subscribers.get(exchange, set()))
            
            status[exchange] = {
                'connected': is_connected,
                'subscribed_symbols': subscribed_symbols,
                'subscriber_count': len(subscribed_symbols)
            }
        
        return {
            'exchanges': status,
            'total_connections': len(self.connections),
            'total_callbacks': len(self.data_callbacks),
            'running': self.running
        }
    
    async def health_check(self) -> bool:
        """Check if WebSocket service is healthy"""
        try:
            # Check if at least one connection is active
            return len(self.connections) > 0 and self.running
        except Exception as e:
            logger.error(f"WebSocket health check failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown WebSocket service"""
        logger.info("Shutting down WebSocket service...")
        self.running = False
        
        # Close all connections
        for exchange, websocket in self.connections.items():
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing {exchange} connection: {e}")
        
        self.connections.clear()
        self.subscribers.clear()
        self.data_callbacks.clear()
        
        logger.info("WebSocket service shutdown complete")
