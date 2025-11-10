// Phone Plugin for Trading System Device Manager
// Detects and manages phone connections for mobile trading

const { exec } = require('child_process');
const util = require('util');
const fs = require('fs').promises;
const path = require('path');

const execPromise = util.promisify(exec);

class PhonePlugin {
    constructor() {
        this.name = 'phone-plugin';
        this.version = '1.0.0';
        this.description = 'Phone device detection and management for mobile trading';
        this.supportedDevices = ['android', 'iphone', 'mobile'];
    }

    async initialize() {
        console.log(`📱 Phone Plugin v${this.version} initialized`);
        return true;
    }

    async discoverDevices() {
        const devices = [];

        try {
            // Check for Android devices via ADB
            const androidDevices = await this.detectAndroidDevices();
            devices.push(...androidDevices);

            // Check for iOS devices (basic detection)
            const iOSDevices = await this.detectiOSDevices();
            devices.push(...iOSDevices);

            // Check for USB connected phones
            const usbPhones = await this.detectUSBPhones();
            devices.push(...usbPhones);

            // Check for network connected phones
            const networkPhones = await this.detectNetworkPhones();
            devices.push(...networkPhones);

        } catch (error) {
            console.error('Phone discovery error:', error.message);
        }

        return devices;
    }

    async detectAndroidDevices() {
        const devices = [];

        try {
            // Check if ADB is available
            const { stdout: adbCheck } = await execPromise('where adb 2>nul || echo "not found"');

            if (adbCheck.includes('not found')) {
                console.log('📱 ADB not found - Android detection limited');
                return devices;
            }

            // List ADB devices
            const { stdout } = await execPromise('adb devices');
            const lines = stdout.split('\n').filter(line => line.trim() && !line.includes('List of devices'));

            for (const line of lines) {
                const [deviceId, status] = line.trim().split('\t');
                if (deviceId && status) {
                    devices.push({
                        id: `android-${deviceId}`,
                        type: 'phone',
                        subtype: 'android',
                        name: `Android Device ${deviceId.substring(0, 8)}`,
                        status: status === 'device' ? 'connected' : 'unauthorized',
                        connectionType: 'usb',
                        capabilities: ['trading-app', 'notifications', 'remote-control'],
                        metadata: {
                            deviceId: deviceId,
                            adbStatus: status,
                            platform: 'android',
                            discoveredAt: new Date().toISOString()
                        }
                    });
                }
            }

        } catch (error) {
            console.log('📱 Android detection failed:', error.message);
        }

        return devices;
    }

    async detectiOSDevices() {
        const devices = [];

        try {
            // Check for iTunes/iOS devices (Windows)
            const { stdout } = await execPromise('wmic path Win32_PnPEntity where "Name like \'%iPhone%\' or Name like \'%iPad%\'" get Name,Status 2>nul || echo "none"');

            if (!stdout.includes('none')) {
                const lines = stdout.split('\n').filter(line => line.trim() && !line.includes('Name'));

                for (const line of lines) {
                    const parts = line.trim().split(/\s+/);
                    if (parts.length >= 2) {
                        const deviceName = parts.slice(0, -1).join(' ');
                        const status = parts[parts.length - 1];

                        devices.push({
                            id: `ios-${Date.now()}`,
                            type: 'phone',
                            subtype: 'ios',
                            name: deviceName,
                            status: status.toLowerCase() === 'ok' ? 'connected' : 'disconnected',
                            connectionType: 'usb',
                            capabilities: ['trading-app', 'notifications'],
                            metadata: {
                                platform: 'ios',
                                systemStatus: status,
                                discoveredAt: new Date().toISOString()
                            }
                        });
                    }
                }
            }

        } catch (error) {
            console.log('📱 iOS detection failed:', error.message);
        }

        return devices;
    }

    async detectUSBPhones() {
        const devices = [];

        try {
            // Check USB storage devices that might be phones
            const { stdout } = await execPromise('wmic logicaldisk where "DriveType=2" get DeviceID,VolumeName,Size 2>nul || echo "none"');

            if (!stdout.includes('none')) {
                const lines = stdout.split('\n').filter(line => line.trim() && !line.includes('DeviceID'));

                for (const line of lines) {
                    const parts = line.trim().split(/\s+/);
                    if (parts.length >= 1) {
                        const deviceId = parts[0];
                        const volumeName = parts[1] || 'Unknown';

                        // Check if it's likely a phone based on volume name or size
                        if (this.isLikelyPhone(volumeName)) {
                            devices.push({
                                id: `usb-phone-${deviceId.replace(':', '')}`,
                                type: 'phone',
                                subtype: 'usb-storage',
                                name: `Phone Storage ${deviceId}`,
                                status: 'connected',
                                connectionType: 'usb-storage',
                                capabilities: ['file-transfer', 'app-install'],
                                metadata: {
                                    driveId: deviceId,
                                    volumeName: volumeName,
                                    discoveredAt: new Date().toISOString()
                                }
                            });
                        }
                    }
                }
            }

        } catch (error) {
            console.log('📱 USB phone detection failed:', error.message);
        }

        return devices;
    }

