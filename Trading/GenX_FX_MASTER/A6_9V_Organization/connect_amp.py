#!/usr/bin/env python3
"""
Simple AMP Connection Script
Quick way to connect and interact with the AMP trading system
"""

import sys
from simple_amp_chat import SimpleAMPChat
from amp_auth import check_auth, get_user_info

def main():
    print("🤖 AMP Connection Test")
    print("======================")
    
    # Check authentication
    if not check_auth():
        print("❌ Not authenticated with AMP")
        print("   You need a valid authentication token")
        print("   Run: python3 amp_cli.py auth --token YOUR_TOKEN")
        return
    
    user_info = get_user_info()
    print(f"✅ Connected to AMP as: {user_info['user_id']}")
    print()
    
    # Initialize chat
    chat = SimpleAMPChat()
    
    # Show available commands
    print("💬 Available commands:")
    print("   - 'status' : Show AMP system status")
    print("   - 'signals' : Get trading signals")
    print("   - 'btc' : Bitcoin analysis")
    print("   - 'prediction' : Market predictions")
    print("   - 'help' : Show help")
    print("   - 'quit' : Exit")
    print()
    
    # Interactive loop
    while True:
        try:
            message = input("AMP> ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("👋 Disconnecting from AMP...")
                break
            
            if not message:
                continue
            
            # Send message to AMP
            result = chat.send_message(message)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"🤖 AMP: {result['amp_response']}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Disconnecting from AMP...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()