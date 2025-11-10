# GenX FX Remote Control System 🚀

## Overview

The GenX FX Remote Control System provides comprehensive remote access and control capabilities for your GenX FX trading platform. It offers both web-based and command-line interfaces for monitoring, managing, and controlling your trading system from anywhere.

## 🔑 Key Features

### **Remote Control Capabilities**
- ✅ Start/Stop trading systems
- ✅ Restart API servers
- ✅ Monitor system resources (CPU, Memory, Disk)
- ✅ View trading signals in real-time
- ✅ Access system logs
- ✅ Backup trading data
- ✅ Update configuration remotely
- ✅ Control Expert Advisors (MT4/MT5)

### **Multiple Access Methods**
- 🌐 **Web Dashboard**: Full-featured web interface
- 🔌 **WebSocket**: Real-time updates and monitoring
- 🌍 **REST API**: Programmatic access
- 💻 **Command Line**: Terminal-based control

### **Security Features**
- 🔐 API key authentication
- 🔑 Session management
- 🛡️ Secure token generation
- 👥 Role-based access (Admin, Trader, Viewer)

## 📋 System Requirements

- Python 3.7+
- Windows 10/11
- Required packages:
  - `websockets`
  - `psutil`
  - `requests`

## 🚀 Quick Start

### 1. Start the Remote Control Server

```bash
# Simple start
python remote_control_server.py

# Or use the batch file
start_remote_control.bat
```

### 2. Access the Web Dashboard

Open your browser and navigate to:
```
http://localhost:8081/remote/dashboard
```

### 3. Use Command Line Client

```bash
# Get system status
python remote_client.py status

# Monitor real-time
python remote_client.py monitor

# Execute commands
python remote_client.py exec start_trading
```

## 🔧 Configuration

### API Keys
Default API keys (change these in production):
- **Admin**: `genx_admin_2024`
- **Trader**: `genx_trader_2024`
- **Viewer**: `genx_viewer_2024`

### Ports
- **HTTP Server**: 8081
- **WebSocket Server**: 8082

### Environment Variables
```bash
# Set custom secret key
set GENX_REMOTE_SECRET=your-super-secret-key
```

## 🌐 Web Dashboard

The web dashboard provides a comprehensive interface with:

### System Status Panel
- Real-time CPU, Memory usage
- Trading system status
- API server status
- Active process monitoring

### Remote Control Panel
- Start/Stop trading systems
- Restart API servers
- Execute various commands
- Backup operations

### Monitoring Panel
- Live log viewing
- Trading signals display
- System alerts

### Features
- **Auto-refresh**: Updates every 30 seconds
- **WebSocket integration**: Real-time status updates
- **Responsive design**: Works on mobile devices

## 🔌 WebSocket API

Connect to: `ws://localhost:8082`

### Authentication
```javascript
{
  "api_key": "genx_admin_2024"
}
```

### Commands
```javascript
// Get system status
{
  "type": "get_status"
}

// Execute command
{
  "type": "command",
  "command": "start_trading",
  "parameters": {}
}
```

## 🌍 REST API

Base URL: `http://localhost:8081`

### Headers Required
```
X-API-Key: genx_admin_2024
Content-Type: application/json
```

### Endpoints

#### GET `/remote/status`
Get current system status
```json
{
  "cpu_usage": 15.2,
  "memory_usage": 42.1,
  "disk_usage": 65.3,
  "trading_status": "Active",
  "api_status": "Running",
  "timestamp": "2025-10-11T15:30:00"
}
```

#### GET `/remote/logs?lines=50`
Get system logs
```json
{
  "logs": ["[remote_control.log] 2025-10-11 15:30:00 - INFO - Server started"]
}
```

#### GET `/remote/signals`
Get trading signals
```json
{
  "signals": [{
    "timestamp": "2025-10-11T15:30:00",
    "symbol": "XAUUSD",
    "action": "BUY",
    "entry_price": "1950.50",
    "stop_loss": "1945.00",
    "take_profit": "1960.00",
    "confidence": "0.85"
  }]
}
```

#### POST `/remote/command`
Execute remote command
```json
{
  "command": "start_trading",
  "parameters": {}
}
```

## 💻 Command Line Client

### Basic Usage
```bash
python remote_client.py [command] [options]
```

### Available Commands

#### System Status
```bash
python remote_client.py status
```

#### View Logs
```bash
python remote_client.py logs --lines 100
```

#### Get Trading Signals
```bash
python remote_client.py signals
```

