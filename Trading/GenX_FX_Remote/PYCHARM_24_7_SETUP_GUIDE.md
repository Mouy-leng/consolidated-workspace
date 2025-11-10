# PyCharm 24/7 Setup Guide for GenX_FX

## 🚀 Complete Setup for 24/7 Operation

Your GenX_FX project is now fully configured for 24/7 operation with PyCharm integration. This guide shows you how to set everything up.

## 📋 Quick Setup Steps

### 1. Install Windows Service (Run as Administrator)
```bash
# Right-click and "Run as Administrator"
setup_windows_service.bat
```

### 2. Open PyCharm with Project
```bash
# Double-click the desktop shortcut or run:
"Start GenX in PyCharm.bat"
```

### 3. Access Monitoring Dashboard
```
http://localhost:9000
```

## 🎯 PyCharm Configuration

### Project Structure
```
GenX_FX_Remote/
├── .idea/                     # PyCharm project files
│   ├── runConfigurations/     # Pre-configured run settings
│   ├── vcs.xml               # Git integration
│   ├── workspace.xml         # Workspace settings
│   └── modules.xml           # Module configuration
├── genx_24_7_service.py      # Main 24/7 service manager
├── monitoring_dashboard.py   # Web monitoring dashboard
├── start_genx_24_7.bat      # Windows startup script
└── service_config.json       # Service configuration
```

### Run Configurations in PyCharm

#### 1. GenX 24/7 Service
- **Name**: GenX 24/7 Service
- **Script**: `genx_24_7_service.py`
- **Parameters**: `start`
- **Purpose**: Starts the main service manager

#### 2. Monitoring Dashboard
- **Name**: Monitoring Dashboard  
- **Script**: `monitoring_dashboard.py`
- **Parameters**: `--host 0.0.0.0 --port 9000`
- **Purpose**: Web-based monitoring interface

### How to Use in PyCharm

1. **Open Project**: File → Open → Select `C:\Users\lengk\GenX_FX_Remote`

2. **Configure Python Interpreter**:
   - File → Settings → Project → Python Interpreter
   - Add interpreter if not detected automatically

3. **Run Services**:
   - Use the run configurations in the toolbar
   - Or press Shift+F10 to run the current file

4. **Debug Services**:
   - Set breakpoints in your code
   - Click the debug button (Shift+F9)

## ⚙️ Service Management

### Windows Task Scheduler Integration

The service is installed as a Windows scheduled task with these triggers:
- **Boot Trigger**: Starts 2 minutes after system boot
- **Login Trigger**: Starts 1 minute after user login
- **Auto-restart**: Restarts failed services automatically

### Manual Service Control

```bash
# Start all services
python genx_24_7_service.py start

# Stop all services  
python genx_24_7_service.py stop

# Restart all services
python genx_24_7_service.py restart

# Check status
python genx_24_7_service.py status

# Start specific service
python genx_24_7_service.py start --service main_app
```

### Task Scheduler Commands
```bash
# Check task status
schtasks /query /tn "GenX_FX_Service"

# Start task manually
schtasks /run /tn "GenX_FX_Service"

# Stop running task
schtasks /end /tn "GenX_FX_Service"

# Delete the task
schtasks /delete /tn "GenX_FX_Service" /f
```

## 📊 Monitoring & Management

### Web Dashboard (Recommended)
- **URL**: http://localhost:9000
- **Features**:
  - Real-time service status
  - System resource monitoring
  - Service control (start/stop/restart)
  - Live log viewing
  - Auto-refresh every 30 seconds

### Desktop Shortcuts Created
- **GenX Control Panel.bat**: Opens monitoring dashboard
- **GenX Status.bat**: Quick command-line status check
- **Start GenX in PyCharm.bat**: Opens PyCharm with project

## 🔧 Configuration Files

