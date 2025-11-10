"""
Pattern Detection for Trading
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class PatternDetector:
    """Detects trading patterns in market data"""
    
    def __init__(self):
        pass
    
    def detect_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect various patterns in market data"""
        
        patterns = {}
        
        # Detect bullish engulfing pattern
        patterns['bullish_engulfing'] = self._detect_bullish_engulfing(data)
        
        # Detect bearish engulfing pattern
        patterns['bearish_engulfing'] = self._detect_bearish_engulfing(data)
        
        # Detect doji pattern
        patterns['doji'] = self._detect_doji(data)
        
        return patterns
    
    def _detect_bullish_engulfing(self, data: pd.DataFrame) -> pd.Series:
        """Detect bullish engulfing pattern"""
        
        if len(data) < 2:
            return pd.Series(0, index=data.index)
        
        # Previous candle is red (bearish)
        prev_bearish = data['close'].shift(1) < data['open'].shift(1)
        
        # Current candle is green (bullish)
        curr_bullish = data['close'] > data['open']
        
        # Current candle engulfs previous candle
        engulfs = (data['open'] < data['close'].shift(1)) & (data['close'] > data['open'].shift(1))
        
        pattern = prev_bearish & curr_bullish & engulfs
        return pattern.astype(int)
    
    def _detect_bearish_engulfing(self, data: pd.DataFrame) -> pd.Series:
        """Detect bearish engulfing pattern"""
        
        if len(data) < 2:
            return pd.Series(0, index=data.index)
        
        # Previous candle is green (bullish)
        prev_bullish = data['close'].shift(1) > data['open'].shift(1)
        
        # Current candle is red (bearish)
        curr_bearish = data['close'] < data['open']
        
        # Current candle engulfs previous candle
        engulfs = (data['open'] > data['close'].shift(1)) & (data['close'] < data['open'].shift(1))
        
        pattern = prev_bullish & curr_bearish & engulfs
        return pattern.astype(int)
    
    def _detect_doji(self, data: pd.DataFrame) -> pd.Series:
        """Detect doji pattern"""
        
        # Doji occurs when open and close are very close
        body_size = abs(data['close'] - data['open'])
        candle_range = data['high'] - data['low']
        
        # Body size should be less than 10% of the total range
        doji = body_size < (candle_range * 0.1)
        
        return doji.astype(int)
