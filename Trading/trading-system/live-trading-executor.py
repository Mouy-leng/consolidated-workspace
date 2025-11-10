#!/usr/bin/env python3
"""
Live Trading Execution Helper
Manual trading execution based on signal generator
"""

import json
import time
from datetime import datetime
import subprocess
import sys

def get_latest_signal():
    """Get the latest trading signal"""
    try:
        # Run signal generator to get fresh signal
        print("🔍 Generating fresh trading signal...")
        result = subprocess.run([sys.executable, "trading-signal-generator.py"], 
                              input="1\n", text=True, capture_output=True)
        
        if "BUY Signal" in result.stdout or "SELL Signal" in result.stdout:
            return parse_signal_from_output(result.stdout)
        else:
            print("❌ No strong signals detected at this time")
            return None
    except Exception as e:
        print(f"❌ Error getting signal: {e}")
        return None

def parse_signal_from_output(output):
    """Parse signal from command output"""
    lines = output.split('\n')
    signal = {}
    
    for line in lines:
        if "BUY Signal:" in line or "SELL Signal:" in line:
            signal['action'] = "BUY" if "BUY" in line else "SELL"
        elif "Entry:" in line:
            signal['entry'] = line.split('$')[1].strip() if '$' in line else ""
        elif "Stop Loss:" in line:
            signal['sl'] = line.split('$')[1].strip() if '$' in line else ""
        elif "Take Profit:" in line:
            signal['tp'] = line.split('$')[1].strip() if '$' in line else ""
        elif "RSI:" in line:
            signal['rsi'] = line.split('RSI:')[1].strip()
    
    if 'action' in signal:
        signal['symbol'] = 'XAUUSD'  # Default symbol
        signal['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return signal
    
    return None

def display_trading_instructions(signal):
    """Display manual trading instructions"""
    print("\n" + "="*50)
    print("🚀 LIVE TRADING EXECUTION INSTRUCTIONS")
    print("="*50)
    print()
    
    print(f"📊 Signal Details:")
    print(f"   Symbol: {signal.get('symbol', 'XAUUSD')}")
    print(f"   Action: {signal['action']}")
    print(f"   Entry Price: ${signal.get('entry', 'Market')}")
    print(f"   Stop Loss: ${signal.get('sl', 'Calculate based on risk')}")
    print(f"   Take Profit: ${signal.get('tp', 'Calculate based on R:R')}")
    print(f"   Time: {signal['timestamp']}")
    print()
    
    print("🎯 MANUAL EXECUTION STEPS:")
    print("1. 🌐 Open your MT4 trading platform")
    print("2. 🔐 Login to account 241926287")
    print("3. 📊 Navigate to XAUUSD chart")
    print("4. 📈 Place a Market Order:")
    print(f"   • Type: {signal['action']} (Market Execution)")
    print(f"   • Volume: Calculate based on 1% account risk")
    print(f"   • Stop Loss: {signal.get('sl', 'Set 30-50 pips from entry')}")
    print(f"   • Take Profit: {signal.get('tp', 'Set 2:1 risk/reward ratio')}")
    print()
    
    print("⚙️ RISK MANAGEMENT:")
    print("   💰 Risk only 1% of account balance per trade")
    print("   📊 Use proper position sizing")
    print("   🛑 Always set stop loss")
    print("   🎯 Target 2:1 risk/reward ratio")
    print()
    
    print("📱 ALTERNATIVE PLATFORMS:")
    print("   🌐 FBS Web Terminal: https://mt4.fbs.com/")
    print("   📱 FBS Mobile App")
    print("   💻 MT4 Desktop Terminal")
    print()

def save_trade_log(signal):
    """Save trade to log file"""
    try:
        trade_log = {
            'timestamp': signal['timestamp'],
            'symbol': signal.get('symbol', 'XAUUSD'),
            'action': signal['action'],
            'entry': signal.get('entry', ''),
            'sl': signal.get('sl', ''),
            'tp': signal.get('tp', ''),
            'status': 'signal_generated',
            'execution': 'manual'
        }
        
        # Save to JSON log
        try:
            with open('live_trading_log.json', 'r') as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        
        logs.append(trade_log)
        
        with open('live_trading_log.json', 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"✅ Trade signal logged to live_trading_log.json")
        
    except Exception as e:
        print(f"⚠️ Could not save to log: {e}")

def main():
    """Main live trading function"""
    print("🎯 LIVE TRADING SIGNAL EXECUTOR")
    print("===============================")
    print("This tool helps you execute trades manually based on our signals")
    print()
    
    while True:
        print("Choose an option:")
        print("1. 🔍 Get fresh trading signal")
        print("2. 📊 View account details")
        print("3. 📈 View trading log")
        print("4. ❌ Exit")
        print()
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            signal = get_latest_signal()
            if signal:
                display_trading_instructions(signal)
                save_trade_log(signal)
                
                execute = input("\n🤔 Execute this trade manually? (y/n): ").strip().lower()
                if execute == 'y':
                    print("\n✅ Proceed with manual execution as instructed above")
                    print("💡 Remember to apply proper risk management!")
                else:
                    print("\n⏸️ Trade signal noted but not executed")
            else:
                print("\n⏳ No strong signals at this time. Try again in a few minutes.")
        
        elif choice == "2":
            print("\n📊 FBS MT4 Account Details:")
            print("   Login: 241926287")
            print("   Server: FBS-Real-4")
            print("   Platform: MT4")
            print("   Risk per trade: 1% recommended")
            
        elif choice == "3":
            try:
                with open('live_trading_log.json', 'r') as f:
                    logs = json.load(f)
                print(f"\n📈 Recent Trading Signals ({len(logs)} total):")
                for log in logs[-5:]:  # Show last 5
                    print(f"   {log['timestamp']}: {log['action']} {log['symbol']} @ {log.get('entry', 'Market')}")
            except FileNotFoundError:
                print("\n📈 No trading log found yet")
        
        elif choice == "4":
            print("\n👋 Happy trading! Remember to manage your risk.")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()