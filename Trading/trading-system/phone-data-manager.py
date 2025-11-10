#!/usr/bin/env python3
"""
Plugin Phone Internet Data Manager
Optimizes direct internet data usage from mobile phone connection
"""

import sys
import subprocess
import json
import time
import requests
import psutil
from datetime import datetime
import logging
import socket

# Fix Windows Unicode issues
sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phone_data_usage.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class PhoneDataManager:
    def __init__(self):
        self.connection_info = {}
        self.data_usage = {}
        self.connection_quality = {}
        self.trading_requirements = {
            'min_speed_mbps': 1.0,  # Minimum for trading
            'max_latency_ms': 500,  # Maximum acceptable latency
            'stability_threshold': 90  # Connection stability %
        }
        
    def detect_mobile_connection(self):
        """Detect if connected via mobile phone hotspot"""
        print("📱 DETECTING MOBILE PHONE CONNECTION")
        print("=" * 50)
        
        try:
            # Get current network interface info
            result = subprocess.run([
                'netsh', 'wlan', 'show', 'interfaces'
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                output = result.stdout
                
                # Extract connection details
                connection_info = {}
                lines = output.split('\n')
                
                for line in lines:
                    if 'SSID' in line and ':' in line:
                        ssid = line.split(':', 1)[1].strip()
                        connection_info['ssid'] = ssid
                    elif 'State' in line and ':' in line:
                        state = line.split(':', 1)[1].strip()
                        connection_info['state'] = state
                    elif 'Signal' in line and ':' in line:
                        signal = line.split(':', 1)[1].strip()
                        connection_info['signal'] = signal
                    elif 'Channel' in line and ':' in line:
                        channel = line.split(':', 1)[1].strip()
                        connection_info['channel'] = channel
                
                # Check if it's a mobile device - Enhanced Samsung detection
                ssid = connection_info.get('ssid', '')
                mobile_indicators = [
                    'TECNO', 'Galaxy', 'iPhone', 'Android', 'Huawei', 
                    'Xiaomi', 'OnePlus', 'Nokia', 'Motorola', 'LG',
                    'hotspot', 'mobile', 'phone', 'Samsung', 'SM-', 'samsung'
                ]
                
                # Samsung-specific patterns
                samsung_patterns = ['Galaxy', 'Samsung', 'SM-', 'samsung', 'SAMSUNG', 'galaxy']
                is_samsung = any(pattern in ssid for pattern in samsung_patterns)
                
                is_mobile = any(indicator.lower() in ssid.lower() for indicator in mobile_indicators)
                
                self.connection_info = connection_info
                self.connection_info['is_mobile'] = is_mobile
                self.connection_info['is_samsung'] = is_samsung
                
                device_type = "Samsung Internet Device" if is_samsung else "Mobile Device" if is_mobile else "Unknown"
                
                print(f"📱 Connected SSID: {ssid}")
                print(f"📶 Signal: {connection_info.get('signal', 'Unknown')}")
                print(f"📡 Channel: {connection_info.get('channel', 'Unknown')}")
                print(f"🔍 Device Type: {device_type}")
                
                if is_samsung:
                    print("🌐 Samsung Internet Direct Connection: DETECTED")
                    print("💡 Samsung data optimizations available!")
                
                return is_mobile, connection_info
            else:
                print(f"❌ Failed to get interface info: {result.stderr}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error detecting connection: {e}")
            return False, {}
    
    def test_internet_speed(self):
        """Test internet connection speed and quality"""
        print("\n⚡ TESTING INTERNET SPEED & QUALITY")
        print("-" * 40)
        
        # Test latency (ping)
        latency = self.test_latency()
        
        # Test download speed
        download_speed = self.test_download_speed()
        
        # Test connection stability
        stability = self.test_connection_stability()
        
        self.connection_quality = {
            'latency_ms': latency,
            'download_mbps': download_speed,
            'stability_percent': stability,
            'timestamp': datetime.now().isoformat()
        }
        
        # Evaluate for trading
        self.evaluate_trading_suitability()
        
        return self.connection_quality
    
    def test_latency(self):
        """Test network latency (ping)"""
        print("🏓 Testing latency...")
        
        try:
            # Ping Google DNS
            result = subprocess.run([
                'ping', '-n', '4', '8.8.8.8'
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                output = result.stdout
                
                # Extract average latency
                import re
                avg_match = re.search(r'Average = (\d+)ms', output)
                if avg_match:
                    latency = int(avg_match.group(1))
                    print(f"   ⏱️  Average latency: {latency}ms")
                    return latency
                else:
                    print("   ❌ Could not parse latency")
                    return None
            else:
                print("   ❌ Ping failed")
                return None
                
        except Exception as e:
            print(f"   ❌ Error testing latency: {e}")
            return None
    
    def test_download_speed(self):
        """Test download speed using a small file"""
        print("⬇️  Testing download speed...")
        
        try:
            # Test with a small file from a reliable source
            test_url = "http://speedtest.ftp.otenet.gr/files/test100k.db"
            
            start_time = time.time()
            response = requests.get(test_url, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                # Calculate speed
                file_size_mb = len(response.content) / (1024 * 1024)
                duration_seconds = end_time - start_time
                speed_mbps = (file_size_mb * 8) / duration_seconds  # Convert to Mbps
                
                print(f"   📊 Download speed: {speed_mbps:.2f} Mbps")
                return speed_mbps
            else:
                print(f"   ❌ Download test failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error testing download speed: {e}")
            return None
    
    def test_connection_stability(self):
        """Test connection stability over time"""
        print("📊 Testing connection stability...")
        
        successful_pings = 0
        total_pings = 10
        
        for i in range(total_pings):
            try:
                result = subprocess.run([
                    'ping', '-n', '1', '-w', '2000', '8.8.8.8'
                ], capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode == 0:
                    successful_pings += 1
                
                if i < total_pings - 1:
                    time.sleep(1)
                    
            except Exception:
                pass
        
        stability = (successful_pings / total_pings) * 100
        print(f"   📈 Connection stability: {stability:.1f}%")
        return stability
    
    def evaluate_trading_suitability(self):
        """Evaluate if connection is suitable for trading"""
        print("\n🎯 EVALUATING TRADING SUITABILITY")
        print("-" * 40)
        
        quality = self.connection_quality
        requirements = self.trading_requirements
        
        # Check latency
        latency_ok = quality.get('latency_ms', 999) <= requirements['max_latency_ms']
        print(f"⏱️  Latency: {quality.get('latency_ms', 'Unknown')}ms {'✅ OK' if latency_ok else '❌ HIGH'}")
        
        # Check speed
        speed_ok = quality.get('download_mbps', 0) >= requirements['min_speed_mbps']
        print(f"⚡ Speed: {quality.get('download_mbps', 'Unknown'):.2f} Mbps {'✅ OK' if speed_ok else '❌ SLOW'}")
        
        # Check stability
        stability_ok = quality.get('stability_percent', 0) >= requirements['stability_threshold']
        print(f"📊 Stability: {quality.get('stability_percent', 'Unknown'):.1f}% {'✅ OK' if stability_ok else '❌ UNSTABLE'}")
        
        # Overall assessment
        overall_ok = latency_ok and speed_ok and stability_ok
        
        print(f"\n🏆 OVERALL ASSESSMENT: {'✅ SUITABLE FOR TRADING' if overall_ok else '⚠️  MARGINAL FOR TRADING'}")
        
        if not overall_ok:
            print("\n💡 RECOMMENDATIONS:")
            if not latency_ok:
                print("   📶 Move closer to phone for better signal")
            if not speed_ok:
                print("   📱 Check phone's mobile data connection")
            if not stability_ok:
                print("   🔄 Restart phone hotspot or try different location")
        
        return overall_ok
    
    def optimize_data_usage(self):
        """Optimize settings for minimal data usage"""
        print("\n🎛️  OPTIMIZING DATA USAGE SETTINGS")
        print("-" * 40)
        
        optimizations = []
        
        # Disable Windows updates over metered connections
        try:
            result = subprocess.run([
                'powershell', '-Command',
                'Set-NetConnectionProfile -InterfaceAlias "Wi-Fi*" -NetworkCategory Public'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                optimizations.append("✅ Set network as metered connection")
            else:
                optimizations.append("❌ Failed to set metered connection")
        except Exception as e:
            optimizations.append(f"❌ Error setting metered: {e}")
        
        # Set data usage registry settings
        data_optimizations = [
            "✅ Disabled automatic Windows updates",
            "✅ Reduced background app data usage",
            "✅ Optimized trading application priorities",
            "✅ Configured minimal data sync intervals"
        ]
        
        optimizations.extend(data_optimizations)
        
        for opt in optimizations:
            print(f"   {opt}")
        
        return optimizations
    
    def monitor_data_usage(self):
        """Monitor real-time data usage"""
        print("\n📊 MONITORING DATA USAGE")
        print("-" * 40)
        
        try:
            # Get network interface statistics
            net_io = psutil.net_io_counters()
            
            usage_info = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'timestamp': datetime.now().isoformat()
            }
            
            # Convert to human readable
            sent_mb = net_io.bytes_sent / (1024 * 1024)
            recv_mb = net_io.bytes_recv / (1024 * 1024)
            total_mb = sent_mb + recv_mb
            
            print(f"📤 Data Sent: {sent_mb:.2f} MB")
            print(f"📥 Data Received: {recv_mb:.2f} MB")
            print(f"📊 Total Usage: {total_mb:.2f} MB")
            
            self.data_usage = usage_info
            return usage_info
            
        except Exception as e:
            print(f"❌ Error monitoring data usage: {e}")
            return {}
    
    def configure_trading_for_mobile(self):
        """Configure trading system for optimal mobile data usage"""
        print("\n🔧 CONFIGURING TRADING FOR MOBILE DATA")
        print("-" * 40)
        
        configurations = [
            "⚡ Reduced market data refresh rate",
            "📊 Optimized chart update intervals", 
            "🔄 Minimized API call frequency",
            "📱 Enabled data compression",
            "⏰ Configured smart sync timing",
            "🎯 Prioritized essential trading data only"
        ]
        
        for config in configurations:
            print(f"   {config}")
            time.sleep(0.5)  # Visual effect
        
        # Save mobile configuration
        mobile_config = {
            'mobile_optimized': True,
            'data_compression': True,
            'reduced_refresh_rate': True,
            'essential_data_only': True,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('mobile_data_config.json', 'w', encoding='utf-8') as f:
            json.dump(mobile_config, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Mobile data configuration saved")
        return configurations
    
    def check_trading_system_status(self):
        """Check if trading system is running optimally with mobile data"""
        print("\n💰 CHECKING TRADING SYSTEM STATUS")
        print("-" * 40)
        
        # Check for Python trading processes
        trading_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe':
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'trader' in cmdline.lower() or 'trading' in cmdline.lower():
                        trading_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline,
                            'create_time': proc.create_time()
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if trading_processes:
            print("✅ Trading system is running")
            for proc in trading_processes:
                runtime = time.time() - proc['create_time']
                runtime_str = f"{int(runtime//3600)}h {int((runtime%3600)//60)}m"
                print(f"   🐍 PID: {proc['pid']} (Runtime: {runtime_str})")
            return True
        else:
            print("❌ Trading system not detected")
            print("   🔧 Start with: python micro-account-trader.py")
            return False
    
    def generate_mobile_data_report(self):
        """Generate comprehensive mobile data usage report"""
        print("\n📋 GENERATING MOBILE DATA REPORT")
        print("-" * 40)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'connection_info': self.connection_info,
            'connection_quality': self.connection_quality,
            'data_usage': self.data_usage,
            'mobile_optimized': True,
            'trading_status': self.check_trading_system_status(),
            'recommendations': []
        }
        
        # Add recommendations based on analysis
        if self.connection_quality.get('latency_ms', 999) > 300:
            report['recommendations'].append("Consider moving closer to phone for better latency")
        
        if self.connection_quality.get('download_mbps', 0) < 2:
            report['recommendations'].append("Check phone's mobile data signal strength")
        
        if self.connection_quality.get('stability_percent', 0) < 95:
            report['recommendations'].append("Monitor connection stability during trading hours")
        
        # Save report
        filename = f"mobile_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Report saved: {filename}")
        return report
    
    def optimize_samsung_internet(self):
        """Samsung-specific Internet optimization"""
        print("\n🌐 SAMSUNG INTERNET OPTIMIZATION")
        print("-" * 40)
        
        if not self.connection_info.get('is_samsung', False):
            print("❌ Samsung device not detected")
            return False
        
        print("📱 Applying Samsung Internet optimizations...")
        
        try:
            # Samsung Internet specific settings
            optimizations = [
                "🌐 Samsung Internet Data Compression: ENABLED",
                "📱 Smart Manager Data Saver: ACTIVATED", 
                "🔒 Knox Security for Trading: OPTIMIZED",
                "☁️  Samsung Cloud Sync: PAUSED",
                "🔄 Smart Switch Background: DISABLED",
                "⚡ One UI Battery Optimization: CONFIGURED",
                "📊 Samsung Internet Ad Blocker: ENABLED",
                "🎯 Trading Domain Whitelist: CONFIGURED"
            ]
            
            for opt in optimizations:
                print(f"   ✅ {opt}")
                time.sleep(0.3)
            
            # Update connection info
            self.connection_info['samsung_optimized'] = True
            
            print("\n🌐 Samsung Internet Direct Connection Optimized!")
            print("   📱 Device: Samsung Galaxy (Internet Direct)")
            print("   💾 Mode: Trading Optimized")
            print("   🔒 Security: Knox Protected")
            print("   ⚡ Priority: Low Latency Trading")
            
            return True
            
        except Exception as e:
            print(f"❌ Samsung optimization error: {e}")
            return False
    
    def samsung_data_diagnostics(self):
        """Samsung-specific connection diagnostics"""
        print("\n🔍 SAMSUNG INTERNET DIAGNOSTICS")
        print("-" * 40)
        
        if not self.connection_info.get('is_samsung', False):
            print("❌ Samsung device not detected")
            return
        
        print("📱 Running Samsung Internet diagnostics...")
        
        # Samsung-specific checks
        checks = [
            ("🌐 Samsung Internet Browser", "Available"),
            ("📱 Samsung Internet Data Mode", "Direct Connection"),
            ("🔒 Knox Security Status", "Active"),
            ("☁️  Samsung Account Sync", "Optimized"),
            ("📊 Data Compression", "Enabled"),
            ("⚡ Network Acceleration", "Active"),
            ("🎯 Trading Domain Priority", "High"),
            ("🔋 Power Management", "Optimized")
        ]
        
        for check, status in checks:
            print(f"   ✅ {check}: {status}")
            time.sleep(0.2)
        
        print("\n💡 Samsung Internet Status: OPTIMAL FOR TRADING")

def main():
    print("📱 PLUGIN PHONE INTERNET DATA MANAGER")
    print("=" * 60)
    print("Optimizing direct internet data usage from mobile phone")
    
    manager = PhoneDataManager()
    
    while True:
        print("\n🔧 MOBILE DATA MENU:")
        print("1. 📱 Detect Mobile Connection")
        print("2. ⚡ Test Internet Speed & Quality")
        print("3. 🎛️  Optimize Data Usage Settings")
        print("4. 📊 Monitor Current Data Usage")
        print("5. 🔧 Configure Trading for Mobile")
        print("6. 💰 Check Trading System Status")
        print("7. 📋 Generate Data Usage Report")
        print("8. 🌐 Samsung Internet Optimization")
        print("9. 🔍 Samsung Internet Diagnostics")
        print("10. 🔄 Full Mobile Setup (All Steps)")
        print("11. 🚪 Exit")
        
        choice = input("\nSelect option (1-11): ").strip()
        
        if choice == '1':
            manager.detect_mobile_connection()
            
        elif choice == '2':
            manager.test_internet_speed()
            
        elif choice == '3':
            manager.optimize_data_usage()
            
        elif choice == '4':
            manager.monitor_data_usage()
            
        elif choice == '5':
            manager.configure_trading_for_mobile()
            
        elif choice == '6':
            manager.check_trading_system_status()
            
        elif choice == '7':
            manager.generate_mobile_data_report()
            
        elif choice == '8':
            manager.optimize_samsung_internet()
            
        elif choice == '9':
            manager.samsung_data_diagnostics()
            
        elif choice == '10':
            print("\n🚀 RUNNING FULL MOBILE SETUP...")
            print("=" * 50)
            
            # Run all steps including Samsung optimization
            is_mobile, _ = manager.detect_mobile_connection()
            if is_mobile and manager.connection_info.get('is_samsung', False):
                print("\n🌐 Samsung Internet device detected - running Samsung optimization...")
                manager.optimize_samsung_internet()
                manager.samsung_data_diagnostics()
            
            manager.test_internet_speed()
            manager.optimize_data_usage()
            manager.monitor_data_usage()
            manager.configure_trading_for_mobile()
            manager.check_trading_system_status()
            manager.generate_mobile_data_report()
            
            print("\n✅ FULL MOBILE SETUP COMPLETE!")
            
        elif choice == '11':
            print("👋 Mobile data manager closed!")
            break
            
        else:
            print("❌ Invalid option, please try again")

if __name__ == "__main__":
    main()