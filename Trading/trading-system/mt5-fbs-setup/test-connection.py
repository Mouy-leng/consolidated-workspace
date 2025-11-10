#!/usr/bin/env python3
"""
Test MT5 connection and basic functionality
"""

try:
    import MetaTrader5 as mt5
    print("MT5 Python package available")
except ImportError:
    print("Installing MetaTrader5 package...")
    import subprocess
    subprocess.check_call(["pip", "install", "MetaTrader5"])
    import MetaTrader5 as mt5

def test_mt5_connection():
    """Test MT5 connection"""
    print("Testing MT5 connection...")
    
    # Initialize MT5
    if not mt5.initialize():
        print("MT5 initialization failed")
        print("Error:", mt5.last_error())
        return False
    
    print("MT5 initialized successfully")
    
    # Get terminal info
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"Terminal: {terminal_info.name}")
        print(f"Version: {terminal_info.build}")
        print(f"Path: {terminal_info.path}")
    
    # Test symbol info
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info:
        print(f"Symbol {symbol} available")
        print(f"Bid: {symbol_info.bid}")
        print(f"Ask: {symbol_info.ask}")
    else:
        print(f"Symbol {symbol} not available")
    
    # Shutdown
    mt5.shutdown()
    print("MT5 connection test completed")
    return True

def main():
    print("MT5 FBS Connection Test")
    print("=" * 25)
    
    if test_mt5_connection():
        print("\nConnection test PASSED!")
        print("MT5 is ready for trading")
    else:
        print("\nConnection test FAILED!")
        print("Please check MT5 installation")

if __name__ == "__main__":
    main()