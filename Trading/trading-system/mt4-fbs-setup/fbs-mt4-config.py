#!/usr/bin/env python3
"""
FBS MT4 Configuration Setup
"""

import json
from datetime import datetime

def setup_mt4_account():
    """Setup MT4 account configuration"""
    
    credentials = {
        "login": "241926287",
        "password": "f0v/9iIH",
        "server": "FBS-Real-4",
        "server_ip": "95.179.194.198:443",
        "company": "FBS Markets Inc.",
        "platform": "MT4",
        "account_type": "real",
        "setup_date": datetime.now().isoformat()
    }
    
    # Save MT4 config
    with open("fbs_mt4_config.json", 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print("FBS MT4 Account Configuration")
    print("=" * 30)
    print(f"Login: {credentials['login']}")
    print(f"Server: {credentials['server']}")
    print(f"Server IP: {credentials['server_ip']}")
    print(f"Company: {credentials['company']}")
    
    return credentials

def create_mt4_ini():
    """Create MT4 configuration file"""
    
    config = """
; FBS MT4 Real Account Configuration
[Server]
Server=FBS-Real-4
Login=241926287
Password=f0v/9iIH

[Common]
Language=English
NewsEnable=true
SoundEnable=true
NotificationEnable=true

[Charts]
Template=default.tpl
Period=240
ShowAskLine=true
ShowBidLine=true

[Expert]
AllowLiveTrading=true
AllowDllImport=true
AllowImport=true

[Connection]
ServerIP=95.179.194.198:443
Timeout=30000
Company=FBS Markets Inc.
"""
    
    with open("mt4_fbs_config.ini", 'w') as f:
        f.write(config)
    
    print("MT4 configuration file created")

def main():
    print("Setting up FBS MT4 Account...")
    
    # Setup account
    setup_mt4_account()
    
    # Create MT4 config
    create_mt4_ini()
    
    print("\nMT4 configuration completed!")
    print("Ready to download and install MT4")

if __name__ == "__main__":
    main()