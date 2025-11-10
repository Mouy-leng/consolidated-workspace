import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class SignalAnalyzer:
    """
    Analyze and filter trading signals based on various criteria
    """
    
    def __init__(self):
        self.signal_history = []
        self.filters = {
            'strength': self._filter_by_strength,
            'time': self._filter_by_time,
            'confluence': self._filter_by_confluence
        }
    
    def analyze_signals(self, patterns: Dict[str, List], 
                       market_data: pd.DataFrame) -> List[Dict]:
        """
        Analyze patterns and generate trading signals
        
        Args:
            patterns: Dictionary of detected patterns
            market_data: Market data for context
            
        Returns:
            List of analyzed signals
        """
        all_signals = []
        
        # Flatten all patterns into signals
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                signal = {
                    'id': f"{pattern_type}_{len(all_signals)}",
                    'pattern_type': pattern_type,
                    'pattern': pattern['type'],
                    'timestamp': pattern['timestamp'],
                    'strength': pattern['strength'],
                    'direction': pattern['direction'],
                    'price': self._get_price_at_timestamp(market_data, pattern['timestamp']),
                    'confidence': self._calculate_confidence(pattern, market_data)
                }
                all_signals.append(signal)
        
        # Apply filters
        filtered_signals = self._apply_filters(all_signals)
        
        # Sort by confidence and timestamp
        filtered_signals.sort(key=lambda x: (x['confidence'], x['timestamp']), reverse=True)
        
        return filtered_signals
    
    def generate_signals_from_predictions(self, predictions: pd.DataFrame) -> List[Dict]:
        """
        Generates trading signals from AI model predictions.
        """
        signals = []

        for index, row in predictions.iterrows():
            if row['prediction'] == 1:
                signals.append({
                    'id': f"ai_model_{len(signals)}",
                    'pattern_type': 'ai_model',
                    'pattern': 'price_increase',
                    'timestamp': index,
                    'strength': 1,
                    'direction': 'bullish',
                    'price': row['close'],
                    'confidence': 1
                })
            elif row['prediction'] == 0:
                signals.append({
                    'id': f"ai_model_{len(signals)}",
                    'pattern_type': 'ai_model',
                    'pattern': 'price_decrease',
                    'timestamp': index,
                    'strength': 1,
                    'direction': 'bearish',
                    'price': row['close'],
                    'confidence': 1
                })

        return signals

    def _get_price_at_timestamp(self, data: pd.DataFrame, timestamp) -> float:
        """Get price at specific timestamp"""
        try:
            if timestamp in data.index:
                return data.loc[timestamp, 'close']
            else:
                # Find nearest timestamp
                nearest_idx = data.index.get_indexer([timestamp], method='nearest')[0]
                return data.iloc[nearest_idx]['close']
        except Exception:
            return 0.0
    
    def _calculate_confidence(self, pattern: Dict, market_data: pd.DataFrame) -> float:
        """Calculate confidence score for a pattern"""
        base_confidence = min(pattern['strength'], 1.0)
        
        # Adjust based on market conditions
        volume_factor = 1.0
        if 'volume' in market_data.columns:
            try:
                timestamp = pattern['timestamp']
                if timestamp in market_data.index:
                    current_volume = market_data.loc[timestamp, 'volume']
                    avg_volume = market_data['volume'].rolling(20).mean().loc[timestamp]
                    volume_factor = min(current_volume / avg_volume, 2.0) if avg_volume > 0 else 1.0
            except Exception:
                pass
        
        return base_confidence * volume_factor
    
    def _apply_filters(self, signals: List[Dict]) -> List[Dict]:
        """Apply filtering criteria to signals"""
        filtered_signals = signals
        
        for filter_name, filter_func in self.filters.items():
            filtered_signals = filter_func(filtered_signals)
        
        return filtered_signals
    
    def _filter_by_strength(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals by minimum strength threshold"""
        min_strength = 0.5
        return [s for s in signals if s['strength'] >= min_strength]
    
    def _filter_by_time(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals by time relevance"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        # return [s for s in signals if s['timestamp'] >= cutoff_time]
        return signals #FIXME
    
    def _filter_by_confluence(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals by confluence (multiple signals in same direction)"""
        # Group signals by direction and time proximity
        signal_groups = {}
        
        for signal in signals:
            time_key = signal['timestamp'].strftime('%Y-%m-%d %H')
            direction_key = f"{time_key}_{signal['direction']}"
            
            if direction_key not in signal_groups:
                signal_groups[direction_key] = []
            signal_groups[direction_key].append(signal)
        
        # Keep signals that have confluence
        filtered_signals = []
        for group in signal_groups.values():
            if len(group) >= 2:  # At least 2 signals in same direction
                # Take the strongest signal from the group
                strongest = max(group, key=lambda x: x['confidence'])
                strongest['confluence_count'] = len(group)
                filtered_signals.append(strongest)
        
        return filtered_signals
    
    def update_signal_history(self, signals: List[Dict]):
        """Update signal history for tracking"""
        self.signal_history.extend(signals)
        
        # Keep only recent signals
        cutoff_time = datetime.now() - timedelta(days=7)
        self.signal_history = [
            s for s in self.signal_history 
            if s['timestamp'] >= cutoff_time
        ]
