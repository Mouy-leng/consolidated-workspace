const express = require('express');
const database = require('../../config/database');
const router = express.Router();

// Basic health check
router.get('/', async (req, res) => {
  try {
    const dbStatus = database.getConnectionStatus();
    const healthCheck = {
      status: 'UP',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: '1.0.0',
      database: {
        status: dbStatus.isConnected ? 'UP' : 'DOWN',
        readyState: dbStatus.readyState
      },
      memory: process.memoryUsage(),
      pid: process.pid
    };

    res.status(200).json(healthCheck);
  } catch (error) {
    res.status(503).json({
      status: 'DOWN',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// Detailed health check
router.get('/detailed', async (req, res) => {
  try {
    const dbStatus = database.getConnectionStatus();
    
    const detailedHealth = {
      status: 'UP',
      timestamp: new Date().toISOString(),
      uptime: Math.floor(process.uptime()),
      environment: process.env.NODE_ENV || 'development',
      version: '1.0.0',
      node_version: process.version,
      platform: process.platform,
      arch: process.arch,
      database: {
        status: dbStatus.isConnected ? 'UP' : 'DOWN',
        readyState: dbStatus.readyState,
        host: dbStatus.host,
        port: dbStatus.port,
        name: dbStatus.name
      },
      memory: {
        ...process.memoryUsage(),
        free: process.memoryUsage().heapTotal - process.memoryUsage().heapUsed,
        unit: 'bytes'
      },
      cpu: process.cpuUsage(),
      pid: process.pid,
      ppid: process.ppid
    };

    res.status(200).json(detailedHealth);
  } catch (error) {
    res.status(503).json({
      status: 'DOWN',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

module.exports = router;