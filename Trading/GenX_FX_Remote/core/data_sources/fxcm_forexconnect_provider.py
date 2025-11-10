"""
FXCM ForexConnect Provider - Real-time and historical forex data using ForexConnect API
Direct integration with FXCM's ForexConnect trading platform
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import json
import time
from dataclasses import dataclass
import os
import sys

# Import ForexConnect (ensure virtual environment is activated)
try:
    import forexconnect as fx
    FOREXCONNECT_AVAILABLE = True
except ImportError:
    FOREXCONNECT_AVAILABLE = False
    logging.warning("ForexConnect module not available. Install with: pip install forexconnect")

logger = logging.getLogger(__name__)

@dataclass
class FXCMForexConnectConfig:
    """FXCM ForexConnect configuration settings"""
    username: str
    password: str
    connection_type: str = "Demo"  # "Demo" or "Real"
    url: str = "http://fxcorporate.com/Hosts.jsp"
    session_id: Optional[str] = None
    pin: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    auto_reconnect: bool = True

class FXCMForexConnectProvider:
    """
    FXCM ForexConnect Provider for real-time and historical market data
    Uses FXCM's native ForexConnect API for direct platform integration
    """
    
    def __init__(self, config: Dict[str, Any]):
        if not FOREXCONNECT_AVAILABLE:
            raise ImportError("ForexConnect module not available. Please install it first.")
            
        self.config = FXCMForexConnectConfig(**config)
        self.forex_connect = None
        self.session = None
        self.is_connected = False
        self.last_error = None
        
        # Data caching
        self.price_cache = {}
        self.historical_cache = {}
        self.account_info = None
        
        # Symbol mapping (standard to FXCM format)
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
        
        # Timeframe mapping for historical data
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
        
        logger.info(f"FXCM ForexConnect Provider initialized for {self.config.connection_type} environment")
    
    async def connect(self) -> bool:
        """Establish connection to FXCM using ForexConnect API"""
        try:
            if not FOREXCONNECT_AVAILABLE:
                logger.error("ForexConnect module not available")
                return False
                
            logger.info("Connecting to FXCM ForexConnect...")
            
            # Create ForexConnect instance
            self.forex_connect = fx.ForexConnect()
            
            # Attempt login
            self.session = self.forex_connect.login(
                user_id=self.config.username,
                password=self.config.password,
                url=self.config.url,
                connection=self.config.connection_type,
                session_id=self.config.session_id,
                pin=self.config.pin
            )
            
            if self.session:
                self.is_connected = True
                logger.info("Successfully connected to FXCM ForexConnect")
                
                # Load account information
                await self._load_account_info()
                
                return True
            else:
                logger.error("Failed to connect to FXCM ForexConnect")
                return False
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error connecting to FXCM ForexConnect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from FXCM ForexConnect"""
        try:
            if self.session:
                self.session.logout()
                logger.info("Disconnected from FXCM ForexConnect")
            
            self.is_connected = False
            self.session = None
            self.forex_connect = None
            
        except Exception as e:
            logger.error(f"Error disconnecting from FXCM: {e}")
    
    async def _load_account_info(self):
        """Load account information"""
        try:
            if not self.is_connected:
                return None
                
            accounts_table = self.forex_connect.get_table(self.forex_connect.ACCOUNTS)
            
            if accounts_table and accounts_table.size() > 0:
                account = accounts_table.get_row(0)
                self.account_info = {
                    'account_id': account.account_id,
                    'balance': float(account.balance),
                    'currency': account.account_currency,
                    'equity': float(getattr(account, 'equity', account.balance)),
                    'margin': float(getattr(account, 'used_margin', 0)),
                    'free_margin': float(getattr(account, 'usable_margin', account.balance))
                }
                
                logger.info(f"Account loaded: {self.account_info['account_id']} - "
                          f"Balance: {self.account_info['balance']} {self.account_info['currency']}")
                
                return self.account_info
            else:
                logger.warning("No account information available")
                return None
                
        except Exception as e:
            logger.error(f"Error loading account info: {e}")
            return None
    
    async def get_live_prices(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """Get live prices for specified symbols"""
        try:
            if not self.is_connected:
                logger.warning("Not connected to FXCM")
                return {}
            
            prices = {}
            offers_table = self.forex_connect.get_table(self.forex_connect.OFFERS)
            
            if not offers_table:
                logger.warning("No offers table available")
                return {}
            
            # Get prices for all requested symbols
            for symbol in symbols:
                fxcm_symbol = self.symbol_map.get(symbol, symbol)
                
                # Find the symbol in offers table
                for i in range(offers_table.size()):
                    offer = offers_table.get_row(i)
                    if offer.instrument == fxcm_symbol:
                        prices[symbol] = {
                            'bid': float(offer.bid),
                            'ask': float(offer.ask),
                            'spread': float(offer.ask - offer.bid),
                            'timestamp': datetime.now(),
                            'symbol': symbol
                        }
                        break
            
            # Update cache
            self.price_cache.update(prices)
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting live prices: {e}")
            return {}
    
    async def get_historical_data(self, symbol: str, timeframe: str, 
                                count: int = 1000, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Get historical price data"""
        try:
            if not self.is_connected:
                logger.warning("Not connected to FXCM")
                return pd.DataFrame()
            
            fxcm_symbol = self.symbol_map.get(symbol, symbol)
            fxcm_timeframe = self.timeframe_map.get(timeframe, timeframe)
            
            # Get historical data from ForexConnect
            history = self.forex_connect.get_history(
                instrument=fxcm_symbol,
                timeframe=fxcm_timeframe,
                count=count
            )
            
            if not history or len(history) == 0:
                logger.warning(f"No historical data for {symbol} {timeframe}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for bar in history:
                data.append({
                    'timestamp': bar.date,
                    'open': float(bar.open),
                    'high': float(bar.high),
                    'low': float(bar.low),
                    'close': float(bar.close),
                    'volume': int(getattr(bar, 'volume', 0))
                })
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            # Cache the data
            cache_key = f"{symbol}_{timeframe}_{count}"
            self.historical_cache[cache_key] = df
            
            logger.info(f"Retrieved {len(df)} historical bars for {symbol} {timeframe}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_account_summary(self) -> Dict[str, Any]:
        """Get account summary information"""
        try:
            if not self.is_connected:
                return {}
            
            if not self.account_info:
                await self._load_account_info()
            
            # Get current positions
            trades_table = self.forex_connect.get_table(self.forex_connect.TRADES)
            positions = []
            
            if trades_table:
                for i in range(trades_table.size()):
                    trade = trades_table.get_row(i)
                    positions.append({
                        'symbol': trade.instrument,
                        'side': 'buy' if trade.buy_sell == 'B' else 'sell',
                        'amount': float(trade.amount),
                        'open_price': float(trade.open_rate),
                        'current_price': float(trade.close),
                        'pl': float(trade.pl),
                        'trade_id': trade.trade_id
                    })
            
            return {
                'account_info': self.account_info or {},
                'positions': positions,
                'total_positions': len(positions),
                'total_pl': sum(pos['pl'] for pos in positions),
                'connection_status': 'connected' if self.is_connected else 'disconnected',
                'last_update': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check if connection is healthy"""
        try:
            if not self.is_connected or not self.session:
                return False
            
            # Try to get a simple table to test connection
            offers_table = self.forex_connect.get_table(self.forex_connect.OFFERS)
            return offers_table is not None
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported symbols"""
        return list(self.symbol_map.keys())
    
    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes"""
        return list(self.timeframe_map.keys())


class MockFXCMForexConnectProvider(FXCMForexConnectProvider):
    """
    Mock FXCM ForexConnect Provider for testing and development
    Simulates real FXCM data without requiring valid credentials
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Don't call parent __init__ to avoid ForexConnect dependency
        self.config = FXCMForexConnectConfig(**config)
        self.forex_connect = None
        self.session = None
        self.is_connected = False
        self.last_error = None
        
        # Mock data
        self.price_cache = {}
        self.historical_cache = {}
        self.account_info = {
            'account_id': 'MOCK123456',
            'balance': 50000.0,
            'currency': 'USD',
            'equity': 50000.0,
            'margin': 0.0,
            'free_margin': 50000.0
        }
        
        # Same mappings as real provider
        self.symbol_map = {
            'EURUSD': 'EUR/USD',
            'GBPUSD': 'GBP/USD', 
            'USDJPY': 'USD/JPY',
            'USDCHF': 'USD/CHF',
            'AUDUSD': 'AUD/USD',
            'USDCAD': 'USD/CAD',
            'NZDUSD': 'NZD/USD'
        }
        
        self.timeframe_map = {
            'M1': 'm1', 'M5': 'm5', 'M15': 'm15', 'M30': 'm30',
            'H1': 'H1', 'H4': 'H4', 'D1': 'D1', 'W1': 'W1'
        }
        
        logger.info("Mock FXCM ForexConnect Provider initialized")
    
    async def connect(self) -> bool:
        """Mock connection - always succeeds"""
        self.is_connected = True
        logger.info("Mock FXCM ForexConnect connected successfully")
        return True
    
    async def disconnect(self):
        """Mock disconnect"""
        self.is_connected = False
        logger.info("Mock FXCM ForexConnect disconnected")
    
    async def get_live_prices(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """Generate mock live prices"""
        import random
        
        prices = {}
        base_prices = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 148.50,
            'USDCHF': 0.8950, 'AUDUSD': 0.6580, 'USDCAD': 1.3620, 'NZDUSD': 0.6120
        }
        
        for symbol in symbols:
            if symbol in base_prices:
                base_price = base_prices[symbol]
                spread = 0.0002 if 'JPY' not in symbol else 0.02
                
                # Add some random variation
                variation = random.uniform(-0.001, 0.001)
                mid_price = base_price + variation
                
                prices[symbol] = {
                    'bid': round(mid_price - spread/2, 5),
                    'ask': round(mid_price + spread/2, 5),
                    'spread': spread,
                    'timestamp': datetime.now(),
                    'symbol': symbol
                }
        
        self.price_cache.update(prices)
        return prices
    
    async def get_historical_data(self, symbol: str, timeframe: str, 
                                count: int = 1000, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Generate mock historical data"""
        import random
        
        base_prices = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 148.50,
            'USDCHF': 0.8950, 'AUDUSD': 0.6580, 'USDCAD': 1.3620, 'NZDUSD': 0.6120
        }
        
        if symbol not in base_prices:
            return pd.DataFrame()
        
        # Generate mock data
        data = []
        current_price = base_prices[symbol]
        current_time = datetime.now() - timedelta(minutes=count)
        
        for i in range(count):
            # Random walk
            change = random.gauss(0, 0.001)
            current_price += change
            
            # Generate OHLC
            high = current_price + random.uniform(0, 0.002)
            low = current_price - random.uniform(0, 0.002)
            open_price = current_price + random.uniform(-0.001, 0.001)
            close_price = current_price + random.uniform(-0.001, 0.001)
            
            data.append({
                'timestamp': current_time + timedelta(minutes=i),
                'open': round(open_price, 5),
                'high': round(high, 5),
                'low': round(low, 5),
                'close': round(close_price, 5),
                'volume': random.randint(10, 1000)
            })
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        return df
    
    async def health_check(self) -> bool:
        """Mock health check - always healthy"""
        return self.is_connected