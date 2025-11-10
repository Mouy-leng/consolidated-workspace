"""
Multi-Timeframe Signal Validator for GenX FX Trading System
Validates trading signals across multiple timeframes for confirmation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass

class ValidationResult(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    INVALID = "invalid"

@dataclass
class TimeframeSignal:
    """Signal information for a specific timeframe"""
    timeframe: str
    signal: str
    confidence: float
    strength: float
    timestamp: pd.Timestamp

@dataclass
class ValidationReport:
    """Signal validation report"""
    overall_result: ValidationResult
    confidence: float
    timeframe_signals: List[TimeframeSignal]
    consensus_score: float
    validation_notes: List[str]

class MultiTimeframeValidator:
    """
    Multi-timeframe signal validator for forex trading
    """
    
    def __init__(self, timeframes: List[str] = None):
        """
        Initialize validator
        
        Args:
            timeframes: List of timeframes to validate (e.g., ['M15', 'H1', 'H4', 'D1'])
        """
        self.timeframes = timeframes or ['M15', 'H1', 'H4', 'D1']
        self.timeframe_weights = self._get_timeframe_weights()
        self.validation_history = []
        
    def _get_timeframe_weights(self) -> Dict[str, float]:
        """Get weights for different timeframes"""
        weights = {
            'M1': 0.1,
            'M5': 0.15,
            'M15': 0.2,
            'M30': 0.25,
            'H1': 0.3,
            'H4': 0.4,
            'D1': 0.5,
            'W1': 0.6
        }
        
        # Normalize weights for configured timeframes
        total_weight = sum(weights.get(tf, 0.3) for tf in self.timeframes)
        normalized_weights = {}
        for tf in self.timeframes:
            normalized_weights[tf] = weights.get(tf, 0.3) / total_weight
            
        return normalized_weights
    
    def validate_signal(self, symbol: str, signal_data: Dict[str, Any], 
                       market_data: Dict[str, pd.DataFrame] = None) -> ValidationReport:
        """
        Validate a trading signal across multiple timeframes
        
        Args:
            symbol: Trading symbol
            signal_data: Signal information (signal, confidence, etc.)
            market_data: Market data for different timeframes
            
        Returns:
            ValidationReport with validation results
        """
        try:
            timeframe_signals = []
            validation_notes = []
            
            # Get or generate timeframe signals
            if market_data:
                timeframe_signals = self._analyze_market_data(symbol, signal_data, market_data)
            else:
                timeframe_signals = self._generate_synthetic_signals(symbol, signal_data)
            
            # Calculate consensus
            consensus_score = self._calculate_consensus(timeframe_signals)
            
            # Determine overall result
            overall_result = self._determine_overall_result(consensus_score, timeframe_signals)
            
            # Calculate final confidence
            final_confidence = self._calculate_final_confidence(timeframe_signals, consensus_score)
            
            # Generate validation notes
            validation_notes = self._generate_validation_notes(timeframe_signals, consensus_score)
            
            report = ValidationReport(
                overall_result=overall_result,
                confidence=final_confidence,
                timeframe_signals=timeframe_signals,
                consensus_score=consensus_score,
                validation_notes=validation_notes
            )
            
            # Store in history
            self.validation_history.append({
                'timestamp': pd.Timestamp.now(),
                'symbol': symbol,
                'report': report
            })
            
            return report
            
        except Exception as e:
            print(f"Warning: Error validating signal: {e}")
            return self._default_validation_report()
    
    def _analyze_market_data(self, symbol: str, signal_data: Dict[str, Any], 
                           market_data: Dict[str, pd.DataFrame]) -> List[TimeframeSignal]:
        """Analyze actual market data across timeframes"""
        timeframe_signals = []
        
        for timeframe in self.timeframes:
            if timeframe in market_data and not market_data[timeframe].empty:
                df = market_data[timeframe].tail(50)  # Use last 50 bars
                
                # Simple trend analysis
                signal_result = self._analyze_timeframe_data(df, signal_data)
                
                timeframe_signals.append(TimeframeSignal(
                    timeframe=timeframe,
                    signal=signal_result['signal'],
                    confidence=signal_result['confidence'],
                    strength=signal_result['strength'],
                    timestamp=pd.Timestamp.now()
                ))
        
        return timeframe_signals
    
    def _analyze_timeframe_data(self, df: pd.DataFrame, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data for a single timeframe"""
        try:
            if len(df) < 20:
                return {'signal': 'neutral', 'confidence': 0.1, 'strength': 0.1}
            
            # Calculate basic indicators
            sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = df['Close'].rolling(window=min(50, len(df))).mean().iloc[-1]
            current_price = df['Close'].iloc[-1]
            
            # Price trend
            price_vs_sma20 = (current_price - sma_20) / sma_20
            price_vs_sma50 = (current_price - sma_50) / sma_50
            
            # Recent price action
            recent_change = df['Close'].pct_change(periods=5).iloc[-1]
            volatility = df['Close'].rolling(window=20).std().iloc[-1] / current_price
            
            # Determine signal
            signal_score = 0
            signal_score += 1 if price_vs_sma20 > 0.01 else -1 if price_vs_sma20 < -0.01 else 0
            signal_score += 1 if price_vs_sma50 > 0.01 else -1 if price_vs_sma50 < -0.01 else 0
            signal_score += 1 if recent_change > 0.005 else -1 if recent_change < -0.005 else 0
            
            # Convert to signal
            if signal_score >= 2:
                signal = 'buy'
                confidence = min(0.8, 0.5 + abs(signal_score) * 0.1)
            elif signal_score <= -2:
                signal = 'sell'
                confidence = min(0.8, 0.5 + abs(signal_score) * 0.1)
            else:
                signal = 'neutral'
                confidence = 0.3
            
            # Adjust confidence based on volatility
            confidence *= (1 - min(0.5, volatility * 10))
            
            strength = abs(signal_score) / 3.0  # Normalize strength
            
            return {
                'signal': signal,
                'confidence': max(0.1, confidence),
                'strength': max(0.1, strength)
            }
            
        except Exception as e:
            print(f"Warning: Error analyzing timeframe data: {e}")
            return {'signal': 'neutral', 'confidence': 0.1, 'strength': 0.1}
    
    def _generate_synthetic_signals(self, symbol: str, signal_data: Dict[str, Any]) -> List[TimeframeSignal]:
        """Generate synthetic signals when no market data is available"""
        timeframe_signals = []
        base_signal = signal_data.get('signal', 'neutral')
        base_confidence = signal_data.get('confidence', 0.5)
        
        for timeframe in self.timeframes:
            # Add some variance to simulate different timeframe perspectives
            confidence_variance = np.random.normal(0, 0.1)
            tf_confidence = max(0.1, min(0.9, base_confidence + confidence_variance))
            
            # Sometimes different timeframes disagree
            signal_agree_prob = 0.7  # 70% chance timeframes agree
            if np.random.random() > signal_agree_prob:
                # Disagreement - use opposite or neutral signal
                if base_signal == 'buy':
                    tf_signal = np.random.choice(['sell', 'neutral'], p=[0.3, 0.7])
                elif base_signal == 'sell':
                    tf_signal = np.random.choice(['buy', 'neutral'], p=[0.3, 0.7])
                else:
                    tf_signal = np.random.choice(['buy', 'sell'], p=[0.5, 0.5])
                tf_confidence *= 0.6  # Lower confidence for disagreeing signals
            else:
                tf_signal = base_signal
            
            timeframe_signals.append(TimeframeSignal(
                timeframe=timeframe,
                signal=tf_signal,
                confidence=tf_confidence,
                strength=tf_confidence,  # Use confidence as strength proxy
                timestamp=pd.Timestamp.now()
            ))
        
        return timeframe_signals
    
    def _calculate_consensus(self, timeframe_signals: List[TimeframeSignal]) -> float:
        """Calculate consensus score across timeframes"""
        if not timeframe_signals:
            return 0.0
        
        weighted_scores = []
        total_weight = 0
        
        for signal in timeframe_signals:
            weight = self.timeframe_weights.get(signal.timeframe, 0.3)
            
            # Convert signal to numeric score
            if signal.signal == 'buy':
                score = signal.confidence
            elif signal.signal == 'sell':
                score = -signal.confidence
            else:  # neutral
                score = 0
            
            weighted_scores.append(score * weight)
            total_weight += weight
        
        consensus = sum(weighted_scores) / max(total_weight, 0.01)
        return max(-1.0, min(1.0, consensus))  # Clamp to [-1, 1]
    
    def _determine_overall_result(self, consensus_score: float, 
                                timeframe_signals: List[TimeframeSignal]) -> ValidationResult:
        """Determine overall validation result"""
        try:
            # Count signal types
            buy_signals = sum(1 for s in timeframe_signals if s.signal == 'buy')
            sell_signals = sum(1 for s in timeframe_signals if s.signal == 'sell')
            total_signals = len(timeframe_signals)
            
            if total_signals == 0:
                return ValidationResult.INVALID
            
            # Strong consensus thresholds
            strong_threshold = 0.7
            moderate_threshold = 0.4
            
            if consensus_score > strong_threshold and buy_signals >= total_signals * 0.7:
                return ValidationResult.STRONG_BUY
            elif consensus_score > moderate_threshold:
                return ValidationResult.BUY
            elif consensus_score < -strong_threshold and sell_signals >= total_signals * 0.7:
                return ValidationResult.STRONG_SELL
            elif consensus_score < -moderate_threshold:
                return ValidationResult.SELL
            else:
                return ValidationResult.NEUTRAL
                
        except Exception as e:
            print(f"Warning: Error determining overall result: {e}")
            return ValidationResult.NEUTRAL
    
    def _calculate_final_confidence(self, timeframe_signals: List[TimeframeSignal], 
                                  consensus_score: float) -> float:
        """Calculate final confidence score"""
        try:
            if not timeframe_signals:
                return 0.1
            
            # Average confidence across timeframes
            avg_confidence = np.mean([s.confidence for s in timeframe_signals])
            
            # Consensus strength (how aligned the signals are)
            consensus_strength = abs(consensus_score)
            
            # Agreement factor (how many signals agree)
            signal_counts = {'buy': 0, 'sell': 0, 'neutral': 0}
            for signal in timeframe_signals:
                signal_counts[signal.signal] += 1
            
            max_agreement = max(signal_counts.values())
            agreement_factor = max_agreement / len(timeframe_signals)
            
            # Final confidence combines multiple factors
            final_confidence = (avg_confidence * 0.4 + 
                              consensus_strength * 0.4 + 
                              agreement_factor * 0.2)
            
            return max(0.1, min(0.95, final_confidence))
            
        except Exception as e:
            print(f"Warning: Error calculating final confidence: {e}")
            return 0.5
    
    def _generate_validation_notes(self, timeframe_signals: List[TimeframeSignal], 
                                 consensus_score: float) -> List[str]:
        """Generate validation notes"""
        notes = []
        
        try:
            # Consensus analysis
            if abs(consensus_score) > 0.7:
                notes.append(f"Strong consensus across timeframes (score: {consensus_score:.2f})")
            elif abs(consensus_score) > 0.4:
                notes.append(f"Moderate consensus across timeframes (score: {consensus_score:.2f})")
            else:
                notes.append(f"Weak consensus - mixed signals across timeframes (score: {consensus_score:.2f})")
            
            # Signal distribution
            signal_counts = {'buy': 0, 'sell': 0, 'neutral': 0}
            for signal in timeframe_signals:
                signal_counts[signal.signal] += 1
            
            notes.append(f"Signal distribution: {signal_counts['buy']} BUY, {signal_counts['sell']} SELL, {signal_counts['neutral']} NEUTRAL")
            
            # High confidence timeframes
            high_conf_signals = [s for s in timeframe_signals if s.confidence > 0.7]
            if high_conf_signals:
                tf_list = [s.timeframe for s in high_conf_signals]
                notes.append(f"High confidence timeframes: {', '.join(tf_list)}")
            
            # Disagreement warning
            if len(set(s.signal for s in timeframe_signals)) > 2:
                notes.append("Warning: Significant disagreement between timeframes")
            
        except Exception as e:
            notes.append(f"Error generating notes: {e}")
        
        return notes
    
    def _default_validation_report(self) -> ValidationReport:
        """Return default validation report for error cases"""
        return ValidationReport(
            overall_result=ValidationResult.INVALID,
            confidence=0.1,
            timeframe_signals=[],
            consensus_score=0.0,
            validation_notes=["Error occurred during validation"]
        )
    
    def get_validation_summary(self, timeframe: str = None) -> Dict[str, Any]:
        """Get validation summary statistics"""
        try:
            if not self.validation_history:
                return {'total_validations': 0}
            
            recent_validations = self.validation_history[-100:]  # Last 100
            
            # Result distribution
            result_counts = {}
            confidence_scores = []
            consensus_scores = []
            
            for validation in recent_validations:
                report = validation['report']
                result = report.overall_result.value
                result_counts[result] = result_counts.get(result, 0) + 1
                confidence_scores.append(report.confidence)
                consensus_scores.append(abs(report.consensus_score))
            
            return {
                'total_validations': len(recent_validations),
                'result_distribution': result_counts,
                'average_confidence': np.mean(confidence_scores),
                'average_consensus': np.mean(consensus_scores),
                'configured_timeframes': self.timeframes,
                'timeframe_weights': self.timeframe_weights
            }
            
        except Exception as e:
            print(f"Warning: Error getting validation summary: {e}")
            return {'error': str(e)}
    
    def is_signal_valid(self, validation_report: ValidationReport, 
                       min_confidence: float = 0.6, min_consensus: float = 0.4) -> bool:
        """
        Check if a signal passes validation criteria
        
        Args:
            validation_report: Validation report
            min_confidence: Minimum confidence threshold
            min_consensus: Minimum consensus threshold
            
        Returns:
            True if signal is valid for trading
        """
        try:
            if validation_report.overall_result == ValidationResult.INVALID:
                return False
            
            if validation_report.confidence < min_confidence:
                return False
            
            if abs(validation_report.consensus_score) < min_consensus:
                return False
            
            # Additional checks
            if validation_report.overall_result == ValidationResult.NEUTRAL:
                return False
            
            return True
            
        except Exception as e:
            print(f"Warning: Error checking signal validity: {e}")
            return False