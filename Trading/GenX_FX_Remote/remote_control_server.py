#!/usr/bin/env python3
"""
GenX FX Remote Control Server
Advanced remote control with WebSocket support, authentication, and real-time monitoring
"""

import asyncio
import json
import logging
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import hmac
import base64
from dataclasses import dataclass, asdict
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import sqlite3

import psutil
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("remote_control.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

@dataclass
class RemoteCommand:
    """Remote command structure"""
    command: str
    parameters: Dict[str, Any]
    timestamp: datetime
    user: str
    session_id: str

@dataclass
class SystemStatus:
    """System status information"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    active_processes: List[str]
    trading_status: str
    api_status: str
    timestamp: datetime

class AuthenticationManager:
    """Handles authentication and session management"""
    
    def __init__(self):
        self.secret_key = os.getenv('GENX_REMOTE_SECRET', 'your-secret-key-change-this')
        self.sessions: Dict[str, Dict] = {}
        self.api_keys: Dict[str, str] = {
            'admin': 'genx_admin_2024',
            'trader': 'genx_trader_2024',
            'viewer': 'genx_viewer_2024'
        }
        
    def authenticate_api_key(self, api_key: str) -> Optional[str]:
        """Authenticate using API key"""
        for user, key in self.api_keys.items():
            if key == api_key:
                return user
        return None
    
    def create_session(self, user: str) -> str:
        """Create a new session"""
        session_id = self.generate_token(user + str(time.time()))
        self.sessions[session_id] = {
            'user': user,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[str]:
        """Validate session and return user"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if datetime.now() - session['last_activity'] < timedelta(hours=24):
                session['last_activity'] = datetime.now()
                return session['user']
            else:
                del self.sessions[session_id]
        return None
    
    def generate_token(self, data: str) -> str:
        """Generate secure token"""
        return hashlib.sha256((self.secret_key + data).encode()).hexdigest()

class SystemMonitor:
    """Monitors system resources and trading status"""
    
    def __init__(self):
        self.last_update = datetime.now()
        self.cache_duration = timedelta(seconds=5)  # Cache for 5 seconds
        self._cached_status = None
        
    def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        now = datetime.now()
        if self._cached_status and (now - self.last_update) < self.cache_duration:
            return self._cached_status
            
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
            
            # Active processes (trading related)
            active_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if any(keyword in ' '.join(proc.info['cmdline'] or []).lower() 
                          for keyword in ['genx', 'mt4', 'mt5', 'forex', 'trading']):
                        active_processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Trading status (check if API server is running)
            api_status = self._check_api_status()
            trading_status = self._check_trading_status()
            
            status = SystemStatus(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_io=network_io,
                active_processes=active_processes,
                trading_status=trading_status,
                api_status=api_status,
                timestamp=now
            )
            
            self._cached_status = status
            self.last_update = now
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return SystemStatus(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                active_processes=[],
                trading_status="Unknown",
                api_status="Unknown",
                timestamp=now
            )
    
    def _check_api_status(self) -> str:
        """Check if API server is running"""
        try:
            import requests
            response = requests.get('http://localhost:8080/health', timeout=2)
            return "Running" if response.status_code == 200 else "Error"
        except:
            return "Stopped"
    
    def _check_trading_status(self) -> str:
        """Check trading system status"""
        # Check if GenX processes are running
        for proc in psutil.process_iter(['name']):
            try:
                if 'genx' in proc.info['name'].lower():
                    return "Active"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return "Inactive"

class RemoteController:
    """Handles remote commands and operations"""
    
    def __init__(self):
        self.allowed_commands = {
            'start_trading': self._start_trading,
            'stop_trading': self._stop_trading,
            'restart_api': self._restart_api,
            'get_signals': self._get_signals,
            'get_logs': self._get_logs,
            'system_info': self._get_system_info,
            'start_ea': self._start_ea,
            'stop_ea': self._stop_ea,
            'backup_data': self._backup_data,
            'update_config': self._update_config,
        }
        
    async def execute_command(self, command: RemoteCommand) -> Dict[str, Any]:
        """Execute a remote command"""
        logger.info(f"Executing command: {command.command} by {command.user}")
        
        if command.command not in self.allowed_commands:
            return {
                'success': False,
                'error': f'Unknown command: {command.command}',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            result = await self.allowed_commands[command.command](command.parameters)
            return {
                'success': True,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing command {command.command}: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _start_trading(self, params: Dict[str, Any]) -> str:
        """Start trading system"""
        try:
            # Start the trading platform
            subprocess.Popen([
                sys.executable, 'main.py'
            ], cwd=str(Path(__file__).parent))
            return "Trading system startup initiated"
        except Exception as e:
            raise Exception(f"Failed to start trading system: {e}")
    
    async def _stop_trading(self, params: Dict[str, Any]) -> str:
        """Stop trading system"""
        try:
            # Find and terminate GenX processes
            terminated = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if any(keyword in ' '.join(proc.info['cmdline'] or []).lower() 
                          for keyword in ['genx', 'main.py', 'trading']):
                        proc.terminate()
                        terminated += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return f"Trading system stopped. Terminated {terminated} processes"
        except Exception as e:
            raise Exception(f"Failed to stop trading system: {e}")
    
    async def _restart_api(self, params: Dict[str, Any]) -> str:
        """Restart API server"""
        await self._stop_trading({})
        await asyncio.sleep(2)
        await self._start_trading({})
        return "API server restarted"
    
    async def _get_signals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get trading signals"""
        try:
            signals_file = Path('signal_output/genx_signals.json')
            if signals_file.exists():
                with open(signals_file, 'r') as f:
                    return json.load(f)
            return {'signals': [], 'message': 'No signals available'}
        except Exception as e:
            raise Exception(f"Failed to get signals: {e}")
    
    async def _get_logs(self, params: Dict[str, Any]) -> List[str]:
        """Get system logs"""
        try:
            log_file = Path('logs/genx_trading.log')
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    return lines[-100:]  # Last 100 lines
            return ['No logs available']
        except Exception as e:
            raise Exception(f"Failed to get logs: {e}")
    
    async def _get_system_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get system information"""
        monitor = SystemMonitor()
        status = monitor.get_system_status()
        return asdict(status)
    
    async def _start_ea(self, params: Dict[str, Any]) -> str:
        """Start Expert Advisor"""
        ea_name = params.get('ea_name', 'GenX_VPS_EA')
        return f"EA {ea_name} start command sent"
    
    async def _stop_ea(self, params: Dict[str, Any]) -> str:
        """Stop Expert Advisor"""
        ea_name = params.get('ea_name', 'GenX_VPS_EA')
        return f"EA {ea_name} stop command sent"
    
    async def _backup_data(self, params: Dict[str, Any]) -> str:
        """Backup trading data"""
        backup_path = Path('backups') / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path.mkdir(parents=True, exist_ok=True)
        return f"Backup created at {backup_path}"
    
    async def _update_config(self, params: Dict[str, Any]) -> str:
        """Update configuration"""
        config_data = params.get('config', {})
        return f"Configuration updated with {len(config_data)} parameters" in ['genx', 'main.py']):
                        proc.terminate()
                        terminated += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return f"Terminated {terminated} trading processes"
        except Exception as e:
            raise Exception(f"Failed to stop trading system: {e}")
    
    async def _restart_api(self, params: Dict[str, Any]) -> str:
        """Restart API server"""
        try:
            # Stop existing API server
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'simple-api-server.py' in cmdline or 'api' in cmdline:
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Start API server
            subprocess.Popen([
                sys.executable, 'simple-api-server.py'
            ], cwd=str(Path(__file__).parent))
            
            return "API server restarted"
        except Exception as e:
            raise Exception(f"Failed to restart API server: {e}")
    
    async def _get_signals(self, params: Dict[str, Any]) -> List[Dict]:
        """Get current trading signals"""
        try:
            signals = []
            signals_file = Path(__file__).parent / "MT4_Signals.csv"
            if signals_file.exists():
                with open(signals_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:  # Skip header
                        parts = line.strip().split(',')
                        if len(parts) >= 8:
                            signals.append({
                                'timestamp': parts[0],
                                'symbol': parts[1],
                                'action': parts[2],
                                'entry_price': parts[3],
                                'stop_loss': parts[4],
                                'take_profit': parts[5],
                                'confidence': parts[6],
                                'reasoning': parts[7]
                            })
            return signals
        except Exception as e:
            raise Exception(f"Failed to get signals: {e}")
    
    async def _get_logs(self, params: Dict[str, Any]) -> List[str]:
        """Get system logs"""
        try:
            lines = params.get('lines', 100)
            log_files = ['remote_control.log', 'api-server.log', 'genx_fx.log']
            
            logs = []
            for log_file in log_files:
                log_path = Path(__file__).parent / log_file
                if log_path.exists():
                    with open(log_path, 'r') as f:
                        file_lines = f.readlines()
                        logs.extend([f"[{log_file}] {line.strip()}" for line in file_lines[-lines:]])
            
            return logs
        except Exception as e:
            raise Exception(f"Failed to get logs: {e}")
    
    async def _get_system_info(self, params: Dict[str, Any]) -> Dict:
        """Get detailed system information"""
        try:
            monitor = SystemMonitor()
            status = monitor.get_system_status()
            return asdict(status)
        except Exception as e:
            raise Exception(f"Failed to get system info: {e}")
    
    async def _start_ea(self, params: Dict[str, Any]) -> str:
        """Start Expert Advisor"""
        ea_name = params.get('ea_name', 'GenX_Gold_Master_EA')
        try:
            # This would integrate with MT4/MT5 to start the EA
            return f"Started EA: {ea_name}"
        except Exception as e:
            raise Exception(f"Failed to start EA: {e}")
    
    async def _stop_ea(self, params: Dict[str, Any]) -> str:
        """Stop Expert Advisor"""
        ea_name = params.get('ea_name', 'all')
        try:
            # This would integrate with MT4/MT5 to stop the EA
            return f"Stopped EA: {ea_name}"
        except Exception as e:
            raise Exception(f"Failed to stop EA: {e}")
    
    async def _backup_data(self, params: Dict[str, Any]) -> str:
        """Backup trading data"""
        try:
            backup_path = Path(__file__).parent / "backups" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy important files
            import shutil
            files_to_backup = ['config/', 'data/', 'logs/', '*.csv']
            copied_files = 0
            
            for pattern in files_to_backup:
                for file_path in Path(__file__).parent.glob(pattern):
                    if file_path.is_file():
                        shutil.copy2(file_path, backup_path)
                        copied_files += 1
                    elif file_path.is_dir():
                        shutil.copytree(file_path, backup_path / file_path.name, dirs_exist_ok=True)
                        copied_files += 1
            
            return f"Backup created at {backup_path} with {copied_files} items"
        except Exception as e:
            raise Exception(f"Failed to backup data: {e}")
    
    async def _update_config(self, params: Dict[str, Any]) -> str:
        """Update configuration"""
        try:
            config_updates = params.get('updates', {})
            config_file = Path(__file__).parent / "config" / "config.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update configuration
            for key, value in config_updates.items():
                config[key] = value
            
            # Save updated configuration
            config_file.parent.mkdir(exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return f"Updated {len(config_updates)} configuration items"
        except Exception as e:
            raise Exception(f"Failed to update config: {e}")

class WebSocketHandler:
    """WebSocket handler for real-time communication"""
    
    def __init__(self, auth_manager: AuthenticationManager, controller: RemoteController):
        self.auth_manager = auth_manager
        self.controller = controller
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.monitor = SystemMonitor()
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        try:
            # Authenticate client
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)
            
            api_key = auth_data.get('api_key')
            user = self.auth_manager.authenticate_api_key(api_key)
            
            if not user:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Authentication failed'
                }))
                return
            
            session_id = self.auth_manager.create_session(user)
            self.clients[session_id] = websocket
            
            await websocket.send(json.dumps({
                'type': 'auth_success',
                'session_id': session_id,
                'user': user
            }))
            
            logger.info(f"WebSocket client connected: {user} (session: {session_id})")
            
            # Handle client messages
            await self.handle_client_messages(websocket, session_id, user)
            
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            # Clean up
            session_id = next((sid for sid, ws in self.clients.items() if ws == websocket), None)
            if session_id:
                del self.clients[session_id]
    
    async def handle_client_messages(self, websocket, session_id: str, user: str):
        """Handle messages from WebSocket clients"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'command':
                    # Execute remote command
                    command = RemoteCommand(
                        command=data['command'],
                        parameters=data.get('parameters', {}),
                        timestamp=datetime.now(),
                        user=user,
                        session_id=session_id
                    )
                    
                    result = await self.controller.execute_command(command)
                    
                    await websocket.send(json.dumps({
                        'type': 'command_result',
                        'command': data['command'],
                        'result': result
                    }))
                
                elif data['type'] == 'get_status':
                    # Send system status
                    status = self.monitor.get_system_status()
                    await websocket.send(json.dumps({
                        'type': 'system_status',
                        'status': asdict(status)
                    }))
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def broadcast_status_updates(self):
        """Broadcast system status updates to all connected clients"""
        while True:
            try:
                if self.clients:
                    status = self.monitor.get_system_status()
                    message = json.dumps({
                        'type': 'status_update',
                        'status': asdict(status)
                    }, default=str)
                    
                    # Send to all connected clients
                    disconnected = []
                    for session_id, websocket in self.clients.items():
                        try:
                            await websocket.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            disconnected.append(session_id)
                    
                    # Remove disconnected clients
                    for session_id in disconnected:
                        del self.clients[session_id]
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error broadcasting status: {e}")
                await asyncio.sleep(10)

class RemoteControlHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for REST API endpoints"""
    
    def __init__(self, auth_manager, controller, *args, **kwargs):
        self.auth_manager = auth_manager
        self.controller = controller
        self.monitor = SystemMonitor()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if not self._authenticate_request():
                return
            
            if path == "/remote/status":
                self._send_status_response()
            elif path == "/remote/logs":
                self._send_logs_response()
            elif path == "/remote/signals":
                self._send_signals_response()
            elif path == "/remote/dashboard":
                self._send_dashboard_response()
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, "Internal Server Error")
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if not self._authenticate_request():
                return
            
            if path == "/remote/command":
                self._handle_command_request()
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, "Internal Server Error")
    
    def _authenticate_request(self) -> bool:
        """Authenticate HTTP request"""
        api_key = self.headers.get('X-API-Key')
        if not api_key:
            self.send_error(401, "Missing API Key")
            return False
        
        user = self.auth_manager.authenticate_api_key(api_key)
        if not user:
            self.send_error(401, "Invalid API Key")
            return False
        
        self.current_user = user
        return True
    
    def _send_status_response(self):
        """Send system status response"""
        status = self.monitor.get_system_status()
        response = asdict(status)
        
        self._send_json_response(response)
    
    def _send_logs_response(self):
        """Send logs response"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            lines = int(query_params.get('lines', ['100'])[0])
            
            log_files = ['remote_control.log', 'api-server.log']
            logs = []
            
            for log_file in log_files:
                log_path = Path(__file__).parent / log_file
                if log_path.exists():
                    with open(log_path, 'r') as f:
                        file_lines = f.readlines()
                        logs.extend([f"[{log_file}] {line.strip()}" for line in file_lines[-lines:]])
            
            self._send_json_response({'logs': logs})
            
        except Exception as e:
            self.send_error(500, f"Error getting logs: {e}")
    
    def _send_signals_response(self):
        """Send trading signals response"""
        try:
            signals = []
            signals_file = Path(__file__).parent / "MT4_Signals.csv"
            if signals_file.exists():
                with open(signals_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:  # Skip header
                        parts = line.strip().split(',')
                        if len(parts) >= 8:
                            signals.append({
                                'timestamp': parts[0],
                                'symbol': parts[1],
                                'action': parts[2],
                                'entry_price': parts[3],
                                'stop_loss': parts[4],
                                'take_profit': parts[5],
                                'confidence': parts[6],
                                'reasoning': parts[7]
                            })
            
            self._send_json_response({'signals': signals})
            
        except Exception as e:
            self.send_error(500, f"Error getting signals: {e}")
    
    def _send_dashboard_response(self):
        """Send dashboard HTML response"""
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GenX FX Remote Control Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .card { background: white; border-radius: 8px; padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .status { display: flex; justify-content: space-between; align-items: center; }
                .metric { text-align: center; }
                .metric-value { font-size: 2em; font-weight: bold; color: #007acc; }
                .metric-label { font-size: 0.9em; color: #666; }
                .button { background: #007acc; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
                .button:hover { background: #005a99; }
                .logs { background: #1e1e1e; color: #fff; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto; }
                .signals-table { width: 100%; border-collapse: collapse; }
                .signals-table th, .signals-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .signals-table th { background-color: #f2f2f2; }
                .ws-status { padding: 10px; border-radius: 4px; margin: 10px 0; }
                .ws-connected { background: #d4edda; color: #155724; }
                .ws-disconnected { background: #f8d7da; color: #721c24; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h1>🚀 GenX FX Remote Control Dashboard</h1>
                    <div id="ws-status" class="ws-status ws-disconnected">WebSocket: Disconnected</div>
                </div>
                
                <div class="card">
                    <h2>System Status</h2>
                    <div class="status">
                        <div class="metric">
                            <div id="cpu-usage" class="metric-value">--</div>
                            <div class="metric-label">CPU Usage %</div>
                        </div>
                        <div class="metric">
                            <div id="memory-usage" class="metric-value">--</div>
                            <div class="metric-label">Memory Usage %</div>
                        </div>
                        <div class="metric">
                            <div id="trading-status" class="metric-value">--</div>
                            <div class="metric-label">Trading Status</div>
                        </div>
                        <div class="metric">
                            <div id="api-status" class="metric-value">--</div>
                            <div class="metric-label">API Status</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Remote Controls</h2>
                    <button class="button" onclick="executeCommand('start_trading')">Start Trading</button>
                    <button class="button" onclick="executeCommand('stop_trading')">Stop Trading</button>
                    <button class="button" onclick="executeCommand('restart_api')">Restart API</button>
                    <button class="button" onclick="executeCommand('get_signals')">Get Signals</button>
                    <button class="button" onclick="executeCommand('backup_data')">Backup Data</button>
                    <button class="button" onclick="getSystemInfo()">Refresh Status</button>
                </div>
                
                <div class="card">
                    <h2>Recent Logs</h2>
                    <div id="logs" class="logs">Loading logs...</div>
                    <button class="button" onclick="refreshLogs()">Refresh Logs</button>
                </div>
                
                <div class="card">
                    <h2>Trading Signals</h2>
                    <div id="signals-container">Loading signals...</div>
                    <button class="button" onclick="refreshSignals()">Refresh Signals</button>
                </div>
            </div>
            
            <script>
                let ws = null;
                const API_KEY = 'genx_admin_2024'; // Change this to your API key
                
                // WebSocket connection
                function connectWebSocket() {
                    try {
                        ws = new WebSocket('ws://localhost:8081');
                        
                        ws.onopen = function() {
                            document.getElementById('ws-status').className = 'ws-status ws-connected';
                            document.getElementById('ws-status').textContent = 'WebSocket: Connected';
                            
                            // Send authentication
                            ws.send(JSON.stringify({
                                api_key: API_KEY
                            }));
                        };
                        
                        ws.onmessage = function(event) {
                            const data = JSON.parse(event.data);
                            handleWebSocketMessage(data);
                        };
                        
                        ws.onclose = function() {
                            document.getElementById('ws-status').className = 'ws-status ws-disconnected';
                            document.getElementById('ws-status').textContent = 'WebSocket: Disconnected';
                            
                            // Reconnect after 5 seconds
                            setTimeout(connectWebSocket, 5000);
                        };
                        
                    } catch (error) {
                        console.error('WebSocket connection error:', error);
                    }
                }
                
                function handleWebSocketMessage(data) {
                    if (data.type === 'auth_success') {
                        console.log('WebSocket authenticated as:', data.user);
                        // Request initial status
                        ws.send(JSON.stringify({type: 'get_status'}));
                    }
                    else if (data.type === 'system_status' || data.type === 'status_update') {
                        updateSystemStatus(data.status);
                    }
                    else if (data.type === 'command_result') {
                        handleCommandResult(data);
                    }
                }
                
                function updateSystemStatus(status) {
                    document.getElementById('cpu-usage').textContent = status.cpu_usage.toFixed(1);
                    document.getElementById('memory-usage').textContent = status.memory_usage.toFixed(1);
                    document.getElementById('trading-status').textContent = status.trading_status;
                    document.getElementById('api-status').textContent = status.api_status;
                }
                
                function executeCommand(command, params = {}) {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({
                            type: 'command',
                            command: command,
                            parameters: params
                        }));
                    } else {
                        alert('WebSocket not connected. Please wait for reconnection.');
                    }
                }
                
                function handleCommandResult(data) {
                    if (data.result.success) {
                        alert(`Command ${data.command} executed successfully: ${JSON.stringify(data.result.result)}`);
                    } else {
                        alert(`Command ${data.command} failed: ${data.result.error}`);
                    }
                }
                
                function getSystemInfo() {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({type: 'get_status'}));
                    }
                }
                
                function refreshLogs() {
                    fetch('/remote/logs?lines=50', {
                        headers: {'X-API-Key': API_KEY}
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('logs').innerHTML = data.logs.join('<br>');
                    })
                    .catch(error => console.error('Error:', error));
                }
                
                function refreshSignals() {
                    fetch('/remote/signals', {
                        headers: {'X-API-Key': API_KEY}
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.signals.length > 0) {
                            let table = '<table class="signals-table"><tr><th>Time</th><th>Symbol</th><th>Action</th><th>Entry</th><th>SL</th><th>TP</th><th>Confidence</th></tr>';
                            data.signals.forEach(signal => {
                                table += `<tr><td>${signal.timestamp}</td><td>${signal.symbol}</td><td>${signal.action}</td><td>${signal.entry_price}</td><td>${signal.stop_loss}</td><td>${signal.take_profit}</td><td>${signal.confidence}</td></tr>`;
                            });
                            table += '</table>';
                            document.getElementById('signals-container').innerHTML = table;
                        } else {
                            document.getElementById('signals-container').innerHTML = 'No signals available';
                        }
                    })
                    .catch(error => console.error('Error:', error));
                }
                
                // Initialize
                connectWebSocket();
                refreshLogs();
                refreshSignals();
                
                // Auto-refresh every 30 seconds
                setInterval(refreshLogs, 30000);
                setInterval(refreshSignals, 30000);
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(dashboard_html.encode())
    
    def _handle_command_request(self):
        """Handle remote command requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            command = RemoteCommand(
                command=data['command'],
                parameters=data.get('parameters', {}),
                timestamp=datetime.now(),
                user=self.current_user,
                session_id='http_' + str(int(time.time()))
            )
            
            # Execute command synchronously for HTTP requests
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.controller.execute_command(command))
            
            self._send_json_response(result)
            
        except Exception as e:
            self.send_error(400, f"Error processing command: {e}")
    
    def _send_json_response(self, data):
        """Send JSON response"""
        response = json.dumps(data, default=str)
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

