#!/usr/bin/env python3
"""
Test MT5 Connection with Updated Credentials
"""

import MetaTrader5 as mt5
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_mt5_connection():
    """Test MT5 connection with updated FBS credentials"""
    
    # Your updated FBS account details
    account = 40933210
    password = "8IA.KFIB"
    server = "FBS-Real"
    
    print(f"🔌 Testing MT5 connection...")
    print(f"   Account: {account}")
    print(f"   Server: {server}")
    print(f"   Server IP: 185.237.98.177:443")
    
    try:
        # Initialize MT5
        if not mt5.initialize():
            print("❌ MT5 initialize() failed")
            print(f"   Error: {mt5.last_error()}")
            return False
        
        print("✅ MT5 initialized successfully")
        
        # Attempt login
        print(f"🔐 Attempting login to account {account}...")
        if not mt5.login(account, password=password, server=server):
            error = mt5.last_error()
            print(f"❌ Failed to connect to account {account}")
            print(f"   Error code: {error[0]}")
            print(f"   Error description: {error[1]}")
            return False
        
        print("✅ Successfully logged in to MT5!")
        
        # Get account info
        account_info = mt5.account_info()
        if account_info is not None:
            print("\n📊 Account Information:")
            print(f"   Login: {account_info.login}")
            print(f"   Balance: ${account_info.balance:.2f}")
            print(f"   Equity: ${account_info.equity:.2f}")
            print(f"   Margin: ${account_info.margin:.2f}")
            print(f"   Free Margin: ${account_info.margin_free:.2f}")
            print(f"   Server: {account_info.server}")
            print(f"   Currency: {account_info.currency}")
            print(f"   Company: {account_info.company}")
        
        # Test symbol access
        print("\n📈 Testing symbol access...")
        symbols = ["XAUUSD", "EURUSD", "GBPUSD"]
        for symbol in symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is not None:
                print(f"   ✅ {symbol}: Available (Spread: {symbol_info.spread})")
            else:
                print(f"   ❌ {symbol}: Not available")
        
        print("\n🎉 MT5 connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    test_mt5_connection()