#### Execute Commands
```bash
# Start trading
python remote_client.py exec start_trading

# Stop trading
python remote_client.py exec stop_trading

# Restart API
python remote_client.py exec restart_api

# Backup data
python remote_client.py exec backup_data

# With parameters
python remote_client.py exec start_ea --params '{"ea_name": "GenX_Gold_Master_EA"}'
```

#### Real-time Monitoring
```bash
python remote_client.py monitor
```

#### Open Dashboard
```bash
python remote_client.py dashboard
```

### Remote Server Access
```bash
# Connect to remote server
python remote_client.py --server 192.168.1.100 --api-key your-api-key status
```

## 🛠️ Available Remote Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `start_trading` | Start the trading system | None |
| `stop_trading` | Stop all trading processes | None |
| `restart_api` | Restart the API server | None |
| `get_signals` | Retrieve current trading signals | None |
| `get_logs` | Get system logs | `lines` (optional) |
| `system_info` | Get detailed system information | None |
| `start_ea` | Start Expert Advisor | `ea_name` |
| `stop_ea` | Stop Expert Advisor | `ea_name` |
| `backup_data` | Create system backup | None |
| `update_config` | Update configuration | `updates` (JSON) |

## 📱 Mobile Access

The web dashboard is fully responsive and works on mobile devices:

1. Connect to the same network as your trading computer
2. Find your computer's IP address (e.g., 192.168.1.100)
3. Open mobile browser: `http://192.168.1.100:8081/remote/dashboard`

## 🔒 Security Best Practices

### 1. Change Default API Keys
```python
# In remote_control_server.py, update the api_keys dictionary
self.api_keys = {
    'admin': 'your-secure-admin-key-2024',
    'trader': 'your-secure-trader-key-2024',
    'viewer': 'your-secure-viewer-key-2024'
}
```

### 2. Use Environment Variables
```bash
set GENX_REMOTE_SECRET=your-very-long-secret-key
```

### 3. Network Security
- Use VPN for remote access
- Configure firewall rules
- Use HTTPS in production (add SSL certificates)

### 4. Access Control
- Limit API key distribution
- Regular key rotation
- Monitor access logs

## 🔧 Troubleshooting

### Server Won't Start
1. Check if ports 8081/8082 are available
2. Install missing dependencies: `pip install websockets psutil requests`
3. Check firewall settings

### Can't Connect Remotely
1. Verify server is running: `python remote_client.py status`
2. Check network connectivity
3. Verify API key is correct
4. Check firewall/router settings

### WebSocket Connection Issues
1. Ensure WebSocket server is running (port 8082)
2. Check browser console for errors
3. Try different browser

### Commands Not Working
1. Verify API key permissions
2. Check server logs for errors
3. Ensure GenX processes are detectable

## 📊 Monitoring and Logging

### Log Files
- `remote_control.log`: Remote control server logs
- `api-server.log`: API server logs
- `genx_fx.log`: Trading platform logs

### Real-time Monitoring
The system provides real-time monitoring of:
- System resources (CPU, Memory, Disk)
- Network I/O statistics
- Active trading processes
- API server status
- Trading system status

## 🔄 Integration with GenX FX

The remote control system integrates seamlessly with:
- **GenX Trading Engine**: Start/stop trading
- **API Server**: Restart and monitor
- **Signal System**: Real-time signal access
- **Expert Advisors**: MT4/MT5 EA control
- **Logging System**: Centralized log access
- **Configuration**: Remote config updates

## 🚀 Advanced Usage

### Custom Commands
Add your own commands by extending the `RemoteController` class:

```python
async def _custom_command(self, params: Dict[str, Any]) -> str:
    # Your custom logic here
    return "Custom command executed"

# Add to allowed_commands
self.allowed_commands['custom_command'] = self._custom_command
```

### Webhook Integration
Set up webhooks to receive notifications:

```python
# Send alerts to external systems
import requests

def send_alert(message):
    requests.post('https://hooks.slack.com/your-webhook', 
                 json={'text': message})
```

## 📈 Performance Optimization

- System status is cached for 5 seconds to reduce overhead
- WebSocket connections are managed efficiently
- Logs are rotated automatically
- Database queries are optimized

## 🎯 Use Cases

1. **Remote Monitoring**: Monitor your trading system while traveling
2. **Emergency Control**: Quickly stop trading during market events
3. **System Administration**: Restart services without physical access
4. **Performance Monitoring**: Track system resources and performance
5. **Signal Analysis**: Review trading signals remotely
6. **Automated Management**: Integration with other systems via API

---

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review log files for error details
- Test with command line client first
- Verify network connectivity and permissions

**Happy Trading! 📈🚀**