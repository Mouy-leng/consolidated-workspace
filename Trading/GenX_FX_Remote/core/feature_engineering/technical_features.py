"""
Technical Feature Engineering for GenX FX Trading System
Generates technical indicators and features for ML models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.technical_indicators import TechnicalIndicators

class TechnicalFeatureEngine:
    """
    Technical Feature Engineering for forex trading signals
    """
    
    def __init__(self):
        self.tech_indicators = TechnicalIndicators()
        self.feature_columns = []
        
    def generate_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """
        Generate comprehensive technical features from OHLCV data
        
        Args:
            df: DataFrame with OHLCV data (columns: Open, High, Low, Close, Volume)
            symbol: Trading symbol (optional)
            
        Returns:
            DataFrame with original data + technical features
        """
        if df.empty or len(df) < 50:
            return df
            
        # Make a copy to avoid modifying original
        features_df = df.copy()
        
        try:
            # Price-based features
            features_df = self._add_price_features(features_df)
            
            # Moving averages
            features_df = self._add_moving_averages(features_df)
            
            # Momentum indicators
            features_df = self._add_momentum_indicators(features_df)
            
            # Volatility indicators
            features_df = self._add_volatility_indicators(features_df)
            
            # Volume indicators (if volume available)
            if 'Volume' in features_df.columns:
                features_df = self._add_volume_indicators(features_df)
            
            # Pattern features
            features_df = self._add_pattern_features(features_df)
            
            # Fill any NaN values
            features_df = features_df.fillna(method='ffill').fillna(0)
            
        except Exception as e:
            print(f"Warning: Error generating features: {e}")
            return df
            
        return features_df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic price-based features"""
        df['HL_pct'] = (df['High'] - df['Low']) / df['Close'] * 100
        df['OC_pct'] = (df['Open'] - df['Close']) / df['Close'] * 100
        df['price_change'] = df['Close'].pct_change()
        df['price_range'] = df['High'] - df['Low']
        df['body_size'] = abs(df['Close'] - df['Open'])
        df['upper_shadow'] = df['High'] - df[['Open', 'Close']].max(axis=1)
        df['lower_shadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']
        
        return df
    
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add moving average features"""
        periods = [5, 10, 20, 50, 100, 200]
        
        for period in periods:
            if len(df) >= period:
                df[f'sma_{period}'] = df['Close'].rolling(window=period).mean()
                df[f'ema_{period}'] = df['Close'].ewm(span=period).mean()
                df[f'price_vs_sma_{period}'] = (df['Close'] - df[f'sma_{period}']) / df[f'sma_{period}'] * 100
                df[f'price_vs_ema_{period}'] = (df['Close'] - df[f'ema_{period}']) / df[f'ema_{period}'] * 100
        
        # Moving average crossovers
        if len(df) >= 50:
            df['sma_5_vs_20'] = (df['sma_5'] - df['sma_20']) / df['sma_20'] * 100
            df['sma_10_vs_50'] = (df['sma_10'] - df['sma_50']) / df['sma_50'] * 100
            
        return df
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-based features"""
        try:
            # RSI
            df['rsi'] = self.tech_indicators.rsi(df['Close'])
            
            # MACD
            macd_line, macd_signal, macd_histogram = self.tech_indicators.macd(df['Close'])
            df['macd'] = macd_line
            df['macd_signal'] = macd_signal
            df['macd_histogram'] = macd_histogram
            
            # Stochastic
            df['stoch_k'], df['stoch_d'] = self.tech_indicators.stochastic(df['High'], df['Low'], df['Close'])
            
            # ROC (Rate of Change)
            for period in [5, 10, 20]:
                if len(df) >= period:
                    df[f'roc_{period}'] = df['Close'].pct_change(periods=period) * 100
            
            # Williams %R
            df['williams_r'] = self.tech_indicators.williams_r(df['High'], df['Low'], df['Close'])
            
        except Exception as e:
            print(f"Warning: Error adding momentum indicators: {e}")
            
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based features"""
        try:
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.tech_indicators.bollinger_bands(df['Close'])
            df['bb_upper'] = bb_upper
            df['bb_middle'] = bb_middle  
            df['bb_lower'] = bb_lower
            df['bb_width'] = (bb_upper - bb_lower) / bb_middle * 100
            df['bb_position'] = (df['Close'] - bb_lower) / (bb_upper - bb_lower) * 100
            
            # ATR
            df['atr'] = self.tech_indicators.atr(df['High'], df['Low'], df['Close'])
            df['atr_pct'] = df['atr'] / df['Close'] * 100
            
            # Price volatility
            for period in [5, 10, 20]:
                if len(df) >= period:
                    df[f'volatility_{period}'] = df['Close'].rolling(window=period).std()
                    df[f'volatility_pct_{period}'] = df[f'volatility_{period}'] / df['Close'] * 100
            
        except Exception as e:
            print(f"Warning: Error adding volatility indicators: {e}")
            
        return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        try:
            # Volume moving averages
            for period in [5, 10, 20]:
                if len(df) >= period:
                    df[f'volume_ma_{period}'] = df['Volume'].rolling(window=period).mean()
                    df[f'volume_ratio_{period}'] = df['Volume'] / df[f'volume_ma_{period}']
            
            # Price-Volume features
            df['price_volume'] = df['Close'] * df['Volume']
            df['volume_change'] = df['Volume'].pct_change()
            
        except Exception as e:
            print(f"Warning: Error adding volume indicators: {e}")
            
        return df
    
    def _add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add candlestick pattern features"""
        try:
            # Simple pattern detection
            df['is_doji'] = (abs(df['Close'] - df['Open']) / (df['High'] - df['Low']) < 0.1).astype(int)
            df['is_hammer'] = ((df['Close'] > df['Open']) & 
                              (df['lower_shadow'] > 2 * df['body_size']) &
                              (df['upper_shadow'] < df['body_size'])).astype(int)
            df['is_shooting_star'] = ((df['Close'] < df['Open']) & 
                                     (df['upper_shadow'] > 2 * df['body_size']) &
                                     (df['lower_shadow'] < df['body_size'])).astype(int)
            
            # Trend patterns
            df['higher_high'] = (df['High'] > df['High'].shift(1)).astype(int)
            df['lower_low'] = (df['Low'] < df['Low'].shift(1)).astype(int)
            df['higher_close'] = (df['Close'] > df['Close'].shift(1)).astype(int)
            
        except Exception as e:
            print(f"Warning: Error adding pattern features: {e}")
            
        return df
    
    def get_feature_importance(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate basic feature importance based on correlation with price movement
        """
        if 'price_change' not in df.columns:
            return {}
            
        try:
            # Get numeric columns only
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            feature_cols = [col for col in numeric_cols if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Calculate correlation with price change
            correlations = {}
            for col in feature_cols:
                if col in df.columns and not df[col].isna().all():
                    corr = abs(df[col].corr(df['price_change']))
                    if not np.isnan(corr):
                        correlations[col] = corr
            
            # Sort by importance
            sorted_features = dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True))
            return sorted_features
            
        except Exception as e:
            print(f"Warning: Error calculating feature importance: {e}")
            return {}
    
    def select_top_features(self, df: pd.DataFrame, n_features: int = 20) -> List[str]:
        """
        Select top N features based on importance
        """
        importance = self.get_feature_importance(df)
        return list(importance.keys())[:n_features]