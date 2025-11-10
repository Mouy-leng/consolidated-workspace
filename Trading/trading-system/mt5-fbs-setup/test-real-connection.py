#!/usr/bin/env python3
"""
Test real FBS account connection
"""

import MetaTrader5 as mt5
import json

def test_real_connection():
    """Test connection to real FBS account"""
    
    # Load real account credentials
    with open("fbs_real_config.json", 'r') as f:
        config = json.load(f)
    
    print("Testing Real FBS Account Connection")
    print("=" * 35)
    print(f"Login: {config['login']}")
    print(f"Server: {config['server']}")
    print(f"Server IP: {config['server_ip']}")
    
    # Initialize MT5
    if not mt5.initialize():
        print("MT5 initialization failed")
        return False
    
    # Login to real account
    if not mt5.login(
        login=int(config['login']),
        password=config['password'],
        server=config['server']
    ):
        error = mt5.last_error()
        print(f"Login failed: {error}")
        mt5.shutdown()
        return False
    
    print("Login successful!")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        print(f"\nAccount Information:")
        print(f"Balance: ${account_info.balance:.2f}")
        print(f"Equity: ${account_info.equity:.2f}")
        print(f"Margin: ${account_info.margin:.2f}")
        print(f"Free Margin: ${account_info.margin_free:.2f}")
        print(f"Leverage: 1:{account_info.leverage}")
        print(f"Currency: {account_info.currency}")
        print(f"Profit: ${account_info.profit:.2f}")
    
    # Test symbol access
    symbols = ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY"]
    print(f"\nTesting Symbol Access:")
    
    for symbol in symbols:
        info = mt5.symbol_info(symbol)
        if info:
            print(f"{symbol}: Bid={info.bid:.5f}, Ask={info.ask:.5f}")
        else:
            print(f"{symbol}: Not available")
    
    # Get positions
    positions = mt5.positions_get()
    print(f"\nOpen Positions: {len(positions) if positions else 0}")
    
    if positions:
        for pos in positions:
            print(f"  {pos.symbol} {pos.type} {pos.volume} lots, Profit: ${pos.profit:.2f}")
    
    mt5.shutdown()
    return True

def main():
    if test_real_connection():
        print("\nConnection test PASSED!")
        print("Real FBS account is ready for trading")
    else:
        print("\nConnection test FAILED!")
        print("Please check account credentials and MT5 installation")

if __name__ == "__main__":
    main()