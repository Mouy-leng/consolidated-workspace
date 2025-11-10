"""
Market Microstructure Features for GenX FX Trading System
Features related to market microstructure and order flow
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

class MarketMicrostructureFeatures:
    """
    Market microstructure feature engineering for forex trading
    """
    
    def __init__(self):
        self.feature_columns = []
        
    def generate_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """
        Generate market microstructure features
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol (optional)
            
        Returns:
            DataFrame with microstructure features
        """
        if df.empty or len(df) < 10:
            return df
            
        features_df = df.copy()
        
        try:
            # Spread indicators
            features_df = self._add_spread_features(features_df)
            
            # Price impact features
            features_df = self._add_price_impact_features(features_df)
            
            # Order flow features
            features_df = self._add_order_flow_features(features_df)
            
            # Market depth features (simulated)
            features_df = self._add_market_depth_features(features_df)
            
            # Fill NaN values
            features_df = features_df.fillna(method='ffill').fillna(0)
            
        except Exception as e:
            print(f"Warning: Error generating microstructure features: {e}")
            return df
            
        return features_df
    
    def _add_spread_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add bid-ask spread related features (simulated)"""
        # Since we don't have real bid/ask data, we'll estimate
        df['estimated_spread'] = (df['High'] - df['Low']) * 0.1  # Rough estimate
        df['spread_pct'] = df['estimated_spread'] / df['Close'] * 100
        df['spread_ma_5'] = df['estimated_spread'].rolling(window=5).mean()
        df['spread_volatility'] = df['estimated_spread'].rolling(window=10).std()
        
        return df
    
    def _add_price_impact_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price impact features"""
        # Price impact estimation based on price movements
        df['price_impact_1'] = abs(df['Close'].shift(1) - df['Open'])
        df['price_impact_5'] = abs(df['Close'].shift(5) - df['Close']) if len(df) > 5 else 0
        df['cumulative_impact'] = df['price_impact_1'].rolling(window=10).sum()
        
        # Effective spread (estimated)
        df['effective_spread'] = abs(df['Close'] - df['Open'])
        df['effective_spread_pct'] = df['effective_spread'] / df['Close'] * 100
        
        return df
    
    def _add_order_flow_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add order flow features (estimated from price/volume)"""
        if 'Volume' in df.columns:
            # Volume-weighted features
            df['vwap'] = (df['Close'] * df['Volume']).rolling(window=20).sum() / df['Volume'].rolling(window=20).sum()
            df['price_vs_vwap'] = (df['Close'] - df['vwap']) / df['vwap'] * 100
            
            # Order flow imbalance (estimated)
            df['volume_imbalance'] = df['Volume'] - df['Volume'].rolling(window=20).mean()
            df['price_volume_trend'] = (df['Close'].pct_change() * df['Volume']).rolling(window=5).sum()
        else:
            # Price-based approximations when volume is not available
            df['vwap'] = df['Close'].rolling(window=20).mean()
            df['price_vs_vwap'] = (df['Close'] - df['vwap']) / df['vwap'] * 100
            df['volume_imbalance'] = 0
            df['price_volume_trend'] = df['Close'].pct_change().rolling(window=5).sum()
        
        # Trade direction (estimated from price movements)
        df['trade_direction'] = np.where(df['Close'] > df['Open'], 1, -1)
        df['buy_pressure'] = df['trade_direction'].rolling(window=10).sum()
        
        return df
    
    def _add_market_depth_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market depth features (simulated)"""
        # Since we don't have real order book data, we'll create proxies
        
        # Depth estimation based on volatility
        df['estimated_depth'] = 1 / (df['High'] - df['Low']).rolling(window=10).std()
        df['depth_ratio'] = df['estimated_depth'] / df['estimated_depth'].rolling(window=20).mean()
        
        # Liquidity proxy
        if 'Volume' in df.columns:
            df['liquidity_proxy'] = df['Volume'] / (df['High'] - df['Low'])
        else:
            df['liquidity_proxy'] = 1 / (df['High'] - df['Low'])
            
        df['liquidity_ratio'] = df['liquidity_proxy'] / df['liquidity_proxy'].rolling(window=20).mean()
        
        # Market resilience (how quickly price returns to equilibrium)
        df['price_resilience'] = abs(df['Close'] - df['Open']).rolling(window=5).mean()
        df['resilience_ratio'] = df['price_resilience'] / df['price_resilience'].rolling(window=20).mean()
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names generated by this class"""
        return [
            'estimated_spread', 'spread_pct', 'spread_ma_5', 'spread_volatility',
            'price_impact_1', 'price_impact_5', 'cumulative_impact',
            'effective_spread', 'effective_spread_pct',
            'vwap', 'price_vs_vwap', 'volume_imbalance', 'price_volume_trend',
            'trade_direction', 'buy_pressure',
            'estimated_depth', 'depth_ratio', 'liquidity_proxy', 'liquidity_ratio',
            'price_resilience', 'resilience_ratio'
        ]