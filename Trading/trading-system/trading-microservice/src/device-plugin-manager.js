// Device Plugin Manager for Trading Microservice
// Handles device registration, synchronization, and plugin management

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

class DevicePluginManager {
    constructor(config = {}) {
        this.config = {
            deviceDataPath: config.deviceDataPath || './device-data',
            syncInterval: config.syncInterval || 30000, // 30 seconds
            maxRetries: config.maxRetries || 3,
            ...config
        };

        this.devices = new Map();
        this.plugins = new Map();
        this.syncQueue = [];
        this.isRunning = false;
    }

    async initialize() {
        try {
            // Ensure device data directory exists
            await fs.mkdir(this.config.deviceDataPath, { recursive: true });

            // Load existing devices
            await this.loadDevices();

            // Load plugins
            await this.loadPlugins();

            // Start sync service
            this.startSyncService();

            console.log('✅ Device Plugin Manager initialized');
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize Device Plugin Manager:', error);
            return false;
        }
    }

    async loadDevices() {
        try {
            const devicesFile = path.join(this.config.deviceDataPath, 'devices.json');

            if (await this.fileExists(devicesFile)) {
                const data = await fs.readFile(devicesFile, 'utf8');
                const devices = JSON.parse(data);

                for (const [deviceId, device] of Object.entries(devices)) {
                    this.devices.set(deviceId, {
                        ...device,
                        lastSeen: new Date(device.lastSeen),
                        lastSync: device.lastSync ? new Date(device.lastSync) : null
                    });
                }

                console.log(`📱 Loaded ${this.devices.size} devices`);
            }
        } catch (error) {
            console.error('⚠️ Error loading devices:', error);
        }
    }

    async saveDevices() {
        try {
            const devicesFile = path.join(this.config.deviceDataPath, 'devices.json');
            const devicesObj = {};

            for (const [deviceId, device] of this.devices) {
                devicesObj[deviceId] = {
                    ...device,
                    lastSeen: device.lastSeen.toISOString(),
                    lastSync: device.lastSync ? device.lastSync.toISOString() : null
                };
            }

            await fs.writeFile(devicesFile, JSON.stringify(devicesObj, null, 2));
        } catch (error) {
            console.error('⚠️ Error saving devices:', error);
        }
    }

    async loadPlugins() {
        try {
            const pluginsDir = path.join(__dirname, 'plugins');

            if (await this.fileExists(pluginsDir)) {
                const files = await fs.readdir(pluginsDir);

                for (const file of files) {
                    if (file.endsWith('.js')) {
                        try {
                            const pluginPath = path.join(pluginsDir, file);
                            const plugin = require(pluginPath);

                            if (plugin.name && plugin.initialize) {
                                await plugin.initialize(this);
                                this.plugins.set(plugin.name, plugin);
                                console.log(`🔌 Loaded plugin: ${plugin.name}`);
                            }
                        } catch (error) {
                            console.error(`⚠️ Failed to load plugin ${file}:`, error);
                        }
                    }
                }
            }

            console.log(`🔌 Loaded ${this.plugins.size} plugins`);
        } catch (error) {
            console.error('⚠️ Error loading plugins:', error);
        }
    }

    async registerDevice(deviceInfo) {
        const deviceId = deviceInfo.deviceId || this.generateDeviceId(deviceInfo);

        const device = {
            deviceId,
            type: deviceInfo.type,
            name: deviceInfo.name || `Device ${deviceId}`,
            status: 'registered',
            registeredAt: new Date(),
            lastSeen: new Date(),
            lastSync: null,
            config: deviceInfo.config || {},
            capabilities: deviceInfo.capabilities || [],
            metadata: deviceInfo.metadata || {}
        };

        this.devices.set(deviceId, device);
        await this.saveDevices();

        console.log(`📱 Device registered: ${deviceId} (${device.type})`);

        // Notify plugins
        for (const plugin of this.plugins.values()) {
            if (plugin.onDeviceRegistered) {
                try {
                    await plugin.onDeviceRegistered(device);
                } catch (error) {
                    console.error(`Plugin ${plugin.name} error on device registration:`, error);
                }
            }
        }

        return device;
    }

    async updateDeviceStatus(deviceId, status, metadata = {}) {
        const device = this.devices.get(deviceId);

        if (!device) {
            throw new Error(`Device not found: ${deviceId}`);
        }

        device.status = status;
        device.lastSeen = new Date();
        device.metadata = { ...device.metadata, ...metadata };

        await this.saveDevices();

        // Notify plugins
        for (const plugin of this.plugins.values()) {
            if (plugin.onDeviceStatusChanged) {
                try {
                    await plugin.onDeviceStatusChanged(device, status);
                } catch (error) {
                    console.error(`Plugin ${plugin.name} error on status change:`, error);
                }
            }
        }

        return device;
    }

