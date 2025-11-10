#!/usr/bin/env python3
"""
GenX_FX Monitoring Dashboard
Web-based interface for monitoring and managing 24/7 services
"""

import json
import os
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
import threading
import subprocess
import sys

class MonitoringDashboard:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.status_file = self.project_root / "service_status.json"
        self.config_file = self.project_root / "service_config.json"
        
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_HTML)
        
        @self.app.route('/api/status')
        def get_status():
            """Get current system status"""
            try:
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/logs/<service_name>')
        def get_logs(service_name):
            """Get service logs"""
            try:
                logs_dir = self.project_root / "logs" / "service"
                log_files = list(logs_dir.glob("*.log"))
                
                if not log_files:
                    return jsonify({"logs": "No log files found"})
                
                # Get latest log file
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                
                with open(latest_log, 'r') as f:
                    logs = f.read().split('\\n')[-100:]  # Last 100 lines
                
                return jsonify({"logs": '\\n'.join(logs)})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/service/<action>', methods=['POST'])
        def service_action(action):
            """Control services"""
            try:
                data = request.get_json() or {}
                service_name = data.get('service_name', '')
                
                if action == 'start':
                    cmd = ['python', 'genx_24_7_service.py', 'start']
                elif action == 'stop':
                    cmd = ['python', 'genx_24_7_service.py', 'stop']
                elif action == 'restart':
                    cmd = ['python', 'genx_24_7_service.py', 'restart']
                else:
                    return jsonify({"error": "Invalid action"}), 400
                
                if service_name:
                    cmd.extend(['--service', service_name])
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
                
                return jsonify({
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/system')
        def get_system_info():
            """Get system information"""
            try:
                # System info
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage(str(self.project_root))
                
                # Process info
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        if 'python' in proc.info['name'].lower():
                            processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                return jsonify({
                    "cpu_percent": cpu_percent,
                    "memory": {
                        "used_mb": memory.used / 1024 / 1024,
                        "total_mb": memory.total / 1024 / 1024,
                        "percent": memory.percent
                    },
                    "disk": {
                        "used_gb": disk.used / 1024 / 1024 / 1024,
                        "total_gb": disk.total / 1024 / 1024 / 1024,
                        "percent": (disk.used / disk.total) * 100
                    },
                    "processes": processes
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def run(self, host='127.0.0.1', port=9000, debug=False):
        """Run the dashboard"""
        print(f"Starting GenX_FX Monitoring Dashboard on http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# HTML Template for Dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenX_FX Monitoring Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #0d1117; 
            color: #c9d1d9; 
            line-height: 1.6; 
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            background: linear-gradient(135deg, #1f6feb, #0969da); 
            padding: 30px 0; 
            text-align: center; 
            margin-bottom: 30px; 
            border-radius: 12px;
        }
        .header h1 { color: white; font-size: 2.5em; margin-bottom: 10px; }
        .header p { color: #f0f6fc; opacity: 0.8; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: #161b22; 
            padding: 25px; 
            border-radius: 12px; 
            border: 1px solid #30363d; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .card h3 { color: #58a6ff; margin-bottom: 15px; font-size: 1.3em; }
        
        .status-indicator { 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            margin-right: 8px; 
        }
        .status-running { background: #2ea043; }
        .status-stopped { background: #da3633; }
        .status-warning { background: #fb8500; }
        
        .service-item { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 12px; 
            margin: 8px 0; 
            background: #21262d; 
            border-radius: 8px; 
            border: 1px solid #30363d;
        }
        
        .btn { 
            padding: 8px 16px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 0.9em; 
            margin: 0 4px;
            transition: all 0.2s;
        }
        .btn-primary { background: #238636; color: white; }
        .btn-danger { background: #da3633; color: white; }
        .btn-warning { background: #fb8500; color: white; }
        .btn:hover { opacity: 0.8; transform: translateY(-2px); }
        
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 8px 0; 
            border-bottom: 1px solid #30363d;
        }
        .metric:last-child { border-bottom: none; }
        
        .progress-bar { 
            width: 100%; 
            height: 8px; 
            background: #21262d; 
            border-radius: 4px; 
            overflow: hidden;
            margin-top: 5px;
        }
        .progress-fill { 
            height: 100%; 
            transition: width 0.3s ease;
        }
        .progress-low { background: #2ea043; }
        .progress-medium { background: #fb8500; }
        .progress-high { background: #da3633; }
        
        .logs { 
            background: #0d1117; 
            padding: 15px; 
            border-radius: 8px; 
            font-family: 'Courier New', monospace; 
            font-size: 0.85em; 
            max-height: 300px; 
            overflow-y: auto;
            border: 1px solid #30363d;
        }
        
        .refresh-btn { 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #238636; 
            color: white; 
            border: none; 
            padding: 12px 20px; 
            border-radius: 25px; 
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
        }
        
        .auto-refresh { 
            position: fixed; 
            top: 20px; 
            left: 20px; 
            background: #161b22; 
            padding: 10px 15px; 
            border-radius: 20px; 
            border: 1px solid #30363d;
        }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .loading { animation: pulse 1.5s infinite; }
    </style>
</head>
<body>
    <div class="auto-refresh">
        <label>
            <input type="checkbox" id="autoRefresh" checked> Auto-refresh (30s)
        </label>
    </div>
    
    <button class="refresh-btn" onclick="refreshAll()">🔄 Refresh</button>
    
    <div class="container">
        <div class="header">
            <h1>🚀 GenX_FX Monitoring Dashboard</h1>
            <p>24/7 Service Management & System Monitoring</p>
        </div>
        
        <div class="grid">
            <!-- Services Status -->
            <div class="card">
                <h3>📊 Services Status</h3>
                <div id="services-list">Loading...</div>
            </div>
            
            <!-- System Resources -->
            <div class="card">
                <h3>💻 System Resources</h3>
                <div id="system-metrics">Loading...</div>
            </div>
            
            <!-- Control Panel -->
            <div class="card">
                <h3>🎛️ Control Panel</h3>
                <div style="text-align: center;">
                    <button class="btn btn-primary" onclick="controlService('start')">🟢 Start All</button>
                    <button class="btn btn-warning" onclick="controlService('restart')">🔄 Restart All</button>
                    <button class="btn btn-danger" onclick="controlService('stop')">🛑 Stop All</button>
                </div>
                <div id="control-status" style="margin-top: 15px;"></div>
            </div>
            
            <!-- Recent Logs -->
            <div class="card" style="grid-column: 1 / -1;">
                <h3>📝 Recent Logs</h3>
                <div class="logs" id="logs-display">Loading logs...</div>
            </div>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval;
        
        async function fetchStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateServicesDisplay(data);
            } catch (error) {
                console.error('Error fetching status:', error);
            }
        }
        
        async function fetchSystemInfo() {
            try {
                const response = await fetch('/api/system');
                const data = await response.json();
                updateSystemDisplay(data);
            } catch (error) {
                console.error('Error fetching system info:', error);
            }
        }
        
        async function fetchLogs() {
            try {
                const response = await fetch('/api/logs/all');
                const data = await response.json();
                document.getElementById('logs-display').textContent = data.logs || 'No logs available';
            } catch (error) {
                console.error('Error fetching logs:', error);
            }
        }
        
        function updateServicesDisplay(status) {
            const servicesDiv = document.getElementById('services-list');
            if (!status.services || Object.keys(status.services).length === 0) {
                servicesDiv.innerHTML = '<p>No services running</p>';
                return;
            }
            
            const servicesHtml = Object.entries(status.services).map(([name, service]) => {
                const isRunning = service.running;
                const statusClass = isRunning ? 'status-running' : 'status-stopped';
                const statusText = isRunning ? 'Running' : 'Stopped';
                
                return `
                    <div class="service-item">
                        <div>
                            <span class="status-indicator ${statusClass}"></span>
                            <strong>${name}</strong> - ${statusText}
                            ${isRunning ? `<br><small>PID: ${service.pid} | Restarts: ${service.restart_count || 0}</small>` : ''}
                        </div>
                        <div>
                            <button class="btn btn-primary" onclick="controlService('start', '${name}')">Start</button>
                            <button class="btn btn-danger" onclick="controlService('stop', '${name}')">Stop</button>
                        </div>
                    </div>
                `;
            }).join('');
            
            servicesDiv.innerHTML = servicesHtml;
        }
        
        function updateSystemDisplay(systemInfo) {
            if (!systemInfo) return;
            
            const metricsDiv = document.getElementById('system-metrics');
            const cpu = systemInfo.cpu_percent || 0;
            const memory = systemInfo.memory?.percent || 0;
            const disk = systemInfo.disk?.percent || 0;
            
            const getProgressClass = (value) => {
                if (value < 50) return 'progress-low';
                if (value < 80) return 'progress-medium';
                return 'progress-high';
            };
            
            metricsDiv.innerHTML = `
                <div class="metric">
                    <span>CPU Usage</span>
                    <span>${cpu.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressClass(cpu)}" style="width: ${cpu}%"></div>
                </div>
                
                <div class="metric">
                    <span>Memory Usage</span>
                    <span>${memory.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressClass(memory)}" style="width: ${memory}%"></div>
                </div>
                
                <div class="metric">
                    <span>Disk Usage</span>
                    <span>${disk.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressClass(disk)}" style="width: ${disk}%"></div>
                </div>
                
                ${systemInfo.memory ? `
                <div class="metric">
                    <span>Memory</span>
                    <span>${(systemInfo.memory.used_mb/1024).toFixed(1)}GB / ${(systemInfo.memory.total_mb/1024).toFixed(1)}GB</span>
                </div>` : ''}
            `;
        }
        
        async function controlService(action, serviceName = null) {
            const payload = serviceName ? { service_name: serviceName } : {};
            
            try {
                const response = await fetch(`/api/service/${action}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                const result = await response.json();
                const statusDiv = document.getElementById('control-status');
                
                if (result.success) {
                    statusDiv.innerHTML = `<p style="color: #2ea043;">✅ ${action} command executed successfully</p>`;
                } else {
                    statusDiv.innerHTML = `<p style="color: #da3633;">❌ Error: ${result.error || 'Unknown error'}</p>`;
                }
                
                // Refresh status after action
                setTimeout(refreshAll, 2000);
                
            } catch (error) {
                document.getElementById('control-status').innerHTML = `<p style="color: #da3633;">❌ Network error: ${error.message}</p>`;
            }
        }
        
        function refreshAll() {
            fetchStatus();
            fetchSystemInfo();
            fetchLogs();
        }
        
        function setupAutoRefresh() {
            const checkbox = document.getElementById('autoRefresh');
            
            const startAutoRefresh = () => {
                if (autoRefreshInterval) clearInterval(autoRefreshInterval);
                autoRefreshInterval = setInterval(refreshAll, 30000);
            };
            
            const stopAutoRefresh = () => {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }
            };
            
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    startAutoRefresh();
                } else {
                    stopAutoRefresh();
                }
            });
            
            // Start auto-refresh by default
            if (checkbox.checked) {
                startAutoRefresh();
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            refreshAll();
            setupAutoRefresh();
        });
    </script>
</body>
</html>
'''

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GenX_FX Monitoring Dashboard")
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=9000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    dashboard = MonitoringDashboard()
    dashboard.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()