class RemoteControlServer:
    """Main remote control server"""
    
    def __init__(self, http_port=8081, websocket_port=8082):
        self.http_port = http_port
        self.websocket_port = websocket_port
        
        self.auth_manager = AuthenticationManager()
        self.controller = RemoteController()
        self.websocket_handler = WebSocketHandler(self.auth_manager, self.controller)
        
        self.http_server = None
        self.websocket_server = None
    
    def start(self):
        """Start the remote control server"""
        try:
            logger.info("Starting GenX FX Remote Control Server...")
            
            # Start HTTP server
            handler = lambda *args, **kwargs: RemoteControlHTTPHandler(
                self.auth_manager, self.controller, *args, **kwargs
            )
            self.http_server = HTTPServer(('0.0.0.0', self.http_port), handler)
            
            http_thread = threading.Thread(target=self.http_server.serve_forever)
            http_thread.daemon = True
            http_thread.start()
            
            logger.info(f"HTTP server started on port {self.http_port}")
            logger.info(f"Dashboard: http://localhost:{self.http_port}/remote/dashboard")
            
            # Start WebSocket server
            async def start_websocket_server():
                self.websocket_server = await websockets.serve(
                    self.websocket_handler.register_client,
                    '0.0.0.0',
                    self.websocket_port
                )
                logger.info(f"WebSocket server started on port {self.websocket_port}")
                
                # Start status broadcasting
                asyncio.create_task(self.websocket_handler.broadcast_status_updates())
                
                await self.websocket_server.wait_closed()
            
            # Run WebSocket server in event loop
            asyncio.run(start_websocket_server())
            
        except Exception as e:
            logger.error(f"Failed to start remote control server: {e}")
            raise
    
    def stop(self):
        """Stop the remote control server"""
        if self.http_server:
            self.http_server.shutdown()
            logger.info("HTTP server stopped")
        
        if self.websocket_server:
            self.websocket_server.close()
            logger.info("WebSocket server stopped")

def main():
    """Main entry point"""
    logger.info("Initializing GenX FX Remote Control System...")
    
    # Create and start remote control server
    server = RemoteControlServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down remote control server...")
        server.stop()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()