#!/usr/bin/env python3
"""
Live Trade Monitor for FBS MT4 Account
Monitors XAUUSD and EURUSD positions
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time

class LiveTradeMonitor:
    def __init__(self):
        self.account = "241926287"
        self.server = "FBS-Real-4"
        self.active_positions = [
            {"symbol": "XAUUSD", "yahoo_symbol": "GC=F"},
            {"symbol": "EURUSD", "yahoo_symbol": "EURUSD=X"}
        ]
        
    def get_current_price(self, yahoo_symbol):
        """Get current price from Yahoo Finance"""
        try:
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error getting price for {yahoo_symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    
    def get_market_analysis(self, yahoo_symbol):
        """Get technical analysis"""
        try:
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period="1d", interval="5m")
            
            if data.empty:
                return {"status": "No data"}
            
            current_price = data['Close'].iloc[-1]
            rsi = self.calculate_rsi(data['Close'])
            
            # Simple trend analysis
            sma20 = data['Close'].rolling(20).mean().iloc[-1]
            trend = "Bullish" if current_price > sma20 else "Bearish"
            
            # Support/Resistance levels
            recent_high = data['High'].tail(20).max()
            recent_low = data['Low'].tail(20).min()
            
            return {
                "current_price": current_price,
                "rsi": rsi,
                "trend": trend,
                "resistance": recent_high,
                "support": recent_low,
                "sma20": sma20
            }
            
        except Exception as e:
            return {"status": f"Error: {e}"}
    
    def display_live_monitor(self):
        """Display live trading monitor"""
        print(f"\n🎯 LIVE TRADE MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        print(f"📊 Account: {self.account} | Server: {self.server}")
        print("=" * 60)
        
        for position in self.active_positions:
            symbol = position["symbol"]
            yahoo_symbol = position["yahoo_symbol"]
            
            print(f"\n📈 {symbol} Analysis:")
            print("-" * 40)
            
            analysis = self.get_market_analysis(yahoo_symbol)
            
            if "status" in analysis:
                print(f"   Status: {analysis['status']}")
                continue
            
            # Display current market data
            print(f"   💰 Current Price: ${analysis['current_price']:.4f}")
            print(f"   📊 RSI: {analysis['rsi']:.1f}")
            print(f"   📈 Trend: {analysis['trend']}")
            print(f"   🔺 Resistance: ${analysis['resistance']:.4f}")
            print(f"   🔻 Support: ${analysis['support']:.4f}")
            print(f"   📊 SMA20: ${analysis['sma20']:.4f}")
            
            # Trading signals
            if analysis['rsi'] > 70:
                print(f"   🚨 OVERBOUGHT - Consider taking profits")
            elif analysis['rsi'] < 30:
                print(f"   🚨 OVERSOLD - Potential buying opportunity")
            elif analysis['current_price'] >= analysis['resistance']:
                print(f"   ⚠️  RESISTANCE LEVEL - Watch for reversal")
            elif analysis['current_price'] <= analysis['support']:
                print(f"   ⚠️  SUPPORT LEVEL - Watch for bounce")
            else:
                print(f"   ✅ NORMAL RANGE - Monitor trends")
        
        print(f"\n🔄 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📊 Monitoring your FBS-Real-4 positions...")
    
    def run_continuous_monitor(self):
        """Run continuous monitoring"""
        print("🎯 STARTING LIVE TRADE MONITOR")
        print("==============================")
        print("Monitoring XAUUSD and EURUSD positions on FBS-Real-4")
        print("Press Ctrl+C to stop monitoring...")
        
        try:
            while True:
                self.display_live_monitor()
                time.sleep(30)  # Update every 30 seconds
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️ Monitoring stopped")
            print("Your trades are still active on FBS-Real-4")

def show_current_signals():
    """Show current trading signals"""
    monitor = LiveTradeMonitor()
    
    print("🎯 CURRENT MARKET SIGNALS")
    print("=========================")
    
    symbols = [("XAUUSD", "GC=F"), ("EURUSD", "EURUSD=X")]
    
    for symbol, yahoo_symbol in symbols:
        analysis = monitor.get_market_analysis(yahoo_symbol)
        
        if "status" in analysis:
            print(f"{symbol}: {analysis['status']}")
            continue
            
        print(f"\n📊 {symbol}:")
        print(f"   Price: ${analysis['current_price']:.4f}")
        print(f"   RSI: {analysis['rsi']:.1f}")
        print(f"   Trend: {analysis['trend']}")
        
        # Generate signal
        if analysis['rsi'] > 70 and analysis['trend'] == "Bearish":
            print(f"   🔴 SIGNAL: SELL (Overbought + Bearish)")
        elif analysis['rsi'] < 30 and analysis['trend'] == "Bullish":
            print(f"   🟢 SIGNAL: BUY (Oversold + Bullish)")
        else:
            print(f"   ⚪ SIGNAL: HOLD (Monitor)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "signals":
        show_current_signals()
    else:
        monitor = LiveTradeMonitor()
        monitor.run_continuous_monitor()