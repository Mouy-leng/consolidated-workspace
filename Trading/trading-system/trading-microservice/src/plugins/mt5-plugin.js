// MT5 Trading Terminal Plugin
// Manages MetaTrader 5 terminal integration and synchronization

const { exec } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class MT5Plugin {
    constructor() {
        this.name = 'mt5-plugin';
        this.version = '1.0.0';
        this.deviceManager = null;
    }

    async initialize(deviceManager) {
        this.deviceManager = deviceManager;
        console.log(`🔌 MT5 Plugin v${this.version} initialized`);

        // Auto-discover MT5 terminals
        await this.discoverMT5Terminals();

        return true;
    }

    async discoverMT5Terminals() {
        try {
            // Check for running MT5 processes
            return new Promise((resolve) => {
                exec('tasklist /FI "IMAGENAME eq metatrader5.exe" /FO CSV', async (error, stdout) => {
                    if (!error && stdout.includes('metatrader5.exe')) {
                        console.log('📊 MT5 Terminal detected');

                        // Register FBS Live MT5 device
                        await this.deviceManager.registerDevice({
                            type: 'mt5-terminal',
                            name: 'MetaTrader 5 - FBS Live',
                            capabilities: ['trading', 'market-data', 'expert-advisors', 'live-trading'],
                            config: {
                                login: process.env.MT5_LOGIN,
                                server: process.env.MT5_SERVER,
                                account_type: 'live',
                                broker: 'FBS',
                                dataPath: this.getMT5DataPath()
                            },
                            metadata: {
                                accountType: 'LIVE',
                                riskLevel: 'HIGH',
                                maxLotSize: parseFloat(process.env.MAX_POSITION_SIZE) || 0.1,
                                riskPercentage: parseFloat(process.env.RISK_PERCENTAGE) || 0.02
                            }
                        });

                        // Register backup Exness account if needed
                        if (process.env.MT5_BACKUP_LOGIN) {
                            await this.deviceManager.registerDevice({
                                type: 'mt5-terminal-backup',
                                name: 'MetaTrader 5 - Exness Trial (Backup)',
                                capabilities: ['trading', 'market-data', 'expert-advisors', 'demo-trading'],
                                config: {
                                    login: process.env.MT5_BACKUP_LOGIN,
                                    server: process.env.MT5_BACKUP_SERVER,
                                    account_type: 'demo',
                                    broker: 'Exness',
                                    dataPath: this.getMT5DataPath()
                                }
                            });
                        }
                    }
                    resolve();
                });
            });
        } catch (error) {
            console.error('MT5 discovery error:', error);
        }
    }

    async onDeviceSync(device, syncData) {
        if (device.type !== 'mt5-terminal') return;

        console.log(`🔄 Syncing MT5 terminal: ${device.deviceId}`);

        try {
            // Sync MT5 configuration
            const mt5Config = {
                login: device.config.login,
                server: device.config.server,
                expertAdvisors: await this.getExpertAdvisors(),
                symbols: await this.getWatchedSymbols(),
                accountInfo: await this.getAccountInfo()
            };

            // Save to sync data
            syncData.mt5 = mt5Config;

            // Upload to remote server if configured
            if (process.env.SYNC_REMOTE === 'true') {
                await this.uploadToRemote(syncData);
            }

            console.log(`✅ MT5 sync completed for ${device.deviceId}`);

        } catch (error) {
            console.error(`❌ MT5 sync failed for ${device.deviceId}:`, error);
            throw error;
        }
    }

    async getExpertAdvisors() {
        try {
            const mt5DataPath = this.getMT5DataPath();
            const expertsPath = path.join(mt5DataPath, 'MQL5', 'Experts');

            if (await this.fileExists(expertsPath)) {
                const files = await fs.readdir(expertsPath);
                return files.filter(file => file.endsWith('.ex5') || file.endsWith('.mq5'));
            }

            return [];
        } catch (error) {
            console.error('Error getting Expert Advisors:', error);
            return [];
        }
    }

    async getWatchedSymbols() {
        // This would integrate with MT5 API to get current symbols
        // For now, return default symbols
        return ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'];
    }

    async getAccountInfo() {
        const credentialManager = require('../../security/credential-manager');
        
        try {
            // Get FBS credentials from secure storage
            const fbsCreds = await credentialManager.getCredentials('mt5-fbs');
            
            if (fbsCreds) {
                return {
                    balance: 0, // Will be updated from MT5 API
                    equity: 0,
                    margin: 0,
                    freeMargin: 0,
                    login: fbsCreds.login,
                    server: fbsCreds.server,
                    company: fbsCreds.company || 'FBS',
                    serverIP: fbsCreds.serverIP,
                    connected: true
                };
            }
        } catch (error) {
            console.error('Error getting FBS credentials:', error);
        }
        
        // Fallback to environment variables
        return {
            balance: 0,
            equity: 0,
            margin: 0,
            freeMargin: 0,
            login: process.env.FBS_LOGIN || process.env.MT5_LOGIN,
            server: process.env.FBS_SERVER || process.env.MT5_SERVER || 'FBS-Demo',
            company: process.env.FBS_COMPANY || 'FBS',
            serverIP: process.env.FBS_SERVER_IP,
            connected: false
        };
    }

    getMT5DataPath() {
        // Standard MT5 data path on Windows
        const appData = process.env.APPDATA;
        return path.join(appData, 'MetaQuotes', 'Terminal');
    }

    async uploadToRemote(syncData) {
        // This would upload sync data to AWS EC2 or other remote location
        console.log('📤 Uploading MT5 sync data to remote server...');

        // Implementation would depend on your remote sync strategy
        // For example: SCP, SFTP, REST API, etc.
    }

    async fileExists(filePath) {
        try {
            await fs.access(filePath);
            return true;
        } catch {
            return false;
        }
    }
}

module.exports = new MT5Plugin();