### Service Configuration (`service_config.json`)
```json
{
  "services": {
    "main_app": {
      "command": "python main.py",
      "auto_restart": true,
      "max_restarts": 10,
      "restart_delay": 30,
      "health_check_url": "http://localhost:8000/health",
      "enabled": true
    }
  },
  "monitoring": {
    "check_interval": 30,
    "health_check_timeout": 10,
    "memory_threshold": 1000,
    "cpu_threshold": 80,
    "log_retention_days": 7
  }
}
```

### Customizing Services
Edit `service_config.json` to:
- Add new services
- Change restart policies
- Modify health check URLs
- Adjust monitoring thresholds

## 📝 Logging

### Log Locations
- **Service Logs**: `logs/service/genx_service_YYYYMMDD.log`
- **Application Logs**: Individual service logs in respective directories

### Log Management
- Automatic rotation daily
- 7-day retention by default
- Configurable in `service_config.json`

## 🛡️ Automatic Recovery Features

### Service-Level Recovery
- **Auto-restart**: Failed services restart automatically
- **Backoff Strategy**: Exponential delay between restart attempts
- **Restart Limits**: Prevents infinite restart loops
- **Health Checks**: HTTP endpoint monitoring for web services

### System-Level Recovery
- **Task Scheduler**: Windows restarts the entire service manager if needed
- **Resource Monitoring**: CPU, memory, and disk usage tracking
- **Alert Thresholds**: Configurable resource usage alerts

### Failure Scenarios Handled
1. **Process Crash**: Automatic service restart
2. **High Resource Usage**: Monitoring and alerts
3. **Network Issues**: HTTP health check failures
4. **System Reboot**: Automatic startup via Task Scheduler
5. **User Logout**: Service continues running

## 🔍 Troubleshooting

### Common Issues

#### Service Won't Start
1. Check Python is in PATH: `python --version`
2. Verify working directory: Should be project root
3. Check log files in `logs/service/`
4. Ensure required packages installed: `pip install -r requirements.txt`

#### Task Scheduler Issues
1. Run setup as Administrator
2. Check XML file syntax in `genx_scheduler_task.xml`
3. Verify user permissions in Task Scheduler

#### PyCharm Integration Issues
1. Ensure project opened from correct directory
2. Configure Python interpreter in settings
3. Check run configurations are loaded correctly

### Debug Mode
```bash
# Run service in debug mode (non-daemon)
python genx_24_7_service.py start --debug

# Run monitoring dashboard in debug mode
python monitoring_dashboard.py --debug
```

## 📈 Performance Optimization

### Resource Usage
- **Memory**: Typical usage 100-500MB per service
- **CPU**: Background monitoring ~1-2% CPU usage
- **Disk**: Log files, configurable retention

### Scaling
- Add more services in `service_config.json`
- Adjust monitoring intervals for performance
- Use health checks for critical services only

## 🔐 Security Considerations

### Firewall Rules
The setup automatically creates Windows Firewall rules for:
- Port 9000: Monitoring dashboard
- Port 8000: Main application API

### Access Control
- Dashboard accessible on localhost by default
- Change host to `0.0.0.0` for network access (less secure)
- Consider VPN or authentication for remote access

## 🎉 You're All Set!

Your GenX_FX system is now configured for:
- ✅ **24/7 Operation**: Automatic startup and monitoring
- ✅ **PyCharm Integration**: Full IDE support with run configurations
- ✅ **Web Monitoring**: Real-time dashboard at http://localhost:9000
- ✅ **Automatic Recovery**: Service restarts and failure handling
- ✅ **Windows Service**: Integrated with Task Scheduler
- ✅ **Easy Management**: Desktop shortcuts and command-line tools

## 🎯 Next Steps

1. **Test the Setup**: Restart your computer and verify services start automatically
2. **Customize Configuration**: Edit `service_config.json` for your specific needs
3. **Monitor Performance**: Use the dashboard to track resource usage
4. **Add Your Services**: Configure additional services in the config file
5. **Set Up Alerts**: Configure email/webhook notifications if needed

---

**🚀 Your GenX_FX system is now running 24/7 with full PyCharm integration!**

Access your monitoring dashboard: **http://localhost:9000**