    async detectNetworkPhones() {
        const devices = [];

        try {
            // Try to detect phones on local network (basic approach)
            // This could be enhanced with specific protocols or apps

            // Check for common mobile trading app ports
            const commonPorts = [8080, 3000, 8000, 9000];
            const localIPs = await this.getLocalNetworkIPs();

            for (const ip of localIPs.slice(0, 10)) { // Limit to first 10 IPs
                for (const port of commonPorts) {
                    try {
                        // Simple connection test (timeout quickly)
                        const testResult = await this.testConnection(ip, port, 1000);
                        if (testResult) {
                            devices.push({
                                id: `network-phone-${ip.replace(/\./g, '-')}-${port}`,
                                type: 'phone',
                                subtype: 'network',
                                name: `Network Device ${ip}:${port}`,
                                status: 'connected',
                                connectionType: 'network',
                                capabilities: ['remote-trading', 'api-access'],
                                metadata: {
                                    ip: ip,
                                    port: port,
                                    discoveredAt: new Date().toISOString()
                                }
                            });
                        }
                    } catch (error) {
                        // Ignore connection failures
                    }
                }
            }

        } catch (error) {
            console.log('📱 Network phone detection failed:', error.message);
        }

        return devices;
    }

    isLikelyPhone(volumeName) {
        const phoneIndicators = [
            'phone', 'android', 'samsung', 'pixel', 'iphone', 'mobile',
            'galaxy', 'xiaomi', 'huawei', 'oneplus', 'lg'
        ];

        const name = volumeName.toLowerCase();
        return phoneIndicators.some(indicator => name.includes(indicator));
    }

    async getLocalNetworkIPs() {
        const ips = [];

        try {
            // Get local network range (simplified)
            const { stdout } = await execPromise('ipconfig | findstr "IPv4"');
            const lines = stdout.split('\n');

            for (const line of lines) {
                const match = line.match(/(\d+\.\d+\.\d+)\.\d+/);
                if (match) {
                    const baseIP = match[1];
                    // Generate common IPs in the range
                    for (let i = 100; i < 110; i++) {
                        ips.push(`${baseIP}.${i}`);
                    }
                }
            }

        } catch (error) {
            console.log('📱 Network IP detection failed:', error.message);
        }

        return ips;
    }

    async testConnection(ip, port, timeout = 1000) {
        return new Promise((resolve) => {
            const net = require('net');
            const socket = new net.Socket();

            const timer = setTimeout(() => {
                socket.destroy();
                resolve(false);
            }, timeout);

            socket.connect(port, ip, () => {
                clearTimeout(timer);
                socket.destroy();
                resolve(true);
            });

            socket.on('error', () => {
                clearTimeout(timer);
                resolve(false);
            });
        });
    }

    async onDeviceConnect(device) {
        console.log(`📱 Phone connected: ${device.name} (${device.subtype})`);

        // Initialize phone-specific services
        if (device.subtype === 'android') {
            await this.setupAndroidTradingEnvironment(device);
        } else if (device.subtype === 'ios') {
            await this.setupiOSTradingEnvironment(device);
        }

        return true;
    }

    async onDeviceDisconnect(device) {
        console.log(`📱 Phone disconnected: ${device.name}`);
        return true;
    }

    async onDeviceSync(device, syncData) {
        console.log(`📱 Syncing phone device: ${device.name}`);

        // Update device status and capabilities
        const updatedData = {
            ...syncData,
            lastSync: new Date().toISOString(),
            batteryLevel: await this.getBatteryLevel(device),
            tradingApps: await this.getTradingApps(device)
        };

        return updatedData;
    }

    async setupAndroidTradingEnvironment(device) {
        try {
            console.log(`📱 Setting up Android trading environment for ${device.id}`);

            // Check for trading apps
            const { stdout } = await execPromise(`adb -s ${device.metadata.deviceId} shell pm list packages | findstr -i "trading\\|forex\\|mt4\\|mt5"`);

            if (stdout.trim()) {
                console.log(`📱 Found trading apps on ${device.name}`);
                device.capabilities.push('trading-apps-installed');
            }

        } catch (error) {
            console.log(`📱 Android setup failed for ${device.id}:`, error.message);
        }
    }

    async setupiOSTradingEnvironment(device) {
        try {
            console.log(`📱 Setting up iOS trading environment for ${device.id}`);
            // iOS setup is more limited due to platform restrictions
            device.capabilities.push('ios-trading-ready');

        } catch (error) {
            console.log(`📱 iOS setup failed for ${device.id}:`, error.message);
        }
    }

    async getBatteryLevel(device) {
        try {
            if (device.subtype === 'android' && device.metadata.deviceId) {
                const { stdout } = await execPromise(`adb -s ${device.metadata.deviceId} shell dumpsys battery | findstr level`);
                const match = stdout.match(/level: (\d+)/);
                return match ? parseInt(match[1]) : null;
            }
        } catch (error) {
            // Battery level not available
        }
        return null;
    }

    async getTradingApps(device) {
        const apps = [];

        try {
            if (device.subtype === 'android' && device.metadata.deviceId) {
                const { stdout } = await execPromise(`adb -s ${device.metadata.deviceId} shell pm list packages | findstr -i "trading\\|forex\\|mt4\\|mt5\\|fbs\\|exness"`);

                const lines = stdout.split('\n').filter(line => line.trim());
                for (const line of lines) {
                    const packageMatch = line.match(/package:(.+)/);
                    if (packageMatch) {
                        apps.push({
                            package: packageMatch[1],
                            type: 'trading-app'
                        });
                    }
                }
            }
        } catch (error) {
            // Apps not available
        }

        return apps;
    }
}

module.exports = new PhonePlugin();