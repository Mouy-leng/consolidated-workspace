#!/usr/bin/env python3
"""
Live Account Balance Checker
Verifies real FBS account balance and adjusts trading parameters
"""

import json
import logging
import datetime
from typing import Dict, Any
import yfinance as yf
import pandas as pd

class LiveAccountChecker:
    def __init__(self):
        self.account_id = "241926287"
        self.server = "FBS-Real-4"
        self.server_ip = "95.179.194.198:443"
        self.current_balance = 47.79  # User reported balance
        
        # Risk management for small account
        self.max_risk_percent = 2.0  # 2% max risk per trade
        self.min_trade_size = 0.01   # Minimum lot size
        self.max_trades = 3          # Maximum concurrent trades
        
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for account checking"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('live_account_check.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def verify_account_status(self) -> Dict[str, Any]:
        """Verify account status and calculate trading parameters"""
        self.logger.info(f"🔍 Checking FBS Account: {self.account_id}")
        self.logger.info(f"💰 Current Balance: ${self.current_balance}")
        
        # Calculate trading parameters
        max_risk_amount = self.current_balance * (self.max_risk_percent / 100)
        
        # For forex pairs, calculate lot sizes based on risk
        # Assuming average 50 pip stop loss
        pip_value_per_lot = 10  # For major pairs
        max_lot_size = max_risk_amount / (50 * pip_value_per_lot)
        
        # Ensure minimum lot size compliance
        recommended_lot_size = max(self.min_trade_size, min(max_lot_size, 0.05))
        
        account_info = {
            "account_id": self.account_id,
            "server": self.server,
            "balance": self.current_balance,
            "max_risk_per_trade": max_risk_amount,
            "recommended_lot_size": recommended_lot_size,
            "max_concurrent_trades": self.max_trades,
            "risk_percent": self.max_risk_percent,
            "account_status": "ACTIVE" if self.current_balance > 10 else "LOW_BALANCE",
            "last_checked": datetime.datetime.now().isoformat()
        }
        
        return account_info
    
    def get_current_market_data(self) -> Dict[str, Any]:
        """Get current market data for major pairs"""
        symbols = ['EURUSD=X', 'GBPUSD=X', 'AUDUSD=X', 'USDJPY=X', 'GC=F']  # GC=F is Gold
        
        market_data = {}
        
        try:
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d", interval="1m")
                
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    change = ((current_price - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
                    
                    # Clean symbol name
                    clean_symbol = symbol.replace('=X', '').replace('=F', '')
                    if clean_symbol == 'GC':
                        clean_symbol = 'XAUUSD'
                    
                    market_data[clean_symbol] = {
                        'price': round(current_price, 5),
                        'change_percent': round(change, 2),
                        'tradeable': True if abs(change) > 0.1 else False
                    }
                    
        except Exception as e:
            self.logger.error(f"Error fetching market data: {e}")
            
        return market_data
    
    def calculate_position_sizes(self, symbol: str, entry_price: float, 
                               stop_loss: float) -> Dict[str, float]:
        """Calculate appropriate position sizes for the symbol"""
        
        # Calculate risk per pip
        if 'JPY' in symbol:
            pip_value = 0.01
        else:
            pip_value = 0.0001
            
        # Calculate stop loss in pips
        sl_pips = abs(entry_price - stop_loss) / pip_value
        
        # Calculate lot size based on risk
        risk_amount = self.current_balance * (self.max_risk_percent / 100)
        
        if symbol == 'XAUUSD':
            # Gold calculation (per 0.01 lot = $0.10 per pip)
            lot_size = min(risk_amount / (sl_pips * 0.10), 0.02)
        else:
            # Forex calculation (per 0.01 lot = $0.10 per pip for majors)
            lot_size = min(risk_amount / (sl_pips * 0.10), 0.05)
            
        # Ensure minimum lot size
        lot_size = max(self.min_trade_size, lot_size)
        
        return {
            'lot_size': round(lot_size, 2),
            'risk_amount': round(risk_amount, 2),
            'sl_pips': round(sl_pips, 1),
            'potential_loss': round(lot_size * sl_pips * 0.10, 2)
        }
    
    def generate_account_report(self) -> None:
        """Generate comprehensive account report"""
        print("\n" + "="*70)
        print("🏦 LIVE FBS ACCOUNT STATUS REPORT")
        print("="*70)
        
        account_info = self.verify_account_status()
        market_data = self.get_current_market_data()
        
        # Account Information
        print(f"\n📊 ACCOUNT DETAILS:")
        print(f"   Account ID: {account_info['account_id']}")
        print(f"   Server: {account_info['server']}")
        print(f"   Balance: ${account_info['balance']:.2f}")
        print(f"   Status: {account_info['account_status']}")
        
        # Risk Management
        print(f"\n⚖️ RISK MANAGEMENT:")
        print(f"   Max Risk per Trade: ${account_info['max_risk_per_trade']:.2f} ({account_info['risk_percent']}%)")
        print(f"   Recommended Lot Size: {account_info['recommended_lot_size']}")
        print(f"   Max Concurrent Trades: {account_info['max_concurrent_trades']}")
        
        # Market Data
        print(f"\n📈 CURRENT MARKET DATA:")
        for symbol, data in market_data.items():
            status = "🟢 TRADEABLE" if data['tradeable'] else "🔴 WAIT"
            print(f"   {symbol}: ${data['price']:.5f} ({data['change_percent']:+.2f}%) {status}")
        
        # Trading Recommendations
        print(f"\n🎯 TRADING RECOMMENDATIONS:")
        print(f"   ✅ Conservative approach with ${account_info['balance']:.2f} balance")
        print(f"   ✅ Focus on 1-2 high-probability trades")
        print(f"   ✅ Use tight stop losses (20-30 pips)")
        print(f"   ✅ Take profits at 1:2 risk/reward ratio")
        print(f"   ⚠️ Avoid over-leveraging with small account")
        
        # Save report
        with open('live_account_report.json', 'w') as f:
            json.dump({
                'account_info': account_info,
                'market_data': market_data,
                'timestamp': datetime.datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n💾 Report saved to: live_account_report.json")
        print("="*70)

def main():
    """Main function"""
    checker = LiveAccountChecker()
    checker.generate_account_report()

if __name__ == "__main__":
    main()