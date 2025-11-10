#!/usr/bin/env python3
"""
Live Trade Monitor for Capital.com
Monitor and manage your live trading positions
"""

import sys
from pathlib import Path
import time
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.brokers.capital_com import CapitalComBroker
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trade_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main trade monitoring loop"""
    
    print("\n" + "="*80)
    print("🚀 GenX_FX Live Trade Monitor - Capital.com")
    print("="*80 + "\n")
    
    # Initialize broker
    broker = CapitalComBroker()
    
    # Check if credentials are configured
    if not broker.api_key or not broker.identifier or not broker.password:
        print("❌ ERROR: Capital.com API credentials not configured!")
        print("\n📝 Please update your .env file with:")
        print("   - CAPITAL_COM_API_KEY")
        print("   - CAPITAL_COM_IDENTIFIER")
        print("   - CAPITAL_COM_PASSWORD")
        print("\n💡 Get your API key from: https://capital.com/trading/platform/")
        return
    
    # Authenticate
    print("🔐 Authenticating with Capital.com...")
    if not broker.authenticate():
        print("❌ Authentication failed. Please check your credentials.")
        return
    
    print(f"✅ Connected to Capital.com ({'DEMO' if broker.is_demo else 'LIVE'} account)")
    print(f"📊 Account ID: {broker.account_id}\n")
    
    # Get account info
    account = broker.get_account_info()
    if account:
        balance = account.get('balance', 'N/A')
        currency = account.get('currency', 'USD')
        print(f"💰 Account Balance: {balance} {currency}\n")
    
    # Main monitoring loop
    try:
        while True:
            print("\n" + "─"*80)
            print("📊 COMMAND MENU")
            print("─"*80)
            print("1. View Open Positions")
            print("2. View Account Info")
            print("3. Search Markets")
            print("4. Create New Position")
            print("5. Close Position")
            print("6. Update Position (SL/TP)")
            print("7. Refresh (auto-refresh every 30s)")
            print("0. Exit")
            print("─"*80)
            
            choice = input("\n👉 Select option: ").strip()
            
            if choice == "1":
                broker.display_positions_summary()
                
            elif choice == "2":
                account = broker.get_account_info()
                if account:
                    print(f"\n💰 Balance: {account.get('balance')} {account.get('currency')}")
                    print(f"📊 Available: {account.get('available', 'N/A')}")
                    print(f"📈 P&L: {account.get('profitLoss', 'N/A')}")
                    
            elif choice == "3":
                search = input("🔍 Search markets (e.g., 'EUR', 'BTC'): ").strip()
                markets = broker.get_markets(search)
                if markets:
                    print(f"\n🔍 Found {len(markets)} markets:")
                    for i, market in enumerate(markets[:10], 1):
                        print(f"{i}. {market.get('instrumentName')} ({market.get('epic')})")
                        
            elif choice == "4":
                print("\n📝 Create New Position")
                epic = input("Market epic (e.g., EURUSD): ").strip()
                direction = input("Direction (BUY/SELL): ").strip().upper()
                size = float(input("Size: "))
                
                use_sl = input("Add stop loss? (y/n): ").strip().lower() == 'y'
                stop_loss = float(input("Stop loss level: ")) if use_sl else None
                
                use_tp = input("Add take profit? (y/n): ").strip().lower() == 'y'
                take_profit = float(input("Take profit level: ")) if use_tp else None
                
                result = broker.create_position(epic, direction, size, stop_loss, take_profit)
                if result:
                    print(f"✅ Position created: {result.get('dealReference')}")
                    
            elif choice == "5":
                broker.display_positions_summary()
                deal_id = input("\n🔴 Enter Deal ID to close: ").strip()
                if broker.close_position(deal_id):
                    print("✅ Position closed successfully")
                    
            elif choice == "6":
                broker.display_positions_summary()
                deal_id = input("\n⚙️ Enter Deal ID to update: ").strip()
                
                use_sl = input("Update stop loss? (y/n): ").strip().lower() == 'y'
                stop_loss = float(input("New stop loss level: ")) if use_sl else None
                
                use_tp = input("Update take profit? (y/n): ").strip().lower() == 'y'
                take_profit = float(input("New take profit level: ")) if use_tp else None
                
                if broker.update_position(deal_id, stop_loss, take_profit):
                    print("✅ Position updated successfully")
                    
            elif choice == "7":
                print("\n🔄 Auto-refreshing positions every 30 seconds...")
                print("Press Ctrl+C to stop\n")
                try:
                    while True:
                        broker.display_positions_summary()
                        time.sleep(30)
                except KeyboardInterrupt:
                    print("\n⏸️ Auto-refresh stopped")
                    
            elif choice == "0":
                print("\n👋 Exiting trade monitor...")
                break
                
            else:
                print("\n❌ Invalid option")
                
    except KeyboardInterrupt:
        print("\n\n⏸️ Trade monitor stopped by user")
    except Exception as e:
        logger.error(f"Error in trade monitor: {str(e)}")
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
