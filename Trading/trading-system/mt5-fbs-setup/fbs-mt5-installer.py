#!/usr/bin/env python3
"""
FBS MT5 Automated Setup and Configuration
Downloads, installs, and configures MT5 with FBS broker
"""

import os
import requests
import subprocess
import json
from pathlib import Path
import time

class FBSMT5Installer:
    def __init__(self):
        self.fbs_mt5_url = "https://www.fbs.com/download/metatrader5"
        self.installer_path = "mt5setup.exe"
        self.mt5_path = None
        
    def download_mt5(self):
        """Download MT5 installer from FBS"""
        print("📥 Downloading MT5 from FBS...")
        
        try:
            response = requests.get(self.fbs_mt5_url, stream=True)
            response.raise_for_status()
            
            with open(self.installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("✅ MT5 installer downloaded")
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def install_mt5(self):
        """Install MT5 silently"""
        print("🔧 Installing MT5...")
        
        try:
            # Silent installation
            subprocess.run([
                self.installer_path,
                "/S",  # Silent mode
                "/D=C:\\Program Files\\MetaTrader 5"
            ], check=True)
            
            print("✅ MT5 installed successfully")
            self.mt5_path = "C:\\Program Files\\MetaTrader 5"
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def configure_fbs_server(self, login, password, server="FBS-Real"):
        """Configure FBS server connection"""
        print("⚙️ Configuring FBS server...")
        
        config = {
            "Login": login,
            "Password": password,
            "Server": server,
            "AutoConfiguration": True
        }
        
        # Create config file for MT5
        config_path = os.path.join(self.mt5_path, "config", "fbs_config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ FBS configuration saved")
        return config_path
    
    def setup_trading_environment(self):
        """Setup trading environment and folders"""
        print("📁 Setting up trading environment...")
        
        folders = [
            "MQL5/Experts",
            "MQL5/Indicators", 
            "MQL5/Scripts",
            "MQL5/Include",
            "Files",
            "Logs"
        ]
        
        for folder in folders:
            folder_path = os.path.join(self.mt5_path, folder)
            os.makedirs(folder_path, exist_ok=True)
        
        print("✅ Trading environment setup complete")
    
    def create_startup_script(self):
        """Create MT5 startup script with FBS configuration"""
        script_content = f'''@echo off
echo 🚀 Starting MT5 with FBS Configuration
cd /d "{self.mt5_path}"
start "" "terminal64.exe" /config:config\\fbs_config.json
echo ✅ MT5 Started with FBS
pause
'''
        
        script_path = "start_mt5_fbs.bat"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"✅ Startup script created: {script_path}")
        return script_path

def main():
    installer = FBSMT5Installer()
    
    print("🏦 FBS MT5 Setup Assistant")
    print("=" * 30)
    
    # Get FBS credentials
    login = input("FBS Login: ")
    password = input("FBS Password: ")
    server = input("FBS Server (default: FBS-Real): ") or "FBS-Real"
    
    # Download MT5
    if not installer.download_mt5():
        return
    
    # Install MT5
    if not installer.install_mt5():
        return
    
    # Configure FBS
    installer.configure_fbs_server(login, password, server)
    
    # Setup environment
    installer.setup_trading_environment()
    
    # Create startup script
    installer.create_startup_script()
    
    print("\n✅ FBS MT5 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Run start_mt5_fbs.bat to launch MT5")
    print("2. Verify FBS server connection")
    print("3. Install Expert Advisors if needed")

if __name__ == "__main__":
    main()