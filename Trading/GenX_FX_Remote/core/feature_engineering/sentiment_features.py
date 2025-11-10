"""
Sentiment Features for GenX FX Trading System
Features related to market sentiment and news analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class SentimentFeatures:
    """
    Sentiment feature engineering for forex trading
    """
    
    def __init__(self):
        self.feature_columns = []
        self.sentiment_cache = {}
        
    def generate_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """
        Generate sentiment-based features
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol (optional)
            
        Returns:
            DataFrame with sentiment features
        """
        if df.empty:
            return df
            
        features_df = df.copy()
        
        try:
            # Market sentiment features
            features_df = self._add_market_sentiment_features(features_df)
            
            # News sentiment features (simulated)
            features_df = self._add_news_sentiment_features(features_df, symbol)
            
            # Social media sentiment (simulated)
            features_df = self._add_social_sentiment_features(features_df, symbol)
            
            # Fear & Greed indicators
            features_df = self._add_fear_greed_features(features_df)
            
            # Fill NaN values
            features_df = features_df.fillna(method='ffill').fillna(0)
            
        except Exception as e:
            print(f"Warning: Error generating sentiment features: {e}")
            return df
            
        return features_df
    
    def _add_market_sentiment_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market sentiment indicators based on price action"""
        # Bull/Bear sentiment based on candlestick patterns
        df['bullish_candles'] = (df['Close'] > df['Open']).astype(int)
        df['bearish_candles'] = (df['Close'] < df['Open']).astype(int)
        df['bull_bear_ratio'] = df['bullish_candles'].rolling(window=20).sum() / 20
        
        # Market momentum sentiment
        df['momentum_sentiment'] = df['Close'].pct_change(periods=5).rolling(window=10).mean()
        df['sentiment_strength'] = abs(df['momentum_sentiment'])
        
        # Volatility sentiment (high volatility = uncertainty)
        df['volatility_sentiment'] = df['Close'].rolling(window=20).std() / df['Close'].rolling(window=20).mean()
        df['uncertainty_index'] = (df['volatility_sentiment'] - df['volatility_sentiment'].rolling(window=50).mean()) / df['volatility_sentiment'].rolling(window=50).std()
        
        # Price position sentiment (where price is relative to recent range)
        df['price_position'] = (df['Close'] - df['Low'].rolling(window=20).min()) / (df['High'].rolling(window=20).max() - df['Low'].rolling(window=20).min())
        df['sentiment_extreme'] = np.where(df['price_position'] > 0.8, 1, np.where(df['price_position'] < 0.2, -1, 0))
        
        return df
    
    def _add_news_sentiment_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """Add news sentiment features (simulated)"""
        # Since we don't have real news data, we'll create synthetic features
        # based on market volatility and price movements
        
        # News impact estimation (higher volatility = more news impact)
        df['news_impact'] = (df['High'] - df['Low']) / df['Close'] * 100
        df['news_sentiment'] = np.where(df['Close'] > df['Open'], 
                                       df['news_impact'] * 0.5,  # Positive news
                                       df['news_impact'] * -0.5)  # Negative news
        
        # News frequency (estimated from volatility spikes)
        df['volatility_spike'] = df['news_impact'] > df['news_impact'].rolling(window=20).quantile(0.8)
        df['news_frequency'] = df['volatility_spike'].rolling(window=10).sum()
        
        # Economic calendar impact (simulated)
        # Higher impact on certain days/times
        if not df.index.empty:
            # Simulate higher impact during typical news hours
            df['calendar_impact'] = np.random.normal(0, 0.1, len(df))  # Base noise
            
            # Add some structure for typical news days (if datetime index)
            try:
                if hasattr(df.index, 'dayofweek'):
                    # Higher impact on weekdays
                    weekday_multiplier = np.where(df.index.dayofweek < 5, 1.2, 0.8)
                    df['calendar_impact'] *= weekday_multiplier
            except:
                pass
        else:
            df['calendar_impact'] = 0
            
        return df
    
    def _add_social_sentiment_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """Add social media sentiment features (simulated)"""
        # Simulated social sentiment based on price momentum
        
        # Twitter sentiment proxy
        price_momentum = df['Close'].pct_change(periods=3).rolling(window=5).mean()
        df['twitter_sentiment'] = np.tanh(price_momentum * 10)  # Normalize to [-1, 1]
        df['twitter_volume'] = abs(price_momentum) * 100  # Simulated tweet volume
        
        # Reddit sentiment proxy
        df['reddit_sentiment'] = df['twitter_sentiment'].rolling(window=3).mean()
        df['reddit_mentions'] = df['twitter_volume'].rolling(window=2).sum()
        
        # Social media trend
        df['social_trend'] = (df['twitter_sentiment'] + df['reddit_sentiment']) / 2
        df['social_momentum'] = df['social_trend'].pct_change().rolling(window=5).mean()
        
        # Influencer sentiment (simulated high-impact accounts)
        df['influencer_sentiment'] = np.where(abs(price_momentum) > price_momentum.rolling(window=20).std(),
                                             np.sign(price_momentum) * 0.8,
                                             0)
        
        return df
    
    def _add_fear_greed_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add fear and greed indicators"""
        # VIX-like fear index based on volatility
        rolling_vol = df['Close'].rolling(window=20).std()
        vol_percentile = rolling_vol.rolling(window=50).rank(pct=True)
        df['fear_index'] = vol_percentile * 100
        df['greed_index'] = 100 - df['fear_index']
        
        # Put/Call ratio proxy (based on price action)
        downward_moves = (df['Close'] < df['Close'].shift(1)).rolling(window=10).sum()
        upward_moves = (df['Close'] > df['Close'].shift(1)).rolling(window=10).sum()
        df['put_call_ratio'] = downward_moves / (upward_moves + 1e-6)  # Add small epsilon
        
        # Market stress indicators
        df['stress_indicator'] = np.where(df['fear_index'] > 70, 1, 0)
        df['euphoria_indicator'] = np.where(df['greed_index'] > 80, 1, 0)
        
        # Sentiment oscillator
        df['sentiment_oscillator'] = (df['greed_index'] - 50) / 50  # Normalize to [-1, 1]
        df['sentiment_extreme_flag'] = np.where(abs(df['sentiment_oscillator']) > 0.6, 1, 0)
        
        return df
    
    def get_sentiment_summary(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Get current sentiment summary
        
        Returns:
            Dictionary with current sentiment metrics
        """
        if df.empty or len(df) < 5:
            return {}
            
        try:
            latest = df.iloc[-1]
            recent = df.tail(5)
            
            summary = {
                'overall_sentiment': latest.get('social_trend', 0),
                'sentiment_strength': latest.get('sentiment_strength', 0),
                'fear_level': latest.get('fear_index', 50),
                'greed_level': latest.get('greed_index', 50),
                'news_impact': latest.get('news_impact', 0),
                'social_momentum': latest.get('social_momentum', 0),
                'market_stress': latest.get('stress_indicator', 0),
                'sentiment_trend': recent['social_trend'].mean() if 'social_trend' in recent.columns else 0
            }
            
            return summary
            
        except Exception as e:
            print(f"Warning: Error calculating sentiment summary: {e}")
            return {}
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names generated by this class"""
        return [
            'bullish_candles', 'bearish_candles', 'bull_bear_ratio',
            'momentum_sentiment', 'sentiment_strength', 'volatility_sentiment', 'uncertainty_index',
            'price_position', 'sentiment_extreme',
            'news_impact', 'news_sentiment', 'news_frequency', 'calendar_impact',
            'twitter_sentiment', 'twitter_volume', 'reddit_sentiment', 'reddit_mentions',
            'social_trend', 'social_momentum', 'influencer_sentiment',
            'fear_index', 'greed_index', 'put_call_ratio', 'stress_indicator',
            'euphoria_indicator', 'sentiment_oscillator', 'sentiment_extreme_flag'
        ]