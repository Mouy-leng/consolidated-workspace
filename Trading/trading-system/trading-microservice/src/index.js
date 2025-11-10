const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const morgan = require('morgan');
const config = require('../config/config');
const DevicePluginManager = require('./device-plugin-manager');

const app = express();

// Initialize Device Plugin Manager
const deviceManager = new DevicePluginManager({
  deviceDataPath: './device-data',
  syncInterval: 30000 // 30 seconds
});

// Initialize device manager on startup
deviceManager.initialize().then(() => {
  console.log('📱 Device Plugin Manager ready');
}).catch(error => {
  console.error('❌ Device Plugin Manager initialization failed:', error);
});

// Security middleware
app.use(helmet());
app.use(cors());

// Logging
app.use(morgan('combined'));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    service: 'trading-microservice',
    version: '1.0.0'
  });
});

// Readiness check
app.get('/ready', (req, res) => {
  // Add database/dependency checks here
  res.status(200).json({
    status: 'ready',
    timestamp: new Date().toISOString()
  });
});

// API routes
app.get('/api/v1/status', (req, res) => {
  res.json({
    message: 'Trading Microservice API v1',
    timestamp: new Date().toISOString()
  });
});

// Example trading endpoint
app.get('/api/v1/trades', (req, res) => {
  // TODO: Implement actual trading logic
  res.json({
    trades: [],
    total: 0,
    page: 1
  });
});

// Device management endpoints
app.get('/api/v1/devices', (req, res) => {
  try {
    const devices = deviceManager.getDevices();
    res.json({
      success: true,
      devices,
      total: devices.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/v1/devices/sync-status', (req, res) => {
  try {
    const syncStatus = deviceManager.getSyncStatus();
    res.json({
      success: true,
      ...syncStatus
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/api/v1/devices/register', async (req, res) => {
  try {
    const device = await deviceManager.registerDevice(req.body);
    res.status(201).json({
      success: true,
      device
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/api/v1/devices/:deviceId/sync', async (req, res) => {
  try {
    const { deviceId } = req.params;
    const { force = false } = req.body;

    const result = await deviceManager.syncDevice(deviceId, force);

    res.json({
      success: result.success,
      message: result.message || (result.success ? 'Sync completed' : 'Sync failed'),
      device: result.device,
      syncData: result.syncData,
      error: result.error
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/api/v1/devices/sync-all', async (req, res) => {
  try {
    const { force = false } = req.body;
    const results = await deviceManager.syncAllDevices(force);

    const successCount = results.filter(r => r.success).length;
    const totalCount = results.length;

    res.json({
      success: true,
      message: `Synced ${successCount}/${totalCount} devices`,
      results,
      summary: {
        total: totalCount,
        successful: successCount,
        failed: totalCount - successCount
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.delete('/api/v1/devices/:deviceId', async (req, res) => {
  try {
    const { deviceId } = req.params;
    await deviceManager.removeDevice(deviceId);

    res.json({
      success: true,
      message: `Device ${deviceId} removed successfully`
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message
    });
  }
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    path: req.path
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// Graceful shutdown
const server = app.listen(config.port, () => {
  console.log(`Trading microservice listening on port ${config.port}`);
  console.log(`Environment: ${config.env}`);
});

process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  deviceManager.stopSyncService();
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT signal received: closing HTTP server');
  deviceManager.stopSyncService();
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});

module.exports = app;
