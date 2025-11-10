#!/usr/bin/env python3
"""
Quick Trading Status Checker for $47.79 Account
"""

import yfinance as yf
import datetime
import json

def check_account_and_market():
    """Check account status and current market opportunities"""
    
    print("\n" + "="*60)
    print("💰 LIVE TRADING STATUS - $47.79 ACCOUNT")
    print("="*60)
    
    # Account info
    balance = 47.79
    risk_per_trade = balance * 0.015  # 1.5%
    max_trades = 2
    
    print(f"\n🏦 ACCOUNT DETAILS:")
    print(f"   Account: 241926287 (FBS-Real-4)")
    print(f"   Balance: ${balance:.2f}")
    print(f"   Risk per trade: ${risk_per_trade:.2f} (1.5%)")
    print(f"   Max concurrent trades: {max_trades}")
    
    # Market data
    symbols = {
        'EURUSD=X': 'EURUSD',
        'GBPUSD=X': 'GBPUSD', 
        'USDJPY=X': 'USDJPY',
        'GC=F': 'XAUUSD',
        'AUDUSD=X': 'AUDUSD'
    }
    
    print(f"\n📈 CURRENT MARKET PRICES:")
    opportunities = []
    
    for yahoo_symbol, clean_symbol in symbols.items():
        try:
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period="1d", interval="5m")
            
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                open_price = data['Open'].iloc[0]
                change_percent = ((current_price - open_price) / open_price) * 100
                
                # Simple volatility check
                high_5m = data['High'].iloc[-12:].max()  # Last hour
                low_5m = data['Low'].iloc[-12:].min()
                volatility = ((high_5m - low_5m) / current_price) * 100
                
                status = "🟢" if abs(change_percent) > 0.2 else "🟡"
                if volatility > 0.5:
                    status += " ACTIVE"
                    opportunities.append(clean_symbol)
                else:
                    status += " QUIET"
                
                print(f"   {clean_symbol}: ${current_price:.5f} ({change_percent:+.2f}%) {status}")
                
        except Exception as e:
            print(f"   {clean_symbol}: Error fetching data")
    
    # Trading opportunities
    print(f"\n🎯 CURRENT OPPORTUNITIES:")
    if opportunities:
        for symbol in opportunities:
            print(f"   ✅ {symbol} - Active movement detected")
        print(f"\n💡 RECOMMENDATION: Monitor {', '.join(opportunities)} for entry signals")
    else:
        print(f"   ⏸️ Markets in consolidation - Wait for breakouts")
        print(f"   💡 RECOMMENDATION: Continue monitoring, no rush to trade")
    
    # Risk management reminder
    print(f"\n⚖️ RISK MANAGEMENT:")
    print(f"   📊 Micro lots only (0.01 - 0.02)")
    print(f"   ⛔ Stop loss: 20-30 pips maximum")
    print(f"   🎯 Take profit: 2:1 ratio (40-60 pips)")
    print(f"   💰 Daily loss limit: $5.00")
    
    # Save status
    status_data = {
        'balance': balance,
        'risk_per_trade': risk_per_trade,
        'opportunities': opportunities,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    with open('quick_status.json', 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"\n💾 Status saved to: quick_status.json")
    print("="*60)

if __name__ == "__main__":
    check_account_and_market()