"""
FXCM REST API Service for real-time market data and trading operations.
Provides WebSocket connections for live data streaming and REST API for historical data.
"""

import asyncio
import json
import logging
import websockets
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import pandas as pd
from ..config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class FXCMCredentials:
    """FXCM API credentials configuration"""
    api_key: str
    access_token: str
    account_id: str
    environment: str = "demo"  # "demo" or "real"
    
    @property
    def base_url(self) -> str:
        """Get base URL based on environment"""
        if self.environment == "demo":
            return "https://api-fxpractice.oanda.com"
        return "https://api-fxtrade.oanda.com"
    
    @property
    def websocket_url(self) -> str:
        """Get WebSocket URL for streaming"""
        if self.environment == "demo":
            return "wss://stream-fxpractice.oanda.com"
        return "wss://stream-fxtrade.oanda.com"


@dataclass
class MarketData:
    """Market data structure"""
    instrument: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime
    volume: Optional[int] = None
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price"""
        return (self.bid + self.ask) / 2


@dataclass
class Candle:
    """OHLCV candlestick data"""
    instrument: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    timeframe: str


@dataclass
class TradeSignal:
    """Trading signal structure"""
    instrument: str
    action: str  # "BUY", "SELL", "CLOSE"
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class FXCMService:
    """FXCM API service for market data and trading operations"""
    
    def __init__(self, credentials: FXCMCredentials):
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.subscribers: Dict[str, List[Callable]] = {
            "price": [],
            "candle": [],
            "trade": []
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection to FXCM API"""
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Test connection
            await self._test_connection()
            self.is_connected = True
            logger.info("Successfully connected to FXCM API")
            
        except Exception as e:
            logger.error(f"Failed to connect to FXCM API: {e}")
            raise
    
    async def disconnect(self):
        """Close connection to FXCM API"""
        try:
            if self.websocket:
                await self.websocket.close()
            
            if self.session:
                await self.session.close()
                
            self.is_connected = False
            logger.info("Disconnected from FXCM API")
            
        except Exception as e:
            logger.error(f"Error disconnecting from FXCM API: {e}")
    
    async def _test_connection(self):
        """Test API connection"""
        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to connect to FXCM API: {response.status}")
            
            data = await response.json()
            logger.info(f"Connected to account: {data.get('account', {}).get('id')}")
    
    async def get_historical_data(
        self, 
        instrument: str, 
        timeframe: str = "M15",
        count: int = 1000,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Candle]:
        """
        Fetch historical candlestick data
        
        Args:
            instrument: Trading instrument (e.g., "EUR_USD")
            timeframe: Timeframe (M1, M5, M15, M30, H1, H4, D)
            count: Number of candles to fetch
            start_time: Start time for data range
            end_time: End time for data range
        """
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        url = f"{self.credentials.base_url}/v3/instruments/{instrument}/candles"
        
        params = {
            "granularity": timeframe,
            "count": count
        }
        
        if start_time:
            params["from"] = start_time.isoformat() + "Z"
        if end_time:
            params["to"] = end_time.isoformat() + "Z"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch historical data: {response.status}")
                
                data = await response.json()
                candles = []
                
                for candle_data in data.get("candles", []):
                    if candle_data["complete"]:
                        candles.append(Candle(
                            instrument=instrument,
                            timestamp=datetime.fromisoformat(candle_data["time"].replace("Z", "+00:00")),
                            open=float(candle_data["mid"]["o"]),
                            high=float(candle_data["mid"]["h"]),
                            low=float(candle_data["mid"]["l"]),
                            close=float(candle_data["mid"]["c"]),
                            volume=int(candle_data["volume"]),
                            timeframe=timeframe
                        ))
                
                logger.info(f"Fetched {len(candles)} candles for {instrument}")
                return candles
                
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
    
    async def get_current_prices(self, instruments: List[str]) -> Dict[str, MarketData]:
        """
        Get current bid/ask prices for instruments
        
        Args:
            instruments: List of trading instruments
        """
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}/pricing"
        
        params = {
            "instruments": ",".join(instruments)
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch current prices: {response.status}")
                
                data = await response.json()
                prices = {}
                
                for price_data in data.get("prices", []):
                    instrument = price_data["instrument"]
                    prices[instrument] = MarketData(
                        instrument=instrument,
                        bid=float(price_data["bids"][0]["price"]),
                        ask=float(price_data["asks"][0]["price"]),
                        spread=float(price_data["asks"][0]["price"]) - float(price_data["bids"][0]["price"]),
                        timestamp=datetime.fromisoformat(price_data["time"].replace("Z", "+00:00"))
                    )
                
                return prices
                
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            raise
    
    async def start_price_stream(self, instruments: List[str]):
        """
        Start real-time price streaming via WebSocket
        
        Args:
            instruments: List of instruments to stream
        """
        try:
            ws_url = f"{self.credentials.websocket_url}/v3/accounts/{self.credentials.account_id}/pricing/stream"
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            params = f"instruments={','.join(instruments)}"
            full_url = f"{ws_url}?{params}"
            
            self.websocket = await websockets.connect(full_url, extra_headers=headers)
            
            logger.info(f"Started price streaming for: {', '.join(instruments)}")
            
            # Listen for incoming messages
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_price_update(data)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse WebSocket message: {message}")
                except Exception as e:
                    logger.error(f"Error handling price update: {e}")
                    
        except Exception as e:
            logger.error(f"Error in price streaming: {e}")
            raise
    
    async def _handle_price_update(self, data: Dict[str, Any]):
        """Handle incoming price updates from WebSocket"""
        if data.get("type") == "PRICE":
            instrument = data.get("instrument")
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            
            if bids and asks:
                market_data = MarketData(
                    instrument=instrument,
                    bid=float(bids[0]["price"]),
                    ask=float(asks[0]["price"]),
                    spread=float(asks[0]["price"]) - float(bids[0]["price"]),
                    timestamp=datetime.fromisoformat(data["time"].replace("Z", "+00:00"))
                )
                
                # Notify all price subscribers
                for callback in self.subscribers["price"]:
                    try:
                        await callback(market_data)
                    except Exception as e:
                        logger.error(f"Error in price callback: {e}")
    
    def subscribe_to_prices(self, callback: Callable[[MarketData], None]):
        """Subscribe to real-time price updates"""
        self.subscribers["price"].append(callback)
    
    def subscribe_to_candles(self, callback: Callable[[Candle], None]):
        """Subscribe to new candle formation"""
        self.subscribers["candle"].append(callback)
    
    def subscribe_to_trades(self, callback: Callable[[Dict], None]):
        """Subscribe to trade execution updates"""
        self.subscribers["trade"].append(callback)
    
    async def place_order(self, signal: TradeSignal) -> Dict[str, Any]:
        """
        Place a trading order based on signal
        
        Args:
            signal: Trading signal with order details
        """
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}/orders"
        
        # Convert signal to FXCM order format
        order_data = {
            "order": {
                "instrument": signal.instrument,
                "units": int(signal.volume * 10000) if signal.action == "BUY" else -int(signal.volume * 10000),
                "type": "MARKET",
                "timeInForce": "FOK"
            }
        }
        
        # Add stop loss if specified
        if signal.stop_loss:
            order_data["order"]["stopLossOnFill"] = {
                "price": str(signal.stop_loss)
            }
        
        # Add take profit if specified
        if signal.take_profit:
            order_data["order"]["takeProfitOnFill"] = {
                "price": str(signal.take_profit)
            }
        
        try:
            async with self.session.post(url, json=order_data) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Failed to place order: {response.status} - {error_text}")
                
                result = await response.json()
                logger.info(f"Order placed successfully: {result}")
                
                # Notify trade subscribers
                for callback in self.subscribers["trade"]:
                    try:
                        await callback(result)
                    except Exception as e:
                        logger.error(f"Error in trade callback: {e}")
                
                return result
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information and balance"""
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}"
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch account info: {response.status}")
                
                data = await response.json()
                return data.get("account", {})
                
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise
    
    async def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}/positions"
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch positions: {response.status}")
                
                data = await response.json()
                return data.get("positions", [])
                
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
    
    def to_dataframe(self, candles: List[Candle]) -> pd.DataFrame:
        """Convert candles to pandas DataFrame for analysis"""
        data = []
        for candle in candles:
            data.append({
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume
            })
        
        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)
        return df


# Factory function for creating FXCM service
async def create_fxcm_service() -> FXCMService:
    """Create and initialize FXCM service"""
    credentials = FXCMCredentials(
        api_key=settings.FXCM_API_KEY,
        access_token=settings.FXCM_ACCESS_TOKEN,
        account_id=settings.FXCM_ACCOUNT_ID,
        environment=settings.FXCM_ENVIRONMENT
    )
    
    service = FXCMService(credentials)
    await service.connect()
    return service
