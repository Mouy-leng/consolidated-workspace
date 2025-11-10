"""
Trading Analysis Engine - Core Analysis Module
Provides comprehensive market analysis, pattern recognition, and smart money concepts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import json

class TradingAnalysisEngine:
    """Main analysis engine for trading strategies and market analysis"""
    
    def __init__(self, config_path: str = "config/analysis-config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.data_cache = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """Load analysis configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "analysis": {
                "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
                "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
                "indicators": {
                    "rsi_period": 14,
                    "macd_fast": 12,
                    "macd_slow": 26,
                    "macd_signal": 9
                }
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/analysis.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

class TechnicalIndicators:
    """Technical indicators calculation and analysis"""
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        return {
            'middle': sma,
            'upper': sma + (std * std_dev),
            'lower': sma - (std * std_dev)
        }
    
    @staticmethod
    def calculate_moving_averages(data: pd.Series, periods: List[int] = [20, 50, 100, 200]) -> Dict[str, pd.Series]:
        """Calculate multiple moving averages"""
        mas = {}
        for period in periods:
            mas[f'MA_{period}'] = data.rolling(window=period).mean()
        return mas

class PatternRecognition:
    """Chart pattern recognition and analysis"""
    
    def __init__(self):
        self.patterns = {
            'double_top': self._detect_double_top,
            'double_bottom': self._detect_double_bottom,
            'head_shoulders': self._detect_head_shoulders,
            'triangle': self._detect_triangle,
            'flag': self._detect_flag,
            'wedge': self._detect_wedge
        }
    
    def detect_patterns(self, ohlc_data: pd.DataFrame) -> Dict[str, List]:
        """Detect all available patterns in OHLC data"""
        detected_patterns = {}
        
        for pattern_name, detector in self.patterns.items():
            try:
                patterns = detector(ohlc_data)
                if patterns:
                    detected_patterns[pattern_name] = patterns
            except Exception as e:
                logging.error(f"Error detecting {pattern_name}: {e}")
        
        return detected_patterns
    
    def _detect_double_top(self, ohlc_data: pd.DataFrame) -> List[Dict]:
        """Detect double top patterns"""
        # Implementation for double top pattern detection
        patterns = []
        highs = ohlc_data['High']
        
        # Find local maxima
        local_maxima = self._find_local_extrema(highs, 'max')
        
        # Look for two similar highs with a valley between
        for i in range(len(local_maxima) - 1):
            peak1 = local_maxima[i]
            peak2 = local_maxima[i + 1]
            
            # Check if peaks are at similar levels (within 1% tolerance)
            if abs(peak1['value'] - peak2['value']) / peak1['value'] < 0.01:
                # Find valley between peaks
                valley_data = highs[peak1['index']:peak2['index']]
                valley_min = valley_data.min()
                
                # Validate pattern
                if (peak1['value'] - valley_min) / peak1['value'] > 0.02:  # 2% decline
                    patterns.append({
                        'type': 'double_top',
                        'start_index': peak1['index'],
                        'end_index': peak2['index'],
                        'peak1': peak1,
                        'peak2': peak2,
                        'valley': valley_min,
                        'strength': self._calculate_pattern_strength(peak1, peak2, valley_min)
                    })
        
        return patterns
    
    def _detect_double_bottom(self, ohlc_data: pd.DataFrame) -> List[Dict]:
        """Detect double bottom patterns"""
        patterns = []
        lows = ohlc_data['Low']
        
        # Find local minima
        local_minima = self._find_local_extrema(lows, 'min')
        
        # Look for two similar lows with a peak between
        for i in range(len(local_minima) - 1):
            trough1 = local_minima[i]
            trough2 = local_minima[i + 1]
            
            # Check if troughs are at similar levels
            if abs(trough1['value'] - trough2['value']) / trough1['value'] < 0.01:
                # Find peak between troughs
                peak_data = lows[trough1['index']:trough2['index']]
                peak_max = peak_data.max()
                
                # Validate pattern
                if (peak_max - trough1['value']) / trough1['value'] > 0.02:
                    patterns.append({
                        'type': 'double_bottom',
                        'start_index': trough1['index'],
                        'end_index': trough2['index'],
                        'trough1': trough1,
                        'trough2': trough2,
                        'peak': peak_max,
                        'strength': self._calculate_pattern_strength(trough1, trough2, peak_max)
                    })
        
        return patterns
    
    def _detect_head_shoulders(self, ohlc_data: pd.DataFrame) -> List[Dict]:
        """Detect head and shoulders patterns"""
        # Simplified implementation
        return []
    
    def _detect_triangle(self, ohlc_data: pd.DataFrame) -> List[Dict]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        # Simplified implementation
        return []
    
    def _detect_flag(self, ohlc_data: pd.DataFrame) -> List[Dict]:
        """Detect flag patterns"""
        # Simplified implementation
        return []
    
    def _detect_wedge(self, ohlc_data: pd.DataFrame) -> List[Dict]:
        """Detect wedge patterns"""
        # Simplified implementation
        return []
    
    def _find_local_extrema(self, data: pd.Series, extrema_type: str, window: int = 5) -> List[Dict]:
        """Find local maxima or minima in price data"""
        extrema = []
        
        for i in range(window, len(data) - window):
            if extrema_type == 'max':
                is_extrema = all(data.iloc[i] >= data.iloc[i-j] for j in range(1, window+1)) and \
                           all(data.iloc[i] >= data.iloc[i+j] for j in range(1, window+1))
            else:  # min
                is_extrema = all(data.iloc[i] <= data.iloc[i-j] for j in range(1, window+1)) and \
                           all(data.iloc[i] <= data.iloc[i+j] for j in range(1, window+1))
            
            if is_extrema:
                extrema.append({
                    'index': i,
                    'value': data.iloc[i],
                    'timestamp': data.index[i]
                })
        
        return extrema
    
    def _calculate_pattern_strength(self, point1: Dict, point2: Dict, reference_point: float) -> float:
        """Calculate pattern strength based on various factors"""
        # Simplified strength calculation
        price_similarity = 1 - abs(point1['value'] - point2['value']) / max(point1['value'], point2['value'])
        time_factor = 1 / (abs(point2['index'] - point1['index']) / 100)  # Normalize by 100 bars
        
        return min(price_similarity * time_factor, 1.0)

class SmartMoneyAnalysis:
    """Smart Money Concepts analysis including order blocks, liquidity zones, and market structure"""
    
    def __init__(self):
        self.order_blocks = []
        self.liquidity_zones = []
        self.market_structure = {
            'trend': 'neutral',
            'last_higher_high': None,
            'last_higher_low': None,
            'last_lower_high': None,
            'last_lower_low': None
        }
    
    def analyze_market_structure(self, ohlc_data: pd.DataFrame) -> Dict:
        """Analyze overall market structure and trend"""
        highs = ohlc_data['High']
        lows = ohlc_data['Low']
        
        # Find swing highs and lows
        swing_highs = self._find_swing_points(highs, 'high')
        swing_lows = self._find_swing_points(lows, 'low')
        
        # Determine trend based on swing points
        trend = self._determine_trend(swing_highs, swing_lows)
        
        return {
            'trend': trend,
            'swing_highs': swing_highs[-5:],  # Last 5 swing highs
            'swing_lows': swing_lows[-5:],    # Last 5 swing lows
            'structure_breaks': self._identify_structure_breaks(swing_highs, swing_lows)
        }
    
    def identify_order_blocks(self, ohlc_data: pd.DataFrame, volume_data: Optional[pd.Series] = None) -> List[Dict]:
        """Identify order blocks (zones where smart money placed large orders)"""
        order_blocks = []
        
        # Look for strong moves followed by pullbacks
        for i in range(20, len(ohlc_data) - 5):
            current_candle = ohlc_data.iloc[i]
            
            # Check for strong bullish candle
            if self._is_strong_bullish_candle(current_candle):
                # Look for previous consolidation area
                consolidation_zone = self._find_consolidation_zone(ohlc_data.iloc[i-20:i])
                
                if consolidation_zone:
                    order_blocks.append({
                        'type': 'bullish_order_block',
                        'zone_high': consolidation_zone['high'],
                        'zone_low': consolidation_zone['low'],
                        'trigger_candle_index': i,
                        'strength': self._calculate_order_block_strength(current_candle, consolidation_zone),
                        'timestamp': ohlc_data.index[i]
                    })
            
            # Check for strong bearish candle
            elif self._is_strong_bearish_candle(current_candle):
                consolidation_zone = self._find_consolidation_zone(ohlc_data.iloc[i-20:i])
                
                if consolidation_zone:
                    order_blocks.append({
                        'type': 'bearish_order_block',
                        'zone_high': consolidation_zone['high'],
                        'zone_low': consolidation_zone['low'],
                        'trigger_candle_index': i,
                        'strength': self._calculate_order_block_strength(current_candle, consolidation_zone),
                        'timestamp': ohlc_data.index[i]
                    })
        
        return order_blocks
    
    def identify_liquidity_zones(self, ohlc_data: pd.DataFrame) -> List[Dict]:
        """Identify liquidity zones (areas where stops are likely accumulated)"""
        liquidity_zones = []
        
        # Find areas with multiple touches (support/resistance)
        significant_levels = self._find_significant_levels(ohlc_data)
        
        for level in significant_levels:
            if level['touches'] >= 3:  # At least 3 touches to be significant
                liquidity_zones.append({
                    'type': 'liquidity_zone',
                    'level': level['price'],
                    'touches': level['touches'],
                    'strength': level['strength'],
                    'last_touch': level['last_touch'],
                    'zone_type': 'resistance' if level['level_type'] == 'high' else 'support'
                })
        
        return liquidity_zones
    
    def _find_swing_points(self, data: pd.Series, point_type: str, lookback: int = 5) -> List[Dict]:
        """Find swing highs or lows"""
        swing_points = []
        
        for i in range(lookback, len(data) - lookback):
            if point_type == 'high':
                is_swing = all(data.iloc[i] >= data.iloc[i-j] for j in range(1, lookback+1)) and \
                          all(data.iloc[i] >= data.iloc[i+j] for j in range(1, lookback+1))
            else:  # low
                is_swing = all(data.iloc[i] <= data.iloc[i-j] for j in range(1, lookback+1)) and \
                          all(data.iloc[i] <= data.iloc[i+j] for j in range(1, lookback+1))
            
            if is_swing:
                swing_points.append({
                    'index': i,
                    'price': data.iloc[i],
                    'timestamp': data.index[i],
                    'type': point_type
                })
        
        return swing_points
    
    def _determine_trend(self, swing_highs: List[Dict], swing_lows: List[Dict]) -> str:
        """Determine market trend based on swing points"""
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return 'neutral'
        
        # Check for higher highs and higher lows (uptrend)
        recent_highs = swing_highs[-2:]
        recent_lows = swing_lows[-2:]
        
        higher_highs = recent_highs[1]['price'] > recent_highs[0]['price']
        higher_lows = recent_lows[1]['price'] > recent_lows[0]['price']
        
        lower_highs = recent_highs[1]['price'] < recent_highs[0]['price']
        lower_lows = recent_lows[1]['price'] < recent_lows[0]['price']
        
        if higher_highs and higher_lows:
            return 'uptrend'
        elif lower_highs and lower_lows:
            return 'downtrend'
        else:
            return 'consolidation'
    
    def _identify_structure_breaks(self, swing_highs: List[Dict], swing_lows: List[Dict]) -> List[Dict]:
        """Identify market structure breaks"""
        structure_breaks = []
        
        # Look for breaks of recent swing highs/lows
        if len(swing_highs) >= 2:
            last_high = swing_highs[-1]
            prev_high = swing_highs[-2]
            
            if last_high['price'] > prev_high['price'] * 1.01:  # 1% break
                structure_breaks.append({
                    'type': 'break_of_structure_high',
                    'break_level': prev_high['price'],
                    'break_time': last_high['timestamp'],
                    'strength': (last_high['price'] - prev_high['price']) / prev_high['price']
                })
        
        return structure_breaks
    
    def _is_strong_bullish_candle(self, candle: pd.Series) -> bool:
        """Check if candle is a strong bullish candle"""
        body_size = candle['Close'] - candle['Open']
        candle_range = candle['High'] - candle['Low']
        
        return (candle['Close'] > candle['Open'] and  # Bullish
                body_size / candle_range > 0.7 and    # Large body
                body_size / candle['Open'] > 0.01)     # Significant move (1%)
    
    def _is_strong_bearish_candle(self, candle: pd.Series) -> bool:
        """Check if candle is a strong bearish candle"""
        body_size = candle['Open'] - candle['Close']
        candle_range = candle['High'] - candle['Low']
        
        return (candle['Close'] < candle['Open'] and  # Bearish
                body_size / candle_range > 0.7 and    # Large body
                body_size / candle['Open'] > 0.01)     # Significant move (1%)
    
    def _find_consolidation_zone(self, data: pd.DataFrame) -> Optional[Dict]:
        """Find consolidation zones in price data"""
        if len(data) < 5:
            return None
        
        high = data['High'].max()
        low = data['Low'].min()
        range_size = high - low
        
        # Check if range is relatively small (consolidation)
        avg_price = (high + low) / 2
        if range_size / avg_price < 0.02:  # Less than 2% range
            return {
                'high': high,
                'low': low,
                'range': range_size,
                'duration': len(data)
            }
        
        return None
    
    def _calculate_order_block_strength(self, trigger_candle: pd.Series, zone: Dict) -> float:
        """Calculate order block strength"""
        move_size = abs(trigger_candle['Close'] - trigger_candle['Open'])
        zone_range = zone['range']
        
        # Strength based on move size relative to zone range
        if zone_range > 0:
            return min(move_size / zone_range, 5.0)  # Cap at 5.0
        return 1.0
    
    def _find_significant_levels(self, ohlc_data: pd.DataFrame, tolerance: float = 0.001) -> List[Dict]:
        """Find significant support/resistance levels"""
        levels = []
        
        # Combine highs and lows
        all_highs = ohlc_data['High'].values
        all_lows = ohlc_data['Low'].values
        
        # Find levels with multiple touches
        for price_level in np.concatenate([all_highs, all_lows]):
            touches = 0
            touch_indices = []
            
            # Count touches within tolerance
            for i, (high, low) in enumerate(zip(all_highs, all_lows)):
                if abs(high - price_level) <= price_level * tolerance:
                    touches += 1
                    touch_indices.append(i)
                elif abs(low - price_level) <= price_level * tolerance:
                    touches += 1
                    touch_indices.append(i)
            
            if touches >= 2:  # At least 2 touches
                levels.append({
                    'price': price_level,
                    'touches': touches,
                    'strength': touches * (1 + len(touch_indices) / len(ohlc_data)),
                    'last_touch': max(touch_indices) if touch_indices else 0,
                    'level_type': 'high' if price_level in all_highs else 'low'
                })
        
        # Remove duplicates and sort by strength
        unique_levels = []
        for level in levels:
            is_duplicate = any(abs(level['price'] - ul['price']) <= level['price'] * tolerance 
                             for ul in unique_levels)
            if not is_duplicate:
                unique_levels.append(level)
        
        return sorted(unique_levels, key=lambda x: x['strength'], reverse=True)

if __name__ == "__main__":
    # Example usage
    engine = TradingAnalysisEngine()
    print("Trading Analysis Engine initialized successfully!")
    print("Available modules:")
    print("- Technical Indicators")
    print("- Pattern Recognition") 
    print("- Smart Money Analysis")