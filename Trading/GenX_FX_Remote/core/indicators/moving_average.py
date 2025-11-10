import numpy as np
import pandas as pd

class MovingAverage:
    """Moving average indicators"""
    
    def __init__(self):
        pass
    
    def sma(self, prices, period):
        """Calculate Simple Moving Average"""
        if isinstance(prices, pd.Series):
            return prices.rolling(window=period).mean()
        else:
            return np.convolve(prices, np.ones(period)/period, mode='valid')
    
    def ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if isinstance(prices, pd.Series):
            return prices.ewm(span=period).mean()
        else:
            alpha = 2.0 / (period + 1.0)
            ema = np.zeros_like(prices)
            ema[0] = prices[0]
            for i in range(1, len(prices)):
                ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]
            return ema

def calculate_sma(prices, period):
    """Legacy function for backward compatibility"""
    ma = MovingAverage()
    return ma.sma(prices, period)

def calculate_ema(prices, period):
    """Legacy function for backward compatibility"""
    ma = MovingAverage()
    return ma.ema(prices, period)
