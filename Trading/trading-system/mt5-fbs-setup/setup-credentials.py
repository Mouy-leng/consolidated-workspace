#!/usr/bin/env python3
"""
Setup FBS credentials securely
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security'))

from credential_manager import CredentialManager
import getpass

def setup_fbs_credentials():
    """Setup FBS credentials securely"""
    print("FBS Credentials Setup")
    print("=" * 20)
    
    # Get credentials from user
    login = input("FBS Login: ")
    password = getpass.getpass("FBS Password: ")
    server = input("FBS Server (default: FBS-Demo): ") or "FBS-Demo"
    
    # Initialize credential manager
    cred_manager = CredentialManager()
    
    try:
        # Store credentials securely
        credentials = {
            "login": login,
            "password": password,
            "server": server,
            "company": "FBS",
            "setup_date": "2024-01-01"
        }
        
        cred_manager.store_credentials("mt5-fbs", credentials)
        print("Credentials stored securely!")
        
        return True
        
    except Exception as e:
        print(f"Error storing credentials: {e}")
        return False

def main():
    if setup_fbs_credentials():
        print("\nFBS credentials setup completed!")
        print("Credentials are encrypted and stored securely.")
    else:
        print("\nCredentials setup failed!")

if __name__ == "__main__":
    main()