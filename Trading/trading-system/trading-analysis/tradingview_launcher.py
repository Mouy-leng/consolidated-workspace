#!/usr/bin/env python3
"""
TradingView Auto-Login Helper
Opens TradingView with saved credentials
"""

import webbrowser
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TradingViewAutoLogin:
    def __init__(self):
        self.email = "Lengkundee01@gmail.com"
        self.password = "Leng1234@#$01"
        self.base_url = "https://www.tradingview.com"
        
    def open_tradingview_manual(self):
        """Open TradingView in browser for manual login"""
        print("🔥 Opening TradingView.com...")
        print(f"📧 Email: {self.email}")
        print("🔑 Password: [Saved in script]")
        print("\n💡 Manual Login Steps:")
        print("1. Click 'Sign In' button")
        print("2. Enter email: Lengkundee01@gmail.com")
        print("3. Enter password: Leng1234@#$01")
        print("4. Complete any 2FA if required")
        print("5. Navigate to your preferred chart")
        
        webbrowser.open(self.base_url)
        
    def create_chrome_profile(self):
        """Create Chrome profile for TradingView"""
        print("🌐 Creating Chrome profile for TradingView...")
        
        # Create profile directory
        profile_dir = os.path.expanduser("~/.tradingview_profile")
        os.makedirs(profile_dir, exist_ok=True)
        
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Opening TradingView login page...")
            driver.get("https://www.tradingview.com/accounts/signin/")
            
            print(f"📧 Please manually enter: {self.email}")
            print("🔑 Please manually enter your password")
            print("💡 After logging in, this profile will save your session")
            print("\n⏳ Press Enter after you've logged in successfully...")
            input()
            
            print("✅ Profile created! TradingView will remember you next time.")
            driver.quit()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Please install ChromeDriver or login manually")
    
    def open_specific_chart(self, symbol="XAUUSD", interval="15"):
        """Open specific chart in TradingView"""
        chart_url = f"https://www.tradingview.com/chart/?symbol=OANDA%3A{symbol}&interval={interval}"
        print(f"📈 Opening {symbol} chart ({interval}min)...")
        webbrowser.open(chart_url)
    
    def get_chart_urls(self):
        """Get pre-configured chart URLs"""
        charts = {
            "XAUUSD": "https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD&interval=15",
            "EURUSD": "https://www.tradingview.com/chart/?symbol=FX%3AEURUSD&interval=15", 
            "GBPUSD": "https://www.tradingview.com/chart/?symbol=FX%3AGBPUSD&interval=15",
            "USDJPY": "https://www.tradingview.com/chart/?symbol=FX%3AUSDJPY&interval=15",
            "BTCUSD": "https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT&interval=15"
        }
        return charts

def main():
    """Main function with menu"""
    tv = TradingViewAutoLogin()
    
    print("🔥 TradingView Auto-Login Helper")
    print("================================")
    print(f"📧 Account: {tv.email}")
    print("\nSelect an option:")
    print("1. 🌐 Open TradingView (Manual Login)")
    print("2. 📈 Open XAUUSD Chart")
    print("3. 💰 Open EURUSD Chart")
    print("4. 🏦 Open GBPUSD Chart")
    print("5. 🗾 Open USDJPY Chart")
    print("6. ₿ Open BTCUSD Chart")
    print("7. 🔧 Create Chrome Profile (Save Login)")
    print("8. 📋 Show All Chart URLs")
    
    choice = input("\nEnter your choice (1-8): ").strip()
    
    if choice == "1":
        tv.open_tradingview_manual()
    elif choice == "2":
        tv.open_specific_chart("XAUUSD")
    elif choice == "3":
        tv.open_specific_chart("EURUSD")
    elif choice == "4":
        tv.open_specific_chart("GBPUSD")
    elif choice == "5":
        tv.open_specific_chart("USDJPY")
    elif choice == "6":
        tv.open_specific_chart("BTCUSD")
    elif choice == "7":
        tv.create_chrome_profile()
    elif choice == "8":
        charts = tv.get_chart_urls()
        print("\n📋 Pre-configured Chart URLs:")
        for symbol, url in charts.items():
            print(f"{symbol}: {url}")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()