import numpy as np
import pandas as pd

class RSI:
    """RSI (Relative Strength Index) indicator"""
    
    def __init__(self, period=14):
        self.period = period
    
    def calculate(self, prices):
        """Calculate RSI for given prices"""
        if isinstance(prices, pd.Series):
            prices = prices.values
        
        deltas = np.diff(prices)
        seed = deltas[:self.period+1]
        up = seed[seed >= 0].sum()/self.period
        down = -seed[seed < 0].sum()/self.period
        rs = up/down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:self.period] = 100. - 100./(1. + rs)

        for i in range(self.period, len(prices)):
            delta = deltas[i-1]  # The diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(self.period-1) + upval)/self.period
            down = (down*(self.period-1) + downval)/self.period

            rs = up/down if down != 0 else 0
            rsi[i] = 100. - 100./(1. + rs)

        return rsi

def calculate_rsi(prices, period=14):
    """Legacy function for backward compatibility"""
    rsi = RSI(period)
    return rsi.calculate(prices)
