#!/usr/bin/env python3
"""
GenX_FX 24/7 Service Manager
Handles automatic startup, monitoring, and recovery for continuous operation
"""

import os
import sys
import time
import json
import psutil
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
import logging
import traceback
from typing import Dict, List, Optional
import requests
import schedule

class GenXServiceManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.logs_dir = self.project_root / "logs" / "service"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.project_root / "service_config.json"
        self.status_file = self.project_root / "service_status.json"
        self.pid_file = self.project_root / "genx_service.pid"
        
        self.setup_logging()
        self.load_config()
        self.services = {}
        self.monitoring = True
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_file = self.logs_dir / f"genx_service_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('GenXService')
        self.logger.info("GenX 24/7 Service Manager initialized")
    
    def load_config(self):
        """Load or create service configuration"""
        default_config = {
            "services": {
                "main_app": {
                    "command": "python main.py",
                    "working_dir": str(self.project_root),
                    "auto_restart": True,
                    "max_restarts": 10,
                    "restart_delay": 30,
                    "health_check_url": "http://localhost:8000/health",
                    "enabled": True
                },
                "amp_system": {
                    "command": "python amp_cli.py monitor --daemon",
                    "working_dir": str(self.project_root),
                    "auto_restart": True,
                    "max_restarts": 5,
                    "restart_delay": 60,
                    "enabled": True
                },
                "remote_control": {
                    "command": "python remote_control_server.py",
                    "working_dir": str(self.project_root),
                    "auto_restart": True,
                    "max_restarts": 3,
                    "restart_delay": 45,
                    "health_check_url": "http://localhost:8080/status",
                    "enabled": True
                }
            },
            "monitoring": {
                "check_interval": 30,
                "health_check_timeout": 10,
                "memory_threshold": 1000,  # MB
                "cpu_threshold": 80,  # %
                "disk_threshold": 90,  # %
                "log_retention_days": 7
            },
            "notifications": {
                "enabled": True,
                "log_failures": True,
                "email_alerts": False,
                "webhook_url": None
            }
        }
        
        if not self.config_file.exists():
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            self.logger.info("Created default service configuration")
        
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
    
    def save_status(self, status: Dict):
        """Save current service status"""
        status['last_update'] = datetime.now().isoformat()
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def get_status(self) -> Dict:
        """Get current service status"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"services": {}, "system": {}, "last_update": None}
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.config['services']:
            self.logger.error(f"Unknown service: {service_name}")
            return False
        
        service_config = self.config['services'][service_name]
        if not service_config.get('enabled', True):
            self.logger.info(f"Service {service_name} is disabled")
            return False
        
        try:
            # Stop existing process if running
            self.stop_service(service_name)
            
            # Start new process
            working_dir = service_config.get('working_dir', str(self.project_root))
            command = service_config['command'].split()
            
            self.logger.info(f"Starting service {service_name}: {' '.join(command)}")
            
            process = subprocess.Popen(
                command,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.services[service_name] = {
                'process': process,
                'config': service_config,
                'start_time': datetime.now(),
                'restart_count': 0,
                'last_restart': None
            }
            
            self.logger.info(f"Service {service_name} started with PID {process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start service {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.services:
            return True
        
        try:
            service = self.services[service_name]
            process = service['process']
            
            if process.poll() is None:  # Process is still running
                self.logger.info(f"Stopping service {service_name} (PID {process.pid})")
                
                if os.name == 'nt':
                    # Windows
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                                 capture_output=True)
                else:
                    # Unix-like
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
            
            del self.services[service_name]
            self.logger.info(f"Service {service_name} stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop service {service_name}: {e}")
            return False
    
    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        process = service['process']
        
        # Check if process is still running
        if process.poll() is not None:
            self.logger.warning(f"Service {service_name} process has terminated")
            return False
        
        # Check health endpoint if configured
        health_url = service['config'].get('health_check_url')
        if health_url:
            try:
                timeout = self.config['monitoring']['health_check_timeout']
                response = requests.get(health_url, timeout=timeout)
                if response.status_code != 200:
                    self.logger.warning(f"Service {service_name} health check failed: {response.status_code}")
                    return False
            except Exception as e:
                self.logger.warning(f"Service {service_name} health check error: {e}")
                return False
        
        return True
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a service with backoff strategy"""
        if service_name not in self.services:
            return self.start_service(service_name)
        
        service = self.services[service_name]
        service_config = service['config']
        
        # Check restart limits
        max_restarts = service_config.get('max_restarts', 5)
        if service['restart_count'] >= max_restarts:
            self.logger.error(f"Service {service_name} exceeded max restarts ({max_restarts})")
            return False
        
        # Apply restart delay
        if service['last_restart']:
            delay = service_config.get('restart_delay', 30)
            time_since_restart = (datetime.now() - service['last_restart']).seconds
            if time_since_restart < delay:
                self.logger.info(f"Waiting {delay - time_since_restart}s before restarting {service_name}")
                time.sleep(delay - time_since_restart)
        
        self.logger.info(f"Restarting service {service_name}")
        self.stop_service(service_name)
        
        if self.start_service(service_name):
            self.services[service_name]['restart_count'] += 1
            self.services[service_name]['last_restart'] = datetime.now()
            return True
        
        return False
    
    def monitor_system_resources(self) -> Dict:
        """Monitor system resources"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024
            
            # Disk usage
            disk = psutil.disk_usage(str(self.project_root))
            disk_percent = (disk.used / disk.total) * 100
            
            # Network stats (optional)
            network = psutil.net_io_counters()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "memory_percent": memory.percent,
                "disk_percent": disk_percent,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system resources: {e}")
            return {}
    
    def cleanup_logs(self):
        """Clean up old log files"""
        retention_days = self.config['monitoring']['log_retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for log_file in self.logs_dir.glob('*.log'):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file.name}")
            except Exception as e:
                self.logger.error(f"Failed to delete log file {log_file}: {e}")
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting monitoring loop")
        
        while self.monitoring:
            try:
                # Check each service
                for service_name in list(self.services.keys()):
                    if not self.check_service_health(service_name):
                        service = self.services.get(service_name)
                        if service and service['config'].get('auto_restart', True):
                            self.logger.warning(f"Service {service_name} is unhealthy, restarting...")
                            self.restart_service(service_name)
                        else:
                            self.logger.error(f"Service {service_name} is unhealthy and auto-restart is disabled")
                
                # Update status
                status = {
                    "services": {
                        name: {
                            "running": service['process'].poll() is None,
                            "pid": service['process'].pid,
                            "start_time": service['start_time'].isoformat(),
                            "restart_count": service['restart_count']
                        }
                        for name, service in self.services.items()
                    },
                    "system": self.monitor_system_resources()
                }
                
                self.save_status(status)
                
                # Sleep until next check
                time.sleep(self.config['monitoring']['check_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                self.logger.error(traceback.format_exc())
                time.sleep(10)  # Short sleep before retrying
    
    def start_all_services(self):
        """Start all enabled services"""
        self.logger.info("Starting all services...")
        
        for service_name, service_config in self.config['services'].items():
            if service_config.get('enabled', True):
                self.start_service(service_name)
        
        # Schedule periodic tasks
        schedule.every().hour.do(self.cleanup_logs)
        schedule.every(10).minutes.do(lambda: self.save_status(self.get_status()))
    
    def stop_all_services(self):
        """Stop all services"""
        self.logger.info("Stopping all services...")
        self.monitoring = False
        
        for service_name in list(self.services.keys()):
            self.stop_service(service_name)
    
    def run(self):
        """Main run method"""
        try:
            # Write PID file
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            # Start all services
            self.start_all_services()
            
            # Start monitoring in separate thread
            monitor_thread = threading.Thread(target=self.monitoring_loop)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            self.logger.info("GenX 24/7 Service Manager is running")
            
            # Main loop
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.logger.error(traceback.format_exc())
        finally:
            self.stop_all_services()
            if self.pid_file.exists():
                self.pid_file.unlink()
            self.logger.info("GenX 24/7 Service Manager stopped")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GenX_FX 24/7 Service Manager")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'install-service'], 
                       help='Action to perform')
    parser.add_argument('--service', help='Specific service name')
    
    args = parser.parse_args()
    
    service_manager = GenXServiceManager()
    
    if args.action == 'start':
        if args.service:
            service_manager.start_service(args.service)
        else:
            service_manager.run()
    
    elif args.action == 'stop':
        if args.service:
            service_manager.stop_service(args.service)
        else:
            service_manager.stop_all_services()
    
    elif args.action == 'restart':
        if args.service:
            service_manager.restart_service(args.service)
        else:
            service_manager.stop_all_services()
            time.sleep(2)
            service_manager.run()
    
    elif args.action == 'status':
        status = service_manager.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.action == 'install-service':
        # This would install as Windows service (requires additional setup)
        print("Service installation feature coming soon...")

if __name__ == "__main__":
    main()