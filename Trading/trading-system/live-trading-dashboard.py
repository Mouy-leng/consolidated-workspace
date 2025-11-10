#!/usr/bin/env python3
"""
Live Multi-Symbol Trading Dashboard
Real-time monitoring of all 10+ symbols with automatic alerts
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor
import threading

class LiveTradingDashboard:
    def __init__(self):
        self.symbols = {
            "XAUUSD": "GC=F",      # Gold
            "EURUSD": "EURUSD=X",  # Euro/USD
            "GBPUSD": "GBPUSD=X",  # Pound/USD
            "USDJPY": "USDJPY=X",  # USD/Yen
            "USDCHF": "USDCHF=X",  # USD/Swiss Franc
            "AUDUSD": "AUDUSD=X",  # Australian Dollar/USD
            "NZDUSD": "NZDUSD=X",  # New Zealand Dollar/USD
            "USDCAD": "USDCAD=X",  # USD/Canadian Dollar
            "EURJPY": "EURJPY=X",  # Euro/Yen
            "GBPJPY": "GBPJPY=X"   # Pound/Yen
        }
        
        self.symbol_data = {}
        self.alerts = []
        self.is_running = False
        
    def get_live_data(self, symbol: str, yahoo_symbol: str) -> dict:
        """Get live market data and analysis for a symbol"""
        try:
            # Get current data
            data = yf.download(yahoo_symbol, period="1d", interval="5m", progress=False)
            
            if data.empty or len(data) < 20:
                return {"symbol": symbol, "status": "no_data", "price": 0}
            
            # Handle multi-level columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            current_price = float(close.iloc[-1])
            
            # Quick technical analysis
            # RSI (14-period)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50
            
            # Simple moving averages
            sma20 = close.rolling(window=20).mean()
            current_sma20 = float(sma20.iloc[-1]) if not sma20.empty else current_price
            
            # Price change
            prev_close = float(close.iloc[-2]) if len(close) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
            
            # ATR for volatility
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean()
            current_atr = float(atr.iloc[-1]) if not atr.empty else 0.001
            
            # Trend analysis
            if current_price > current_sma20:
                trend = "BULLISH" if change > 0 else "MIXED"
            else:
                trend = "BEARISH" if change < 0 else "MIXED"
            
            # Signal strength
            signal_strength = 0
            signal_type = "HOLD"
            
            # RSI signals
            if current_rsi < 30:
                signal_strength += 0.4
                signal_type = "BUY"
            elif current_rsi > 70:
                signal_strength += 0.4
                signal_type = "SELL"
            
            # Trend confirmation
            if trend == "BULLISH" and signal_type == "BUY":
                signal_strength += 0.3
            elif trend == "BEARISH" and signal_type == "SELL":
                signal_strength += 0.3
            
            # Calculate potential SL/TP
            if signal_type == "BUY":
                stop_loss = current_price - (current_atr * 2)
                take_profit = current_price + (current_atr * 3)
            elif signal_type == "SELL":
                stop_loss = current_price + (current_atr * 2)
                take_profit = current_price - (current_atr * 3)
            else:
                stop_loss = take_profit = 0
            
            return {
                "symbol": symbol,
                "price": round(current_price, 5),
                "change": round(change, 5),
                "change_pct": round(change_pct, 2),
                "rsi": round(current_rsi, 1),
                "trend": trend,
                "signal": signal_type,
                "strength": round(signal_strength, 2),
                "atr": round(current_atr, 5),
                "stop_loss": round(stop_loss, 5),
                "take_profit": round(take_profit, 5),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "status": "active"
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "status": "error",
                "error": str(e),
                "price": 0,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
    
    def update_all_symbols(self):
        """Update data for all symbols concurrently"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.get_live_data, symbol, yahoo_symbol): symbol 
                for symbol, yahoo_symbol in self.symbols.items()
            }
            
            for future in futures:
                try:
                    result = future.result(timeout=10)
                    self.symbol_data[result["symbol"]] = result
                except Exception as e:
                    symbol = futures[future]
                    self.symbol_data[symbol] = {
                        "symbol": symbol,
                        "status": "timeout",
                        "error": str(e),
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
    
    def check_alerts(self):
        """Check for trading alerts"""
        new_alerts = []
        
        for symbol, data in self.symbol_data.items():
            if data.get("status") != "active":
                continue
            
            # Strong buy/sell signals
            if data.get("strength", 0) >= 0.7:
                alert = {
                    "symbol": symbol,
                    "type": "STRONG_SIGNAL",
                    "signal": data["signal"],
                    "strength": data["strength"],
                    "price": data["price"],
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                new_alerts.append(alert)
            
            # Extreme RSI
            if data.get("rsi", 50) < 20:
                alert = {
                    "symbol": symbol,
                    "type": "RSI_OVERSOLD",
                    "rsi": data["rsi"],
                    "price": data["price"],
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                new_alerts.append(alert)
            elif data.get("rsi", 50) > 80:
                alert = {
                    "symbol": symbol,
                    "type": "RSI_OVERBOUGHT",
                    "rsi": data["rsi"],
                    "price": data["price"],
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                new_alerts.append(alert)
        
        # Keep only last 10 alerts
        self.alerts.extend(new_alerts)
        self.alerts = self.alerts[-10:]
        
        return new_alerts
    
    def display_dashboard(self):
        """Display the live trading dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("🚀 LIVE MULTI-SYMBOL TRADING DASHBOARD")
        print("=" * 80)
        print(f"⏰ Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏦 FBS Account: 241926287 | Server: FBS-Real-4")
        print("")
        
        # Summary stats
        active_signals = [d for d in self.symbol_data.values() if d.get("signal") in ["BUY", "SELL"]]
        strong_signals = [d for d in active_signals if d.get("strength", 0) >= 0.7]
        
        print(f"📊 MARKET OVERVIEW")
        print(f"   Active Symbols: {len(self.symbol_data)}")
        print(f"   🎯 Trading Signals: {len(active_signals)}")
        print(f"   ⚡ Strong Signals: {len(strong_signals)}")
        print("")
        
        # Symbol table
        print("📈 SYMBOL ANALYSIS")
        print("-" * 80)
        print(f"{'Symbol':<8} {'Price':<10} {'Change%':<8} {'RSI':<6} {'Trend':<8} {'Signal':<6} {'Strength':<8}")
        print("-" * 80)
        
        for symbol in sorted(self.symbols.keys()):
            data = self.symbol_data.get(symbol, {})
            
            if data.get("status") == "active":
                price = f"{data['price']:.5f}"
                change_pct = f"{data['change_pct']:+.2f}%"
                rsi = f"{data['rsi']:.1f}"
                trend = data['trend']
                signal = data['signal']
                strength = f"{data['strength']:.2f}" if data['strength'] > 0 else "-"
                
                # Color coding based on signal
                if signal == "BUY":
                    signal_color = "🟢"
                elif signal == "SELL":
                    signal_color = "🔴"
                else:
                    signal_color = "⚪"
                
                print(f"{symbol:<8} {price:<10} {change_pct:<8} {rsi:<6} {trend:<8} {signal_color}{signal:<5} {strength:<8}")
            else:
                status = data.get("status", "unknown")
                print(f"{symbol:<8} {'---':<10} {'---':<8} {'---':<6} {'---':<8} {'⚫---':<6} {'---':<8}")
        
        print("-" * 80)
        
        # Trading opportunities
        if strong_signals:
            print("\n🎯 IMMEDIATE TRADING OPPORTUNITIES")
            print("-" * 50)
            for signal in strong_signals:
                print(f"💎 {signal['symbol']} {signal['signal']} - Strength: {signal['strength']:.2f}")
                print(f"   Entry: {signal['price']:.5f}")
                print(f"   SL: {signal['stop_loss']:.5f} | TP: {signal['take_profit']:.5f}")
                print(f"   RSI: {signal['rsi']:.1f} | Trend: {signal['trend']}")
                print("")
        
        # Recent alerts
        if self.alerts:
            print("🚨 RECENT ALERTS")
            print("-" * 40)
            for alert in self.alerts[-5:]:
                if alert["type"] == "STRONG_SIGNAL":
                    print(f"⚡ {alert['timestamp']} - {alert['symbol']} {alert['signal']} ({alert['strength']:.2f})")
                elif "RSI" in alert["type"]:
                    print(f"📊 {alert['timestamp']} - {alert['symbol']} {alert['type']} (RSI: {alert.get('rsi', 0):.1f})")
        
        print("\n" + "=" * 80)
        print("🤖 Auto Trading: ACTIVE | 💤 Monitoring 24/5 | 🔄 Updates every 30 seconds")
        print("Press Ctrl+C to stop monitoring...")
    
    def run_dashboard(self):
        """Run the live dashboard"""
        self.is_running = True
        
        print("🚀 Starting Live Trading Dashboard...")
        print("📊 Loading market data for all symbols...")
        
        while self.is_running:
            try:
                # Update all symbol data
                self.update_all_symbols()
                
                # Check for alerts
                new_alerts = self.check_alerts()
                
                # Display dashboard
                self.display_dashboard()
                
                # Wait 30 seconds
                time.sleep(30)
                
            except KeyboardInterrupt:
                self.is_running = False
                print("\n\n⏹️ Dashboard stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Dashboard error: {e}")
                time.sleep(10)

def main():
    """Main function"""
    dashboard = LiveTradingDashboard()
    
    try:
        dashboard.run_dashboard()
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed")

if __name__ == "__main__":
    main()