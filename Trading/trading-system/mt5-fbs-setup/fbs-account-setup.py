#!/usr/bin/env python3
"""
FBS Account Setup and Verification
Handles FBS account creation and verification process
"""

import requests
import json
from datetime import datetime

class FBSAccountSetup:
    def __init__(self):
        self.fbs_api_base = "https://api.fbs.com"
        self.account_types = {
            "demo": "Demo Account",
            "cent": "Cent Account", 
            "micro": "Micro Account",
            "standard": "Standard Account",
            "zero": "Zero Spread Account",
            "ecn": "ECN Account"
        }
        
    def get_fbs_servers(self):
        """Get available FBS servers"""
        servers = {
            "demo": [
                "FBS-Demo",
                "FBS-Demo2", 
                "FBS-Demo3"
            ],
            "real": [
                "FBS-Real",
                "FBS-Real2",
                "FBS-Real3",
                "FBS-ECN",
                "FBS-Zero"
            ]
        }
        return servers
    
    def display_account_info(self):
        """Display FBS account information and requirements"""
        info = """
🏦 FBS BROKER INFORMATION
========================

📊 Account Types:
• Demo Account - Free practice trading
• Cent Account - Trade in cents (1:3000 leverage)
• Micro Account - Small deposits ($1 min)
• Standard Account - Standard trading ($100 min)
• Zero Spread Account - Zero spread on major pairs
• ECN Account - Direct market access ($1000 min)

💰 Leverage Options:
• Up to 1:3000 for Cent accounts
• Up to 1:1000 for Standard accounts
• Up to 1:500 for ECN accounts

🌍 Servers:
• FBS-Real - Main trading server
• FBS-Demo - Demo trading server
• FBS-ECN - ECN trading server
• FBS-Zero - Zero spread server

📱 Platforms:
• MetaTrader 5 (Recommended)
• MetaTrader 4
• FBS Trader (Mobile)
• WebTrader

🎁 Bonuses:
• $140 No Deposit Bonus
• 100% Deposit Bonus
• Cashback up to $15 per lot
        """
        print(info)
    
    def create_demo_account_config(self):
        """Create demo account configuration"""
        print("🎯 Creating Demo Account Configuration...")
        
        config = {
            "account_type": "demo",
            "server": "FBS-Demo",
            "leverage": "1:1000",
            "deposit": 10000,  # Demo balance
            "currency": "USD",
            "created_at": datetime.now().isoformat()
        }
        
        # Save demo config
        with open("fbs_demo_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Demo account configuration saved")
        return config
    
    def generate_mt5_config(self, account_config):
        """Generate MT5 configuration file"""
        mt5_config = f"""
; FBS MT5 Configuration
[Server]
Server={account_config['server']}
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
        
        print("✅ MT5 configuration file created")
        return "mt5_fbs_config.ini"
    
    def setup_trading_symbols(self):
        """Setup common trading symbols for FBS"""
        symbols = {
            "forex_majors": [
                "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
                "AUDUSD", "USDCAD", "NZDUSD"
            ],
            "forex_minors": [
                "EURJPY", "GBPJPY", "EURGBP", "AUDCAD",
                "AUDCHF", "AUDJPY", "CADJPY"
            ],
            "metals": [
                "XAUUSD", "XAGUSD", "XPDUSD", "XPTUSD"
            ],
            "indices": [
                "US30", "US500", "NAS100", "UK100",
                "GER30", "FRA40", "JPN225"
            ],
            "crypto": [
                "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD"
            ]
        }
        
        with open("fbs_trading_symbols.json", 'w') as f:
            json.dump(symbols, f, indent=2)
        
        print("✅ Trading symbols configuration saved")
        return symbols

def main():
    setup = FBSAccountSetup()
    
    print("🏦 FBS Account Setup Assistant")
    print("=" * 35)
    
    # Display FBS information
    setup.display_account_info()
    
    # Account type selection
    print("\n📋 Account Setup Options:")
    print("1. Demo Account (Recommended for beginners)")
    print("2. Real Account Setup Guide")
    print("3. Generate MT5 Configuration")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        config = setup.create_demo_account_config()
        setup.generate_mt5_config(config)
        setup.setup_trading_symbols()
        
        print("\n✅ Demo Account Setup Complete!")
        print("\n📋 Next Steps:")
        print("1. Go to https://www.fbs.com/registration")
        print("2. Register for a demo account")
        print("3. Download MT5 from FBS website")
        print("4. Use the generated configuration files")
        
    elif choice == "2":
        print("\n🔗 Real Account Setup:")
        print("1. Visit: https://www.fbs.com/registration")
        print("2. Complete KYC verification")
        print("3. Choose account type")
        print("4. Make initial deposit")
        print("5. Download MT5 and login")
        
    elif choice == "3":
        demo_config = setup.create_demo_account_config()
        setup.generate_mt5_config(demo_config)
        setup.setup_trading_symbols()
        print("✅ Configuration files generated")
    
    print(f"\n📁 Files created in: {os.getcwd()}")

if __name__ == "__main__":
    main()