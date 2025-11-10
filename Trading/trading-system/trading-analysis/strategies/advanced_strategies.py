"""
Advanced Trading Strategies with Smart Money Concepts
Implementation of sophisticated trading strategies combining technical analysis with smart money principles
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import sys
import os

# Import base classes
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'analysis-engine'))
from core_analysis import SmartMoneyAnalysis, TechnicalIndicators, PatternRecognition
from strategy_framework import TradingStrategy, Trade, OrderSide

class SmartMoneyStrategy(TradingStrategy):
    """Advanced strategy using smart money concepts"""
    
    def __init__(self, name: str = "Smart Money Strategy"):
        super().__init__(name)
        self.smart_money = SmartMoneyAnalysis()
        self.pattern_recognition = PatternRecognition()
        self.min_order_block_strength = 3.0
        self.min_liquidity_touches = 3
        self.structure_break_confirmation = 2
        
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate signals based on smart money concepts"""
        if len(data) < 100:  # Need sufficient data
            return None
        
        current_price = data['Close'].iloc[-1]
        
        # Analyze market structure
        market_structure = self.smart_money.analyze_market_structure(data)
        
        # Identify order blocks
        order_blocks = self.smart_money.identify_order_blocks(data)
        
        # Identify liquidity zones
        liquidity_zones = self.smart_money.identify_liquidity_zones(data)
        
        # Look for trading opportunities
        signal = None
        
        # Strategy 1: Order Block Breakout
        for ob in order_blocks:
            if ob['strength'] >= self.min_order_block_strength:
                if ob['type'] == 'bullish_order_block':
                    # Check if price is testing the order block from above
                    if ob['zone_low'] <= current_price <= ob['zone_high'] * 1.002:
                        signal = {
                            'action': 'BUY',
                            'symbol': 'EURUSD',
                            'price': current_price,
                            'stop_loss': ob['zone_low'] * 0.998,
                            'take_profit': current_price + (current_price - ob['zone_low']) * 2,
                            'reason': f'Bullish order block retest (strength: {ob["strength"]:.2f})',
                            'confidence': min(ob['strength'] / 5.0, 1.0)
                        }
                        break
                        
                elif ob['type'] == 'bearish_order_block':
                    # Check if price is testing the order block from below
                    if ob['zone_low'] * 0.998 <= current_price <= ob['zone_high']:
                        signal = {
                            'action': 'SELL',
                            'symbol': 'EURUSD',
                            'price': current_price,
                            'stop_loss': ob['zone_high'] * 1.002,
                            'take_profit': current_price - (ob['zone_high'] - current_price) * 2,
                            'reason': f'Bearish order block retest (strength: {ob["strength"]:.2f})',
                            'confidence': min(ob['strength'] / 5.0, 1.0)
                        }
                        break
        
        # Strategy 2: Liquidity Zone Breakout
        if not signal:
            for lz in liquidity_zones:
                if lz['touches'] >= self.min_liquidity_touches and lz['strength'] > 2.0:
                    if lz['zone_type'] == 'support':
                        # Support broken - bearish signal
                        if current_price < lz['level'] * 0.999:
                            signal = {
                                'action': 'SELL',
                                'symbol': 'EURUSD',
                                'price': current_price,
                                'stop_loss': lz['level'] * 1.001,
                                'take_profit': current_price - (lz['level'] - current_price) * 2,
                                'reason': f'Support liquidity zone broken ({lz["touches"]} touches)',
                                'confidence': min(lz['touches'] / 5.0, 1.0)
                            }
                            break
                    else:  # resistance
                        # Resistance broken - bullish signal
                        if current_price > lz['level'] * 1.001:
                            signal = {
                                'action': 'BUY',
                                'symbol': 'EURUSD',
                                'price': current_price,
                                'stop_loss': lz['level'] * 0.999,
                                'take_profit': current_price + (current_price - lz['level']) * 2,
                                'reason': f'Resistance liquidity zone broken ({lz["touches"]} touches)',
                                'confidence': min(lz['touches'] / 5.0, 1.0)
                            }
                            break
        
        # Strategy 3: Market Structure Break
        if not signal:
            structure_breaks = market_structure.get('structure_breaks', [])
            for sb in structure_breaks:
                if sb['strength'] > 0.01:  # 1% move
                    if sb['type'] == 'break_of_structure_high':
                        signal = {
                            'action': 'BUY',
                            'symbol': 'EURUSD',
                            'price': current_price,
                            'stop_loss': sb['break_level'] * 0.998,
                            'take_profit': current_price + (current_price - sb['break_level']) * 1.5,
                            'reason': f'Market structure break to upside ({sb["strength"]:.2%})',
                            'confidence': min(sb['strength'] * 10, 1.0)
                        }
                        break
        
        return signal