    async syncDevice(deviceId, force = false) {
        const device = this.devices.get(deviceId);

        if (!device) {
            throw new Error(`Device not found: ${deviceId}`);
        }

        // Check if sync is needed
        if (!force && device.lastSync) {
            const timeSinceLastSync = Date.now() - device.lastSync.getTime();
            if (timeSinceLastSync < this.config.syncInterval) {
                return { success: true, message: 'Sync not needed', device };
            }
        }

        console.log(`🔄 Syncing device: ${deviceId}`);

        try {
            // Update device status
            await this.updateDeviceStatus(deviceId, 'syncing');

            // Create sync data
            const syncData = {
                deviceId,
                timestamp: new Date(),
                config: device.config,
                capabilities: device.capabilities,
                metadata: device.metadata
            };

            // Save sync data locally
            const syncFile = path.join(this.config.deviceDataPath, `${deviceId}-sync.json`);
            await fs.writeFile(syncFile, JSON.stringify(syncData, null, 2));

            // Run plugin sync handlers
            for (const plugin of this.plugins.values()) {
                if (plugin.onDeviceSync) {
                    try {
                        await plugin.onDeviceSync(device, syncData);
                    } catch (error) {
                        console.error(`Plugin ${plugin.name} sync error:`, error);
                    }
                }
            }

            // Update sync status
            device.lastSync = new Date();
            await this.updateDeviceStatus(deviceId, 'online');

            console.log(`✅ Device synced successfully: ${deviceId}`);

            return { success: true, device, syncData };

        } catch (error) {
            console.error(`❌ Device sync failed: ${deviceId}`, error);
            await this.updateDeviceStatus(deviceId, 'error', { syncError: error.message });

            return { success: false, error: error.message, device };
        }
    }

    async syncAllDevices(force = false) {
        console.log('🔄 Starting bulk device sync...');

        const results = [];

        for (const [deviceId, device] of this.devices) {
            if (device.status !== 'disabled') {
                try {
                    const result = await this.syncDevice(deviceId, force);
                    results.push({ deviceId, ...result });
                } catch (error) {
                    results.push({
                        deviceId,
                        success: false,
                        error: error.message
                    });
                }
            }
        }

        console.log(`🏁 Bulk sync completed: ${results.length} devices processed`);
        return results;
    }

    startSyncService() {
        if (this.isRunning) return;

        this.isRunning = true;
        console.log('🚀 Starting device sync service...');

        this.syncInterval = setInterval(async () => {
            try {
                await this.syncAllDevices(false);
            } catch (error) {
                console.error('Sync service error:', error);
            }
        }, this.config.syncInterval);
    }

    stopSyncService() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
        this.isRunning = false;
        console.log('🛑 Device sync service stopped');
    }

    getDevices() {
        return Array.from(this.devices.values());
    }

    getDevice(deviceId) {
        return this.devices.get(deviceId);
    }

    async removeDevice(deviceId) {
        const device = this.devices.get(deviceId);

        if (!device) {
            throw new Error(`Device not found: ${deviceId}`);
        }

        // Notify plugins
        for (const plugin of this.plugins.values()) {
            if (plugin.onDeviceRemoved) {
                try {
                    await plugin.onDeviceRemoved(device);
                } catch (error) {
                    console.error(`Plugin ${plugin.name} error on device removal:`, error);
                }
            }
        }

        this.devices.delete(deviceId);
        await this.saveDevices();

        // Clean up device files
        try {
            const syncFile = path.join(this.config.deviceDataPath, `${deviceId}-sync.json`);
            await fs.unlink(syncFile);
        } catch (error) {
            // File might not exist, ignore
        }

        console.log(`🗑️ Device removed: ${deviceId}`);
        return true;
    }

    generateDeviceId(deviceInfo) {
        const data = `${deviceInfo.type}-${deviceInfo.name}-${Date.now()}`;
        return crypto.createHash('md5').update(data).digest('hex').substring(0, 8);
    }

    async fileExists(filePath) {
        try {
            await fs.access(filePath);
            return true;
        } catch {
            return false;
        }
    }

    // API method for getting sync status
    getSyncStatus() {
        const devices = this.getDevices();
        const totalDevices = devices.length;
        const onlineDevices = devices.filter(d => d.status === 'online').length;
        const syncingDevices = devices.filter(d => d.status === 'syncing').length;
        const errorDevices = devices.filter(d => d.status === 'error').length;

        return {
            totalDevices,
            onlineDevices,
            syncingDevices,
            errorDevices,
            lastSyncService: new Date(),
            isRunning: this.isRunning,
            devices: devices.map(d => ({
                deviceId: d.deviceId,
                type: d.type,
                name: d.name,
                status: d.status,
                lastSync: d.lastSync,
                lastSeen: d.lastSeen
            }))
        };
    }
}

module.exports = DevicePluginManager;