"""
FXCM Data Provider - Real-time and historical forex data
Handles connection to FXCM's REST API and WebSocket feeds
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import websockets
import json
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FXCMConfig:
    """FXCM configuration settings"""
    access_token: str
    environment: str = "demo"  # "demo" or "real"
    server_url: str = "https://api-fxpractice.fxcm.com"
    socket_url: str = "wss://api-fxpractice.fxcm.com/socket.io/"
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit_delay: float = 0.1

class FXCMDataProvider:
    """
    FXCM Data Provider for real-time and historical market data
    Optimized for trading signal generation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = FXCMConfig(**config)
        self.session = None
        self.websocket = None
        self.is_connected = False
        self.subscriptions = {}
        self.data_cache = {}
        self.last_request_time = 0
        
        # Symbol mapping (FXCM format to standard format)
        self.symbol_map = {
            'EURUSD': 'EUR/USD',
            'GBPUSD': 'GBP/USD', 
            'USDJPY': 'USD/JPY',
            'USDCHF': 'USD/CHF',
            'AUDUSD': 'AUD/USD',
            'USDCAD': 'USD/CAD',
            'NZDUSD': 'NZD/USD',
            'EURGBP': 'EUR/GBP',
            'EURJPY': 'EUR/JPY',
            'GBPJPY': 'GBP/JPY'
        }
        
        # Timeframe mapping
        self.timeframe_map = {
            'M1': 'm1',
            'M5': 'm5', 
            'M15': 'm15',
            'M30': 'm30',
            'H1': 'H1',
            'H4': 'H4',
            'D1': 'D1',
            'W1': 'W1'
        }
        
        logger.info(f"FXCM Data Provider initialized for {self.config.environment} environment")
    
    async def connect(self) -> bool:
        """Establish connection to FXCM API"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test authentication
            if await self._authenticate():
                self.is_connected = True
                logger.info("Successfully connected to FXCM API")
                return True
            else:
                logger.error("Failed to authenticate with FXCM API")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to FXCM: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from FXCM API"""
        try:
            if self.websocket:
                await self.websocket.close()
            
            if self.session:
                await self.session.close()
            
            self.is_connected = False
            logger.info("Disconnected from FXCM API")
            
        except Exception as e:
            logger.error(f"Error disconnecting from FXCM: {e}")
    
    async def _authenticate(self) -> bool:
        """Authenticate with FXCM API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.config.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.config.server_url}/trading/get_model"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("FXCM authentication successful")
                    return True
                else:
                    logger.error(f"FXCM authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error during FXCM authentication: {e}")
            return False
    
    async def _rate_limit(self):
        """Implement rate limiting to avoid API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.config.rate_limit_delay:
            await asyncio.sleep(self.config.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        periods: int = 100,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Get historical market data from FXCM
        
        Args:
            symbol: Currency pair (e.g., 'EURUSD')
            timeframe: Timeframe (e.g., 'H1', 'M15')
            periods: Number of periods to retrieve
            end_time: End time for historical data
        
        Returns:
            DataFrame with OHLCV data
        """
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        await self._rate_limit()
        
        try:
            # Convert symbol and timeframe to FXCM format
            fxcm_symbol = self.symbol_map.get(symbol, symbol)
            fxcm_timeframe = self.timeframe_map.get(timeframe, timeframe)
            
            # Prepare parameters
            params = {
                'instrument': fxcm_symbol,
                'periodicity': fxcm_timeframe,
                'num': periods
            }
            
            if end_time:
                params['end'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
            
            headers = {
                'Authorization': f'Bearer {self.config.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.config.server_url}/candles"
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_historical_data(data, symbol)
                else:
                    error_text = await response.text()
                    logger.error(f"Error getting historical data for {symbol}: {response.status} - {error_text}")
                    raise Exception(f"API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol} {timeframe}: {e}")
            
            # Return cached data if available
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.data_cache:
                logger.warning(f"Returning cached data for {symbol} {timeframe}")
                return self.data_cache[cache_key]
            
            # Return empty DataFrame if no cached data
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    def _process_historical_data(self, raw_data: Dict, symbol: str) -> pd.DataFrame:
        """Process raw FXCM data into standardized DataFrame"""
        try:
            if 'candles' not in raw_data or not raw_data['candles']:
                logger.warning(f"No candle data received for {symbol}")
                return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            candles = raw_data['candles']
            
            # Extract data
            data = []
            for candle in candles:
                data.append({
                    'timestamp': pd.to_datetime(candle['timestamp']),
                    'open': float(candle['bidopen']),
                    'high': float(candle['bidhigh']),
                    'low': float(candle['bidlow']),
                    'close': float(candle['bidclose']),
                    'volume': float(candle.get('tickqty', 0))
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            # Cache the data
            cache_key = f"{symbol}_{len(df)}"
            self.data_cache[cache_key] = df.copy()
            
            logger.debug(f"Processed {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error processing historical data for {symbol}: {e}")
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    async def get_current_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get current bid/ask prices for a symbol"""
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        await self._rate_limit()
        
        try:
            fxcm_symbol = self.symbol_map.get(symbol, symbol)
            
            headers = {
                'Authorization': f'Bearer {self.config.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.config.server_url}/trading/get_instruments"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Find the symbol in the instruments list
                    for instrument in data.get('instruments', []):
                        if instrument.get('instrument') == fxcm_symbol:
                            return {
                                'bid': float(instrument.get('bid', 0)),
                                'ask': float(instrument.get('ask', 0)),
                                'spread': float(instrument.get('spread', 0)),
                                'timestamp': datetime.now()
                            }
                    
                    logger.warning(f"Symbol {symbol} not found in instruments")
                    return None
                else:
                    logger.error(f"Error getting current price for {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    async def get_market_status(self) -> Dict[str, Any]:
        """Get current market status and trading hours"""
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.config.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.config.server_url}/trading/get_model"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'market_open': data.get('isTradingAllowed', False),
                        'server_time': data.get('serverTime', datetime.now().isoformat()),
                        'equity': data.get('equity', 0),
                        'balance': data.get('balance', 0),
                        'margin_available': data.get('marginAvailable', 0)
                    }
                else:
                    logger.error(f"Error getting market status: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {}
    
    async def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.config.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.config.server_url}/trading/get_instruments"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    symbols = []
                    
                    for instrument in data.get('instruments', []):
                        fxcm_symbol = instrument.get('instrument', '')
                        # Convert back to standard format
                        standard_symbol = None
                        for std, fxcm in self.symbol_map.items():
                            if fxcm == fxcm_symbol:
                                standard_symbol = std
                                break
                        
                        if standard_symbol:
                            symbols.append(standard_symbol)
                        else:
                            symbols.append(fxcm_symbol.replace('/', ''))
                    
                    return symbols
                else:
                    logger.error(f"Error getting available symbols: {response.status}")
                    return list(self.symbol_map.keys())
                    
        except Exception as e:
            logger.error(f"Error getting available symbols: {e}")
            return list(self.symbol_map.keys())
    
    async def subscribe_to_price_updates(self, symbols: List[str], callback=None):
        """Subscribe to real-time price updates via WebSocket"""
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        try:
            # This would implement WebSocket subscription for real-time data
            # FXCM's WebSocket implementation varies, so this is a simplified version
            logger.info(f"Subscribing to price updates for: {symbols}")
            
            for symbol in symbols:
                self.subscriptions[symbol] = {
                    'callback': callback,
                    'last_update': datetime.now()
                }
            
            logger.info(f"Subscribed to {len(symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error subscribing to price updates: {e}")
    
    async def unsubscribe_from_price_updates(self, symbols: List[str]):
        """Unsubscribe from real-time price updates"""
        try:
            for symbol in symbols:
                if symbol in self.subscriptions:
                    del self.subscriptions[symbol]
            
            logger.info(f"Unsubscribed from {len(symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error unsubscribing from price updates: {e}")
    
    async def get_account_summary(self) -> Dict[str, Any]:
        """Get account summary information"""
        if not self.is_connected:
            raise Exception("Not connected to FXCM API")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.config.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.config.server_url}/trading/get_model"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'account_id': data.get('accountId', ''),
                        'balance': float(data.get('balance', 0)),
                        'equity': float(data.get('equity', 0)),
                        'margin_used': float(data.get('usableMargin', 0)),
                        'margin_available': float(data.get('marginAvailable', 0)),
                        'currency': data.get('accountCurrency', 'USD'),
                        'leverage': data.get('leverage', 1),
                        'is_trading_allowed': data.get('isTradingAllowed', False)
                    }
                else:
                    logger.error(f"Error getting account summary: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {}
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            'connected': self.is_connected,
            'environment': self.config.environment,
            'server_url': self.config.server_url,
            'last_request_time': self.last_request_time,
            'cached_symbols': len(self.data_cache),
            'active_subscriptions': len(self.subscriptions)
        }
    
    async def test_connection(self) -> bool:
        """Test the connection to FXCM API"""
        try:
            if not self.is_connected:
                return False
            
            # Try to get account summary as a connection test
            account_data = await self.get_account_summary()
            return bool(account_data)
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# Alternative data provider for when FXCM is not available
class MockFXCMProvider(FXCMDataProvider):
    """Mock FXCM provider for testing and development"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.is_connected = True
        logger.info("Mock FXCM Provider initialized")
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info("Mock FXCM connection established")
        return True
    
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        periods: int = 100,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Generate mock historical data"""
        
        # Generate realistic forex data
        np.random.seed(42)  # For reproducible data
        
        end_time = end_time or datetime.now()
        
        # Calculate time intervals based on timeframe
        if timeframe == 'M1':
            delta = timedelta(minutes=1)
        elif timeframe == 'M5':
            delta = timedelta(minutes=5)
        elif timeframe == 'M15':
            delta = timedelta(minutes=15)
        elif timeframe == 'H1':
            delta = timedelta(hours=1)
        elif timeframe == 'H4':
            delta = timedelta(hours=4)
        else:  # D1
            delta = timedelta(days=1)
        
        # Generate timestamps
        timestamps = [end_time - delta * i for i in range(periods)]
        timestamps.reverse()
        
        # Generate price data (starting around typical forex rates)
        base_prices = {
            'EURUSD': 1.1000,
            'GBPUSD': 1.3000,
            'USDJPY': 110.00,
            'USDCHF': 0.9200,
            'AUDUSD': 0.7500,
            'USDCAD': 1.2500,
            'NZDUSD': 0.7000
        }
        
        base_price = base_prices.get(symbol, 1.0000)
        
        # Generate realistic price movements
        returns = np.random.normal(0, 0.001, periods)  # 0.1% daily volatility
        prices = [base_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)
        
        # Generate OHLC data
        data = []
        for i, timestamp in enumerate(timestamps):
            price = prices[i]
            volatility = abs(np.random.normal(0, 0.0005))  # Random volatility
            
            high = price * (1 + volatility)
            low = price * (1 - volatility)
            open_price = price * (1 + np.random.normal(0, 0.0002))
            
            data.append({
                'timestamp': timestamp,
                'open': round(open_price, 5),
                'high': round(high, 5),
                'low': round(low, 5),
                'close': round(price, 5),
                'volume': np.random.randint(100, 1000)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        return df
    
    async def get_current_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get mock current price"""
        base_prices = {
            'EURUSD': 1.1000,
            'GBPUSD': 1.3000,
            'USDJPY': 110.00,
            'USDCHF': 0.9200,
            'AUDUSD': 0.7500,
            'USDCAD': 1.2500,
            'NZDUSD': 0.7000
        }
        
        base_price = base_prices.get(symbol, 1.0000)
        spread = base_price * 0.00002  # 2 pip spread
        
        return {
            'bid': round(base_price - spread/2, 5),
            'ask': round(base_price + spread/2, 5),
            'spread': round(spread, 5),
            'timestamp': datetime.now()
        }