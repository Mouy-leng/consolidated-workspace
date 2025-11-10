#!/usr/bin/env python3
"""
Hidden Hotspot Detection and Connection System
Detects and connects to plugin device hotspots with hidden SSIDs
"""

import sys
import subprocess
import json
import time
import re
from datetime import datetime
import logging

# Fix Windows Unicode issues
sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hotspot_connection.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class HotspotDetector:
    def __init__(self):
        self.detected_devices = {}
        self.hidden_ssids = []
        self.plugin_devices = []
        
    def scan_hidden_networks(self):
        """Scan for hidden SSIDs and plugin device hotspots"""
        print("🔍 SCANNING FOR HIDDEN HOTSPOTS")
        print("=" * 50)
        
        try:
            # Run netsh to scan available networks
            result = subprocess.run([
                'netsh', 'wlan', 'show', 'network', 'mode=bssid'
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                networks = self.parse_network_scan(result.stdout)
                self.detect_plugin_devices(networks)
                return networks
            else:
                print(f"❌ Network scan failed: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"❌ Error scanning networks: {e}")
            return []
    
    def parse_network_scan(self, scan_output):
        """Parse netsh wlan scan output"""
        networks = []
        current_network = {}
        
        lines = scan_output.split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('SSID'):
                if current_network:
                    networks.append(current_network)
                ssid_match = re.search(r'SSID \d+ : (.+)', line)
                current_network = {
                    'ssid': ssid_match.group(1).strip() if ssid_match else '',
                    'signal': '',
                    'authentication': '',
                    'encryption': '',
                    'bssid': ''
                }
            elif 'Signal' in line:
                signal_match = re.search(r'Signal\s+:\s+(\d+)%', line)
                if signal_match:
                    current_network['signal'] = signal_match.group(1)
            elif 'Authentication' in line:
                auth_match = re.search(r'Authentication\s+:\s+(.+)', line)
                if auth_match:
                    current_network['authentication'] = auth_match.group(1).strip()
            elif 'Encryption' in line:
                enc_match = re.search(r'Encryption\s+:\s+(.+)', line)
                if enc_match:
                    current_network['encryption'] = enc_match.group(1).strip()
            elif 'BSSID' in line:
                bssid_match = re.search(r'BSSID \d+\s+:\s+([a-fA-F0-9:]+)', line)
                if bssid_match:
                    current_network['bssid'] = bssid_match.group(1)
        
        if current_network:
            networks.append(current_network)
            
        return networks
    
    def detect_plugin_devices(self, networks):
        """Detect potential plugin device hotspots"""
        print("\n📱 DETECTING PLUGIN DEVICE HOTSPOTS")
        print("-" * 40)
        
        # Common plugin device patterns
        device_patterns = [
            r'TECNO.*',           # TECNO phones
            r'Galaxy.*',          # Samsung Galaxy
            r'iPhone.*',          # iPhones
            r'Android.*',         # Android devices
            r'.*_5G',            # 5G networks
            r'.*hotspot.*',      # Generic hotspots
            r'.*mobile.*',       # Mobile hotspots
            r'.*portable.*',     # Portable devices
            r'^[A-Z0-9]{6,12}$', # Random device names
        ]
        
        plugin_devices = []
        hidden_networks = []
        
        for network in networks:
            ssid = network.get('ssid', '')
            signal = network.get('signal', '0')
            
            # Check for hidden networks (empty SSID)
            if not ssid or ssid.strip() == '':
                hidden_networks.append({
                    'type': 'hidden',
                    'bssid': network.get('bssid', ''),
                    'signal': signal,
                    'authentication': network.get('authentication', ''),
                    'encryption': network.get('encryption', '')
                })
                print(f"🔒 Hidden Network: BSSID {network.get('bssid', 'Unknown')} (Signal: {signal}%)")
                continue
            
            # Check for plugin device patterns
            for pattern in device_patterns:
                if re.match(pattern, ssid, re.IGNORECASE):
                    plugin_devices.append({
                        'ssid': ssid,
                        'type': 'plugin_device',
                        'signal': signal,
                        'bssid': network.get('bssid', ''),
                        'authentication': network.get('authentication', ''),
                        'encryption': network.get('encryption', '')
                    })
                    print(f"📱 Plugin Device: {ssid} (Signal: {signal}%)")
                    break
        
        self.plugin_devices = plugin_devices
        self.hidden_ssids = hidden_networks
        
        print(f"\n✅ Found {len(plugin_devices)} plugin devices")
        print(f"✅ Found {len(hidden_networks)} hidden networks")
        
        return plugin_devices, hidden_networks
    
    def connect_to_hidden_network(self, ssid, password=None):
        """Connect to a hidden network by SSID"""
        print(f"\n🔗 CONNECTING TO HIDDEN NETWORK: {ssid}")
        print("-" * 40)
        
        # Create temporary profile for hidden network
        profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
        <nonBroadcast>true</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password if password else ''}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        
        # Save profile to temp file
        profile_path = f"temp_profile_{ssid}.xml"
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                f.write(profile_xml)
            
            # Add profile
            add_result = subprocess.run([
                'netsh', 'wlan', 'add', 'profile', f'filename={profile_path}'
            ], capture_output=True, text=True)
            
            if add_result.returncode == 0:
                print(f"✅ Profile added for {ssid}")
                
                # Connect to network
                connect_result = subprocess.run([
                    'netsh', 'wlan', 'connect', f'name={ssid}'
                ], capture_output=True, text=True)
                
                if connect_result.returncode == 0:
                    print(f"✅ Connected to {ssid}")
                    return True
                else:
                    print(f"❌ Connection failed: {connect_result.stderr}")
                    return False
            else:
                print(f"❌ Profile creation failed: {add_result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to {ssid}: {e}")
            return False
        finally:
            # Clean up temp file
            try:
                import os
                if os.path.exists(profile_path):
                    os.remove(profile_path)
            except:
                pass
    
    def connect_to_plugin_device(self, device_info):
        """Connect to a detected plugin device"""
        ssid = device_info.get('ssid', '')
        print(f"\n📱 CONNECTING TO PLUGIN DEVICE: {ssid}")
        print("-" * 40)
        
        # Try common plugin device passwords
        common_passwords = [
            '',              # Open network
            '12345678',      # Common default
            'password',      # Generic
            'admin',         # Admin default
            ssid.lower(),    # SSID as password
            ssid,            # SSID exact
            '00000000',      # Zeros
            '11111111',      # Ones
        ]
        
        for password in common_passwords:
            print(f"🔑 Trying password: {'(open)' if not password else '***'}")
            
            try:
                # Try to connect
                if password:
                    connect_cmd = f'netsh wlan connect name="{ssid}" key={password}'
                else:
                    connect_cmd = f'netsh wlan connect name="{ssid}"'
                
                result = subprocess.run(connect_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Connected to {ssid} successfully!")
                    time.sleep(3)  # Wait for connection to establish
                    
                    # Verify connection
                    if self.verify_connection(ssid):
                        return True
                else:
                    print(f"❌ Connection attempt failed")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
            time.sleep(2)  # Wait between attempts
        
        print(f"❌ Could not connect to {ssid}")
        return False
    
    def verify_connection(self, expected_ssid=None):
        """Verify current network connection"""
        try:
            result = subprocess.run([
                'netsh', 'wlan', 'show', 'interfaces'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Check if connected
                if 'State                   : connected' in output:
                    # Extract SSID
                    ssid_match = re.search(r'SSID\s+:\s+(.+)', output)
                    if ssid_match:
                        current_ssid = ssid_match.group(1).strip()
                        print(f"✅ Connected to: {current_ssid}")
                        
                        if expected_ssid and current_ssid == expected_ssid:
                            return True
                        elif not expected_ssid:
                            return True
                
                print("❌ Not connected to any network")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying connection: {e}")
            return False
    
    def restart_live_trading(self):
        """Restart live trading system after network connection"""
        print("\n🚀 RESTARTING LIVE TRADING SYSTEM")
        print("=" * 50)
        
        # Check if trading is already running
        try:
            result = subprocess.run([
                'powershell', '-Command', 
                "Get-Process | Where-Object {$_.ProcessName -eq 'python'} | Select-Object Id, ProcessName"
            ], capture_output=True, text=True)
            
            if 'python' in result.stdout:
                print("✅ Python trading processes already running")
                print(result.stdout)
            else:
                print("🔄 Starting live trading system...")
                
                # Start live trading
                subprocess.Popen([
                    'python', 'micro-account-trader.py'
                ], shell=True)
                
                time.sleep(5)
                print("✅ Live trading system started")
                
        except Exception as e:
            print(f"❌ Error restarting trading: {e}")
    
    def generate_connection_report(self):
        """Generate hotspot connection report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'plugin_devices_found': len(self.plugin_devices),
            'hidden_networks_found': len(self.hidden_ssids),
            'plugin_devices': self.plugin_devices,
            'hidden_networks': self.hidden_ssids,
            'connection_status': self.verify_connection()
        }
        
        # Save report
        with open('hotspot_connection_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Connection report saved: hotspot_connection_report.json")
        return report

def main():
    print("📡 HIDDEN HOTSPOT CONNECTION SYSTEM")
    print("=" * 60)
    print("Detecting plugin device hotspots with hidden SSIDs")
    
    detector = HotspotDetector()
    
    while True:
        print("\n🔧 HOTSPOT CONNECTION MENU:")
        print("1. 🔍 Scan for Hidden Networks & Plugin Devices")
        print("2. 📱 Connect to Plugin Device")
        print("3. 🔒 Connect to Hidden Network (Manual SSID)")
        print("4. ✅ Verify Current Connection")
        print("5. 🚀 Restart Live Trading")
        print("6. 📋 Generate Connection Report")
        print("7. 🚪 Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            networks = detector.scan_hidden_networks()
            
        elif choice == '2':
            if detector.plugin_devices:
                print("\n📱 AVAILABLE PLUGIN DEVICES:")
                for i, device in enumerate(detector.plugin_devices):
                    print(f"   {i+1}. {device['ssid']} (Signal: {device['signal']}%)")
                
                try:
                    selection = int(input("\nSelect device (number): ")) - 1
                    if 0 <= selection < len(detector.plugin_devices):
                        detector.connect_to_plugin_device(detector.plugin_devices[selection])
                    else:
                        print("❌ Invalid selection")
                except ValueError:
                    print("❌ Please enter a valid number")
            else:
                print("❌ No plugin devices found. Run scan first.")
                
        elif choice == '3':
            ssid = input("Enter hidden SSID name: ").strip()
            password = input("Enter password (or press Enter for open): ").strip()
            if ssid:
                detector.connect_to_hidden_network(ssid, password if password else None)
            else:
                print("❌ SSID cannot be empty")
                
        elif choice == '4':
            detector.verify_connection()
            
        elif choice == '5':
            detector.restart_live_trading()
            
        elif choice == '6':
            detector.generate_connection_report()
            
        elif choice == '7':
            print("👋 Hotspot connection system closed!")
            break
            
        else:
            print("❌ Invalid option, please try again")

if __name__ == "__main__":
    main()