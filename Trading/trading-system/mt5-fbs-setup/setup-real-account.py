#!/usr/bin/env python3
"""
Setup Real FBS Account with provided credentials
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security'))

import json
from datetime import datetime

def setup_real_fbs_account():
    """Setup real FBS account configuration"""
    
    # Real account credentials
    credentials = {
        "login": "40933210",
        "password": "8IA.KFIB",
        "server": "FBS-Real",
        "server_ip": "185.237.98.177:443",
        "company": "FBS",
        "account_type": "real",
        "setup_date": datetime.now().isoformat()
    }
    
    # Save credentials securely
    try:
        from credential_manager import CredentialManager
        cred_manager = CredentialManager()
        cred_manager.store_credentials("mt5-fbs-real", credentials)
        print("Real FBS credentials stored securely")
    except:
        # Fallback to JSON file
        with open("fbs_real_config.json", 'w') as f:
            json.dump(credentials, f, indent=2)
        print("Real FBS credentials saved to config file")
    
    return credentials

def create_real_mt5_config():
    """Create MT5 configuration for real account"""
    
    config = """
; FBS Real Account MT5 Configuration
[Server]
Server=FBS-Real
Login=40933210
Password=8IA.KFIB

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

[Connection]
ServerIP=185.237.98.177:443
Timeout=30000
"""
    
    with open("mt5_fbs_real_config.ini", 'w') as f:
        f.write(config)
    
    print("Real account MT5 configuration created")

def main():
    print("FBS Real Account Setup")
    print("=" * 25)
    
    # Setup real account
    credentials = setup_real_fbs_account()
    
    # Create MT5 config
    create_real_mt5_config()
    
    print("\nReal FBS account configured!")
    print(f"Login: {credentials['login']}")
    print(f"Server: {credentials['server']}")
    print(f"Server IP: {credentials['server_ip']}")
    
    print("\nNext steps:")
    print("1. Launch MT5 with real account config")
    print("2. Test connection")
    print("3. Start trading")

if __name__ == "__main__":
    main()