class MultiTimeframeStrategy(TradingStrategy):
    """Strategy that analyzes multiple timeframes"""
    
    def __init__(self, name: str = "Multi-Timeframe Strategy"):
        super().__init__(name)
        self.timeframes = ['1h', '4h', '1d']
        self.technical_indicators = TechnicalIndicators()
        
    def analyze_timeframe_alignment(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """Analyze trend alignment across timeframes"""
        trends = {}
        
        for tf, data in data_dict.items():
            if len(data) < 50:
                continue
                
            # Calculate trend indicators
            ma_20 = data['Close'].rolling(20).mean()
            ma_50 = data['Close'].rolling(50).mean()
            
            current_price = data['Close'].iloc[-1]
            current_ma_20 = ma_20.iloc[-1]
            current_ma_50 = ma_50.iloc[-1]
            
            # Determine trend
            if current_price > current_ma_20 > current_ma_50:
                trend = 'bullish'
            elif current_price < current_ma_20 < current_ma_50:
                trend = 'bearish'
            else:
                trend = 'neutral'
            
            # Calculate trend strength
            ma_separation = abs(current_ma_20 - current_ma_50) / current_price
            price_ma_distance = abs(current_price - current_ma_20) / current_price
            
            trends[tf] = {
                'trend': trend,
                'strength': ma_separation + price_ma_distance,
                'ma_20': current_ma_20,
                'ma_50': current_ma_50
            }
        
        return trends
    
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate signals based on multi-timeframe analysis"""
        # For demo purposes, we'll simulate multi-timeframe data
        # In practice, you'd fetch data for different timeframes
        
        current_price = data['Close'].iloc[-1]
        
        # Analyze current timeframe (assume 1h)
        ma_20 = data['Close'].rolling(20).mean().iloc[-1]
        ma_50 = data['Close'].rolling(50).mean().iloc[-1]
        rsi = self.technical_indicators.calculate_rsi(data['Close']).iloc[-1]
        
        # Simulate higher timeframe trend (4h)
        # In practice, fetch actual 4h data
        higher_tf_bullish = ma_20 > ma_50  # Simplified
        
        signal = None
        
        # Look for pullback entries in trending markets
        if higher_tf_bullish and rsi < 40:  # Pullback in uptrend
            signal = {
                'action': 'BUY',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 0.985,
                'take_profit': current_price * 1.03,
                'reason': 'Multi-timeframe bullish pullback entry',
                'confidence': 0.7
            }
        elif not higher_tf_bullish and rsi > 60:  # Pullback in downtrend
            signal = {
                'action': 'SELL',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 1.015,
                'take_profit': current_price * 0.97,
                'reason': 'Multi-timeframe bearish pullback entry',
                'confidence': 0.7
            }
        
        return signal

class VolatilityBreakoutStrategy(TradingStrategy):
    """Strategy based on volatility breakouts"""
    
    def __init__(self, name: str = "Volatility Breakout Strategy"):
        super().__init__(name)
        self.atr_period = 14
        self.volatility_threshold = 1.5
        
    def calculate_atr(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close_prev = np.abs(data['High'] - data['Close'].shift())
        low_close_prev = np.abs(data['Low'] - data['Close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        atr = true_range.rolling(window=self.atr_period).mean()
        
        return atr
    
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate signals based on volatility breakouts"""
        if len(data) < self.atr_period + 20:
            return None
        
        current_price = data['Close'].iloc[-1]
        current_high = data['High'].iloc[-1]
        current_low = data['Low'].iloc[-1]
        
        # Calculate ATR
        atr = self.calculate_atr(data)
        current_atr = atr.iloc[-1]
        avg_atr = atr.iloc[-20:-1].mean()  # Average ATR over last 20 periods
        
        # Check for volatility expansion
        volatility_expansion = current_atr > (avg_atr * self.volatility_threshold)
        
        if not volatility_expansion:
            return None
        
        # Calculate support and resistance levels
        lookback = 20
        recent_data = data.iloc[-lookback:]
        resistance = recent_data['High'].max()
        support = recent_data['Low'].min()
        
        signal = None
        
        # Bullish breakout
        if current_high > resistance * 1.001:  # 0.1% above resistance
            signal = {
                'action': 'BUY',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price - (current_atr * 1.5),
                'take_profit': current_price + (current_atr * 3),
                'reason': f'Volatility breakout above resistance (ATR: {current_atr:.5f})',
                'confidence': min(current_atr / avg_atr / self.volatility_threshold, 1.0)
            }
        
        # Bearish breakdown
        elif current_low < support * 0.999:  # 0.1% below support
            signal = {
                'action': 'SELL',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price + (current_atr * 1.5),
                'take_profit': current_price - (current_atr * 3),
                'reason': f'Volatility breakdown below support (ATR: {current_atr:.5f})',
                'confidence': min(current_atr / avg_atr / self.volatility_threshold, 1.0)
            }
        
        return signal

class MeanReversionStrategy(TradingStrategy):
    """Mean reversion strategy for ranging markets"""
    
    def __init__(self, name: str = "Mean Reversion Strategy"):
        super().__init__(name)
        self.bb_period = 20
        self.bb_std = 2
        self.rsi_period = 14
        
    def detect_ranging_market(self, data: pd.DataFrame) -> bool:
        """Detect if market is in a ranging phase"""
        if len(data) < 50:
            return False
        
        # Calculate ADX to measure trend strength
        # Simplified: use price volatility as proxy
        returns = data['Close'].pct_change()
        volatility = returns.rolling(20).std().iloc[-1]
        avg_volatility = returns.rolling(50).std().mean()
        
        # Low volatility suggests ranging market
        return volatility < avg_volatility * 0.8
    
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate mean reversion signals"""
        if len(data) < max(self.bb_period, self.rsi_period) + 10:
            return None
        
        # Check if market is ranging
        if not self.detect_ranging_market(data):
            return None
        
        current_price = data['Close'].iloc[-1]
        
        # Calculate Bollinger Bands
        bb_data = TechnicalIndicators.calculate_bollinger_bands(data['Close'], self.bb_period, self.bb_std)
        current_bb_upper = bb_data['upper'].iloc[-1]
        current_bb_lower = bb_data['lower'].iloc[-1]
        current_bb_middle = bb_data['middle'].iloc[-1]
        
        # Calculate RSI
        rsi = TechnicalIndicators.calculate_rsi(data['Close'], self.rsi_period)
        current_rsi = rsi.iloc[-1]
        
        signal = None
        
        # Mean reversion from upper band
        if current_price >= current_bb_upper and current_rsi > 70:
            signal = {
                'action': 'SELL',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_bb_upper * 1.005,
                'take_profit': current_bb_middle,
                'reason': f'Mean reversion from upper BB (RSI: {current_rsi:.1f})',
                'confidence': min((current_rsi - 50) / 30, 1.0)
            }
        
        # Mean reversion from lower band
        elif current_price <= current_bb_lower and current_rsi < 30:
            signal = {
                'action': 'BUY',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_bb_lower * 0.995,
                'take_profit': current_bb_middle,
                'reason': f'Mean reversion from lower BB (RSI: {current_rsi:.1f})',
                'confidence': min((50 - current_rsi) / 30, 1.0)
            }
        
        return signal

class CombinedAdvancedStrategy(TradingStrategy):
    """Advanced strategy combining multiple approaches"""
    
    def __init__(self, name: str = "Combined Advanced Strategy"):
        super().__init__(name)
        self.smart_money_strategy = SmartMoneyStrategy()
        self.volatility_strategy = VolatilityBreakoutStrategy()
        self.mean_reversion_strategy = MeanReversionStrategy()
        self.pattern_recognition = PatternRecognition()
        
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate signals by combining multiple strategies"""
        if len(data) < 100:
            return None
        
        # Get signals from different strategies
        smart_money_signal = self.smart_money_strategy.generate_signal(data, current_time)
        volatility_signal = self.volatility_strategy.generate_signal(data, current_time)
        mean_reversion_signal = self.mean_reversion_strategy.generate_signal(data, current_time)
        
        # Detect patterns
        patterns = self.pattern_recognition.detect_patterns(data)
        
        signals = []
        
        # Collect all signals with their confidence scores
        if smart_money_signal:
            signals.append({
                'signal': smart_money_signal,
                'weight': 0.4,  # High weight for smart money concepts
                'type': 'smart_money'
            })
        
        if volatility_signal:
            signals.append({
                'signal': volatility_signal,
                'weight': 0.3,
                'type': 'volatility'
            })
        
        if mean_reversion_signal:
            signals.append({
                'signal': mean_reversion_signal,
                'weight': 0.2,
                'type': 'mean_reversion'
            })
        
        # Add pattern-based signals
        if patterns:
            for pattern_type, pattern_list in patterns.items():
                for pattern in pattern_list[:1]:  # Take strongest pattern
                    if pattern['strength'] > 0.7:
                        pattern_signal = self._create_pattern_signal(pattern, data['Close'].iloc[-1])
                        if pattern_signal:
                            signals.append({
                                'signal': pattern_signal,
                                'weight': 0.1,
                                'type': 'pattern'
                            })
        
        if not signals:
            return None
        
        # Combine signals using weighted voting
        return self._combine_signals(signals)
    
    def _create_pattern_signal(self, pattern: Dict, current_price: float) -> Optional[Dict]:
        """Create trading signal from detected pattern"""
        if pattern['type'] == 'double_top':
            return {
                'action': 'SELL',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 1.01,
                'take_profit': current_price * 0.97,
                'reason': f'Double top pattern (strength: {pattern["strength"]:.2f})',
                'confidence': pattern['strength']
            }
        elif pattern['type'] == 'double_bottom':
            return {
                'action': 'BUY',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 0.99,
                'take_profit': current_price * 1.03,
                'reason': f'Double bottom pattern (strength: {pattern["strength"]:.2f})',
                'confidence': pattern['strength']
            }
        
        return None
    
    def _combine_signals(self, signals: List[Dict]) -> Optional[Dict]:
        """Combine multiple signals using weighted voting"""
        if not signals:
            return None
        
        # Separate buy and sell signals
        buy_signals = [s for s in signals if s['signal']['action'] == 'BUY']
        sell_signals = [s for s in signals if s['signal']['action'] == 'SELL']
        
        # Calculate weighted scores
        buy_score = sum(s['weight'] * s['signal'].get('confidence', 0.5) for s in buy_signals)
        sell_score = sum(s['weight'] * s['signal'].get('confidence', 0.5) for s in sell_signals)
        
        # Minimum threshold for signal generation
        min_threshold = 0.3
        
        if buy_score > sell_score and buy_score > min_threshold:
            # Combine buy signals
            best_buy_signal = max(buy_signals, key=lambda x: x['signal'].get('confidence', 0))
            combined_signal = best_buy_signal['signal'].copy()
            combined_signal['confidence'] = buy_score
            combined_signal['reason'] = f"Combined signal: {combined_signal['reason']} (score: {buy_score:.2f})"
            combined_signal['components'] = [s['type'] for s in buy_signals]
            return combined_signal
            
        elif sell_score > buy_score and sell_score > min_threshold:
            # Combine sell signals
            best_sell_signal = max(sell_signals, key=lambda x: x['signal'].get('confidence', 0))
            combined_signal = best_sell_signal['signal'].copy()
            combined_signal['confidence'] = sell_score
            combined_signal['reason'] = f"Combined signal: {combined_signal['reason']} (score: {sell_score:.2f})"
            combined_signal['components'] = [s['type'] for s in sell_signals]
            return combined_signal
        
        return None

if __name__ == "__main__":
    print("Advanced Trading Strategies initialized!")
    print("Available strategies:")
    print("- Smart Money Strategy (Order blocks, liquidity zones)")
    print("- Multi-Timeframe Strategy (Trend alignment)")
    print("- Volatility Breakout Strategy (ATR-based)")
    print("- Mean Reversion Strategy (Bollinger Bands + RSI)")
    print("- Combined Advanced Strategy (Multi-approach)")