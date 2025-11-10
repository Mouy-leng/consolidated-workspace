#!/usr/bin/env python3
"""
Quick MT5 FBS Setup - Simplified version
"""

import os
import json
from datetime import datetime

def setup_demo_account():
    """Setup demo account configuration"""
    print("FBS Demo Account Setup")
    print("=" * 25)
    
    config = {
        "account_type": "demo",
        "server": "FBS-Demo",
        "leverage": "1:1000",
        "deposit": 10000,
        "currency": "USD",
        "created_at": datetime.now().isoformat()
    }
    
    with open("fbs_demo_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Demo account configuration saved")
    return config

def create_mt5_config():
    """Create MT5 configuration"""
    mt5_config = """
; FBS MT5 Configuration
[Server]
Server=FBS-Demo
Login=<YOUR_LOGIN>
Password=<YOUR_PASSWORD>

[Common]
Language=English
NewsEnable=true
SoundEnable=true
NotificationEnable=true

[Charts]
Template=default.tpl
Period=H1
ShowAskLine=true
ShowBidLine=true

[Expert]
AllowLiveTrading=true
AllowDllImport=true
AllowImport=true
"""
    
    with open("mt5_fbs_config.ini", 'w') as f:
        f.write(mt5_config)
    
    print("MT5 configuration created")

def setup_trading_symbols():
    """Setup trading symbols"""
    symbols = {
        "forex_majors": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF"],
        "metals": ["XAUUSD", "XAGUSD"],
        "indices": ["US30", "US500", "NAS100"]
    }
    
    with open("fbs_trading_symbols.json", 'w') as f:
        json.dump(symbols, f, indent=2)
    
    print("Trading symbols configured")

def main():
    print("MT5 FBS Quick Setup")
    print("=" * 20)
    
    # Setup demo account
    setup_demo_account()
    
    # Create MT5 config
    create_mt5_config()
    
    # Setup symbols
    setup_trading_symbols()
    
    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Go to https://www.fbs.com/registration")
    print("2. Register for demo account")
    print("3. Download MT5 from FBS")
    print("4. Use generated config files")

if __name__ == "__main__":
    main()