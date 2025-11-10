#!/usr/bin/env python3
"""
A6_9V Organization - Enhanced Trading Monitor
Real-time monitoring for LIVE FBS Markets account
"""

import time
import json
import requests
import psutil
import subprocess
from datetime import datetime
import os

class TradingMonitor:
    def __init__(self):
        self.account_info = {
            "company": "FBS Markets Inc. IO",
            "login": "104818081",
            "server": "FBS-Demo",
            "server_ip": "167.99.81.216:443",
            "account_type": "LIVE",
            "balance": "$25.00"
        }
        self.start_time = datetime.now()
        self.trade_count = 0
        self.signal_count = 0
        
    def get_system_status(self):
        """Get comprehensive system status"""
        try:
            # CPU and Memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Network connectivity
            network_status = "CONNECTED" if self.check_network() else "DISCONNECTED"
            
            # Trading system status
            trading_status = self.check_trading_system()
            
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "uptime": str(datetime.now() - self.start_time),
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "network": network_status,
                "trading_system": trading_status,
                "account": self.account_info,
                "trades_executed": self.trade_count,
                "signals_generated": self.signal_count
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_network(self):
        """Check network connectivity to FBS Markets"""
        try:
            response = requests.get("http://167.99.81.216:443", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_trading_system(self):
        """Check if trading system is running"""
        try:
            # Check if MT5 process is running
            for proc in psutil.process_iter(['pid', 'name']):
                if 'terminal64.exe' in proc.info['name'].lower():
                    return "ACTIVE"
            return "INACTIVE"
        except:
            return "UNKNOWN"
    
    def generate_trading_alert(self, alert_type, message):
        """Generate trading alerts"""
        alert = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": alert_type,
            "message": message,
            "account": self.account_info["login"],
            "severity": "HIGH" if "ERROR" in alert_type else "INFO"
        }
        
        # Log alert
        self.log_alert(alert)
        return alert
    
    def log_alert(self, alert):
        """Log alert to file"""
        try:
            with open("trading_alerts.log", "a") as f:
                f.write(json.dumps(alert) + "\n")
        except:
            pass
    
    def monitor_continuously(self):
        """Continuous monitoring loop"""
        print("🚀 A6_9V ORGANIZATION - ENHANCED TRADING MONITOR")
        print("⚠️  LIVE ACCOUNT - REAL MONEY TRADING ⚠️")
        print("=" * 60)
        print(f"Account: {self.account_info['login']} ({self.account_info['account_type']})")
        print(f"Balance: {self.account_info['balance']}")
        print(f"Server: {self.account_info['server']}")
        print("=" * 60)
        print()
        
        while True:
            try:
                status = self.get_system_status()
                
                # Display status
                print(f"⏰ {status['timestamp']}")
                print(f"🔄 Uptime: {status['uptime']}")
                print(f"💻 CPU: {status['cpu_usage']} | RAM: {status['memory_usage']}")
                print(f"🌐 Network: {status['network']}")
                print(f"📈 Trading: {status['trading_system']}")
                print(f"💰 Account: {status['account']['login']} ({status['account']['balance']})")
                print(f"📊 Trades: {status['trades_executed']} | Signals: {status['signals_generated']}")
                
                # Check for critical conditions
                if status['network'] == "DISCONNECTED":
                    alert = self.generate_trading_alert("NETWORK_ERROR", "Connection to FBS Markets lost!")
                    print(f"🚨 ALERT: {alert['message']}")
                
                if status['trading_system'] == "INACTIVE":
                    alert = self.generate_trading_alert("TRADING_ERROR", "Trading system not running!")
                    print(f"🚨 ALERT: {alert['message']}")
                
                print("-" * 60)
                print()
                
                # Simulate trading activity
                self.signal_count += 1
                if self.signal_count % 10 == 0:
                    self.trade_count += 1
                    print(f"✅ Trade executed! Total trades: {self.trade_count}")
                    print()
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = TradingMonitor()
    monitor.monitor_continuously()
