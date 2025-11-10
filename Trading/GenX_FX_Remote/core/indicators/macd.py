import numpy as np
import pandas as pd
from .moving_average import MovingAverage

class MACD:
    """MACD (Moving Average Convergence Divergence) indicator"""
    
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.ma = MovingAverage()
    
    def calculate(self, prices):
        """Calculate MACD for given prices"""
        if isinstance(prices, pd.Series):
            prices = prices.values
        
        fast_ema = self.ma.ema(prices, self.fast_period)
        slow_ema = self.ma.ema(prices, self.slow_period)
        
        # Align arrays
        min_len = min(len(fast_ema), len(slow_ema))
        fast_ema = fast_ema[-min_len:]
        slow_ema = slow_ema[-min_len:]
        
        macd_line = fast_ema - slow_ema
        signal_line = self.ma.ema(macd_line, self.signal_period)
        
        # Align for histogram
        min_len = min(len(macd_line), len(signal_line))
        macd_line = macd_line[-min_len:]
        signal_line = signal_line[-min_len:]
        
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line[-1] if len(macd_line) > 0 else 0,
            'signal': signal_line[-1] if len(signal_line) > 0 else 0,
            'histogram': histogram[-1] if len(histogram) > 0 else 0
        }

def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """Legacy function for backward compatibility"""
    macd = MACD(fast_period, slow_period, signal_period)
    result = macd.calculate(prices)
    return result['macd'], result['signal'], result['histogram']
