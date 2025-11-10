"""
Position Sizing and Risk Management for GenX FX Trading System
Manages position sizes, risk limits, and portfolio risk
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Try to import pandas and numpy, but provide fallbacks if not available
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    NUMPY_AVAILABLE = False
    # Create simple fallback classes
    class pd:
        @staticmethod
        def Timestamp():
            return datetime.now()
    
    class np:
        @staticmethod
        def round(x, decimals=0):
            return round(x, decimals)

class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class PositionInfo:
    """Position information structure"""
    symbol: str
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    risk_percent: float
    max_loss: float

class PositionSizer:
    """
    Position sizing and risk management for forex trading
    """
    
    def __init__(self, account_balance: float = 10000.0, max_risk_per_trade: float = 0.02, 
                 max_portfolio_risk: float = 0.20, risk_level: RiskLevel = RiskLevel.MODERATE):
        """
        Initialize position sizer
        
        Args:
            account_balance: Total account balance
            max_risk_per_trade: Maximum risk per trade as percentage (0.02 = 2%)
            max_portfolio_risk: Maximum portfolio risk as percentage (0.20 = 20%)
            risk_level: Risk management level
        """
        self.account_balance = account_balance
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.risk_level = risk_level
        
        # Risk multipliers based on risk level
        self.risk_multipliers = {
            RiskLevel.CONSERVATIVE: 0.5,
            RiskLevel.MODERATE: 1.0,
            RiskLevel.AGGRESSIVE: 2.0
        }
        
        # Active positions tracking
        self.active_positions = {}
        self.position_history = []
        
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float,
                              confidence: float = 1.0, current_positions: int = 0) -> PositionInfo:
        """
        Calculate optimal position size based on risk management rules
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the position
            stop_loss: Stop loss price
            confidence: Signal confidence (0-1)
            current_positions: Number of current open positions
            
        Returns:
            PositionInfo with calculated position details
        """
        try:
            # Validate inputs
            if entry_price <= 0 or stop_loss <= 0:
                raise ValueError("Entry price and stop loss must be positive")
            
            if confidence < 0 or confidence > 1:
                confidence = max(0, min(1, confidence))  # Clamp to 0-1
            
            # Calculate risk per pip/point
            price_difference = abs(entry_price - stop_loss)
            if price_difference == 0:
                price_difference = entry_price * 0.01  # Default 1% if no stop loss
            
            # Adjust risk based on confidence and risk level
            base_risk = self.max_risk_per_trade
            risk_multiplier = self.risk_multipliers[self.risk_level]
            adjusted_risk = base_risk * risk_multiplier * confidence
            
            # Reduce risk if portfolio is concentrated
            portfolio_risk_adjustment = self._calculate_portfolio_risk_adjustment(current_positions)
            final_risk = adjusted_risk * portfolio_risk_adjustment
            
            # Calculate risk amount in account currency
            risk_amount = self.account_balance * final_risk
            
            # Calculate position size
            position_size = risk_amount / price_difference
            
            # Apply position size limits
            position_size = self._apply_position_limits(position_size, entry_price)
            
            # Calculate actual risk and take profit
            actual_risk = position_size * price_difference
            take_profit = self._calculate_take_profit(entry_price, stop_loss, confidence)
            
            return PositionInfo(
                symbol=symbol,
                entry_price=entry_price,
                position_size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=actual_risk,
                risk_percent=actual_risk / self.account_balance,
                max_loss=actual_risk
            )
            
        except Exception as e:
            print(f"Warning: Error calculating position size: {e}")
            return self._default_position_info(symbol, entry_price, stop_loss)
    
    def _calculate_portfolio_risk_adjustment(self, current_positions: int) -> float:
        """Calculate risk adjustment based on portfolio concentration"""
        if current_positions == 0:
            return 1.0
        elif current_positions <= 3:
            return 0.8
        elif current_positions <= 5:
            return 0.6
        else:
            return 0.4  # Heavily reduce risk when overconcentrated
    
    def _apply_position_limits(self, position_size: float, entry_price: float) -> float:
        """Apply minimum and maximum position size limits"""
        # Minimum position size (e.g., 0.01 lots in forex)
        min_position = 0.01
        
        # Maximum position size (e.g., 5% of account balance worth)
        max_position_value = self.account_balance * 0.05
        max_position = max_position_value / entry_price
        
        # Apply limits
        position_size = max(min_position, min(position_size, max_position))
        
        return round(position_size, 2)  # Round to 2 decimal places
    
    def _calculate_take_profit(self, entry_price: float, stop_loss: float, confidence: float) -> float:
        """Calculate take profit based on risk-reward ratio"""
        stop_distance = abs(entry_price - stop_loss)
        
        # Base risk-reward ratio
        base_rr_ratio = 2.0  # 1:2 risk-reward
        
        # Adjust based on confidence
        rr_ratio = base_rr_ratio * (1 + confidence * 0.5)  # Up to 1:3 for high confidence
        
        # Calculate take profit
        if entry_price > stop_loss:  # Long position
            take_profit = entry_price + (stop_distance * rr_ratio)
        else:  # Short position
            take_profit = entry_price - (stop_distance * rr_ratio)
        
        return round(take_profit, 5)  # Round to 5 decimal places for forex
    
    def _default_position_info(self, symbol: str, entry_price: float, stop_loss: float) -> PositionInfo:
        """Return default position info in case of errors"""
        return PositionInfo(
            symbol=symbol,
            entry_price=entry_price,
            position_size=0.01,  # Minimum position
            stop_loss=stop_loss,
            take_profit=entry_price * 1.02,  # 2% take profit
            risk_amount=self.account_balance * 0.01,  # 1% risk
            risk_percent=0.01,
            max_loss=self.account_balance * 0.01
        )
    
    def add_position(self, position_info: PositionInfo) -> bool:
        """
        Add a position to tracking
        
        Args:
            position_info: Position information
            
        Returns:
            True if position can be added within risk limits
        """
        try:
            # Check if adding this position exceeds portfolio risk
            total_risk = self._calculate_total_portfolio_risk()
            new_total_risk = total_risk + position_info.risk_percent
            
            if new_total_risk > self.max_portfolio_risk:
                print(f"Warning: Position rejected - would exceed portfolio risk limit ({new_total_risk:.2%} > {self.max_portfolio_risk:.2%})")
                return False
            
            # Add position to tracking
            self.active_positions[position_info.symbol] = position_info
            return True
            
        except Exception as e:
            print(f"Warning: Error adding position: {e}")
            return False
    
    def remove_position(self, symbol: str, exit_price: float = None, profit_loss: float = None) -> bool:
        """
        Remove a position from tracking
        
        Args:
            symbol: Symbol to remove
            exit_price: Exit price (optional)
            profit_loss: Realized P&L (optional)
            
        Returns:
            True if position was removed
        """
        try:
            if symbol in self.active_positions:
                position = self.active_positions[symbol]
                
                # Calculate P&L if exit price provided
                if exit_price is not None and profit_loss is None:
                    profit_loss = (exit_price - position.entry_price) * position.position_size
                
                # Add to history
                self.position_history.append({
                    'symbol': symbol,
                    'entry_price': position.entry_price,
                    'exit_price': exit_price,
                    'position_size': position.position_size,
                    'profit_loss': profit_loss,
                    'exit_time': pd.Timestamp.now() if PANDAS_AVAILABLE else datetime.now()
                })
                
                # Remove from active positions
                del self.active_positions[symbol]
                return True
            
            return False
            
        except Exception as e:
            print(f"Warning: Error removing position: {e}")
            return False
    
    def _calculate_total_portfolio_risk(self) -> float:
        """Calculate total portfolio risk from active positions"""
        total_risk = 0.0
        for position in self.active_positions.values():
            total_risk += position.risk_percent
        return total_risk
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get current portfolio risk summary
        
        Returns:
            Dictionary with portfolio metrics
        """
        try:
            total_risk = self._calculate_total_portfolio_risk()
            total_exposure = sum(pos.position_size * pos.entry_price for pos in self.active_positions.values())
            
            return {
                'account_balance': self.account_balance,
                'active_positions': len(self.active_positions),
                'total_risk_percent': total_risk,
                'total_risk_amount': total_risk * self.account_balance,
                'total_exposure': total_exposure,
                'remaining_risk_capacity': max(0, self.max_portfolio_risk - total_risk),
                'risk_utilization': total_risk / self.max_portfolio_risk if self.max_portfolio_risk > 0 else 0,
                'positions': list(self.active_positions.keys())
            }
            
        except Exception as e:
            print(f"Warning: Error calculating portfolio summary: {e}")
            return {}
    
    def update_account_balance(self, new_balance: float) -> None:
        """Update account balance and recalculate risk limits"""
        try:
            if new_balance <= 0:
                raise ValueError("Account balance must be positive")
                
            self.account_balance = new_balance
            
            # Update existing position risk percentages
            for position in self.active_positions.values():
                position.risk_percent = position.risk_amount / new_balance
                
        except Exception as e:
            print(f"Warning: Error updating account balance: {e}")
    
    def can_open_position(self, risk_amount: float) -> bool:
        """
        Check if a new position can be opened within risk limits
        
        Args:
            risk_amount: Risk amount for the new position
            
        Returns:
            True if position can be opened
        """
        try:
            if risk_amount <= 0:
                return False
                
            current_risk = self._calculate_total_portfolio_risk()
            new_risk_percent = risk_amount / self.account_balance
            total_risk = current_risk + new_risk_percent
            
            return total_risk <= self.max_portfolio_risk
            
        except Exception as e:
            print(f"Warning: Error checking position capacity: {e}")
            return False
    
    def get_risk_metrics(self) -> Dict[str, float]:
        """Get detailed risk metrics"""
        try:
            portfolio_summary = self.get_portfolio_summary()
            
            # Calculate additional metrics
            active_positions = portfolio_summary.get('active_positions', 0)
            total_risk_percent = portfolio_summary.get('total_risk_percent', 0)
            
            avg_position_risk = (total_risk_percent / max(1, active_positions))
            
            risk_concentration = (total_risk_percent / 
                                self.max_portfolio_risk) if self.max_portfolio_risk > 0 else 0
            
            return {
                'max_risk_per_trade': self.max_risk_per_trade,
                'max_portfolio_risk': self.max_portfolio_risk,
                'current_portfolio_risk': total_risk_percent,
                'average_position_risk': avg_position_risk,
                'risk_concentration': risk_concentration,
                'remaining_capacity': portfolio_summary.get('remaining_risk_capacity', 0),
                'risk_multiplier': self.risk_multipliers[self.risk_level]
            }
            
        except Exception as e:
            print(f"Warning: Error calculating risk metrics: {e}")
            return {}
    
    def set_risk_level(self, risk_level: RiskLevel) -> None:
        """Update risk level"""
        self.risk_level = risk_level
        
    def reset_positions(self) -> None:
        """Reset all position tracking (for testing/simulation)"""
        self.active_positions = {}
        self.position_history = []
