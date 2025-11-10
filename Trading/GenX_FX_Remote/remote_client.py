#!/usr/bin/env python3
"""
GenX FX Remote Client
Command-line interface for remote control of GenX FX trading platform
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any
import websockets
import requests
import argparse
from datetime import datetime

class GenXRemoteClient:
    """Remote client for GenX FX platform"""
    
    def __init__(self, server_url: str = "localhost", http_port: int = 8081, ws_port: int = 8082, api_key: str = "genx_admin_2024"):
        self.server_url = server_url
        self.http_port = http_port
        self.ws_port = ws_port
        self.api_key = api_key
        
        self.base_url = f"http://{server_url}:{http_port}"
        self.ws_url = f"ws://{server_url}:{ws_port}"
        
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status via HTTP"""
        try:
            response = requests.get(f"{self.base_url}/remote/status", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Get system logs via HTTP"""
        try:
            response = requests.get(f"{self.base_url}/remote/logs?lines={lines}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_signals(self) -> Dict[str, Any]:
        """Get trading signals via HTTP"""
        try:
            response = requests.get(f"{self.base_url}/remote/signals", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def execute_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute command via HTTP"""
        try:
            payload = {
                'command': command,
                'parameters': parameters or {}
            }
            response = requests.post(f"{self.base_url}/remote/command", 
                                   json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def websocket_client(self):
        """WebSocket client for real-time monitoring"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Authenticate
                await websocket.send(json.dumps({
                    'api_key': self.api_key
                }))
                
                # Wait for auth response
                auth_response = await websocket.recv()
                auth_data = json.loads(auth_response)
                
                if auth_data.get('type') == 'auth_success':
                    print(f"✅ WebSocket connected as: {auth_data.get('user')}")
                    
                    # Start real-time monitoring
                    await websocket.send(json.dumps({'type': 'get_status'}))
                    
                    # Listen for messages
                    async for message in websocket:
                        data = json.loads(message)
                        self._handle_websocket_message(data)
                        
                else:
                    print("❌ WebSocket authentication failed")
                    
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    def _handle_websocket_message(self, data: Dict[str, Any]):
        """Handle WebSocket messages"""
        if data['type'] == 'system_status' or data['type'] == 'status_update':
            status = data['status']
            timestamp = datetime.fromisoformat(status['timestamp'].replace('Z', '+00:00'))
            print(f"\n📊 System Status Update ({timestamp.strftime('%H:%M:%S')})")
            print(f"   CPU: {status['cpu_usage']:.1f}% | Memory: {status['memory_usage']:.1f}%")
            print(f"   Trading: {status['trading_status']} | API: {status['api_status']}")
            
        elif data['type'] == 'command_result':
            print(f"\n🔧 Command Result: {data['command']}")
            result = data['result']
            if result['success']:
                print(f"   ✅ Success: {result['result']}")
            else:
                print(f"   ❌ Error: {result['error']}")

def main():
    parser = argparse.ArgumentParser(description='GenX FX Remote Client')
    parser.add_argument('--server', default='localhost', help='Server URL')
    parser.add_argument('--http-port', type=int, default=8081, help='HTTP port')
    parser.add_argument('--ws-port', type=int, default=8082, help='WebSocket port')
    parser.add_argument('--api-key', default='genx_admin_2024', help='API key')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Get system logs')
    logs_parser.add_argument('--lines', type=int, default=50, help='Number of log lines')
    
    # Signals command
    signals_parser = subparsers.add_parser('signals', help='Get trading signals')
    
    # Execute command
    exec_parser = subparsers.add_parser('exec', help='Execute remote command')
    exec_parser.add_argument('cmd', help='Command to execute')
    exec_parser.add_argument('--params', help='Parameters as JSON string')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Real-time monitoring via WebSocket')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Open dashboard in browser')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create client
    client = GenXRemoteClient(
        server_url=args.server,
        http_port=args.http_port,
        ws_port=args.ws_port,
        api_key=args.api_key
    )
    
    # Execute command
    if args.command == 'status':
        print("📊 Getting system status...")
        result = client.get_system_status()
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ CPU: {result['cpu_usage']:.1f}%")
            print(f"✅ Memory: {result['memory_usage']:.1f}%")
            print(f"✅ Disk: {result['disk_usage']:.1f}%")
            print(f"✅ Trading Status: {result['trading_status']}")
            print(f"✅ API Status: {result['api_status']}")
            print(f"✅ Active Processes: {len(result['active_processes'])}")
    
    elif args.command == 'logs':
        print(f"📝 Getting last {args.lines} log lines...")
        result = client.get_logs(args.lines)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            logs = result.get('logs', [])
            for log in logs[-20:]:  # Show last 20 lines
                print(f"   {log}")
    
    elif args.command == 'signals':
        print("📈 Getting trading signals...")
        result = client.get_signals()
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            signals = result.get('signals', [])
            if signals:
                print(f"✅ Found {len(signals)} signals:")
                for signal in signals[-5:]:  # Show last 5 signals
                    print(f"   {signal['timestamp']} | {signal['symbol']} | {signal['action']} | {signal['entry_price']}")
            else:
                print("ℹ️  No signals available")
    
    elif args.command == 'exec':
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError:
                print("❌ Invalid JSON parameters")
                return
        
        print(f"🔧 Executing command: {args.cmd}")
        result = client.execute_command(args.cmd, params)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            if result['success']:
                print(f"✅ Success: {result['result']}")
            else:
                print(f"❌ Failed: {result['error']}")
    
    elif args.command == 'monitor':
        print("👀 Starting real-time monitoring...")
        print("Press Ctrl+C to stop")
        try:
            asyncio.run(client.websocket_client())
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
    
    elif args.command == 'dashboard':
        import webbrowser
        dashboard_url = f"http://{args.server}:{args.http_port}/remote/dashboard"
        print(f"🌐 Opening dashboard: {dashboard_url}")
        webbrowser.open(dashboard_url)

if __name__ == "__main__":
    main()