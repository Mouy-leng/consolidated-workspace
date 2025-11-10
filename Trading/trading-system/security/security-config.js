// Security Configuration Manager
const credentialManager = require('./credential-manager');
const vpsManager = require('./vps-manager');
const sshManager = require('./ssh-manager');

class SecurityConfig {
    constructor() {
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;

        console.log('🔐 Initializing security system...');
        
        await credentialManager.initialize();
        await vpsManager.initialize();
        await sshManager.initialize();
        
        this.initialized = true;
        console.log('✅ Security system initialized');
    }

    async setupMT5Credentials(credentials) {
        await this.initialize();
        
        const mt5Creds = {
            login: credentials.login,
            password: credentials.password,
            server: credentials.server,
            serverIP: credentials.serverIP,
            company: credentials.company
        };

        await credentialManager.storeCredentials('mt5-fbs', mt5Creds);
        console.log('🔒 MT5 credentials secured');
    }

    async setupVPSCredentials(apiKey) {
        await this.initialize();
        await vpsManager.setCredentials(apiKey);
        console.log('🔒 Vultr credentials secured');
    }

    async createSecureVPS(config = {}) {
        await this.initialize();
        
        const vpsConfig = {
            region: config.region || 'ewr',
            plan: config.plan || 'vc2-1c-1gb',
            label: 'secure-trading-vps',
            hostname: 'trading-server',
            ...config
        };

        const instance = await vpsManager.createVPS(vpsConfig);
        
        // Store VPS info securely
        await credentialManager.storeCredentials(`vps-${instance.id}`, {
            id: instance.id,
            ip: instance.main_ip,
            region: instance.region,
            plan: instance.plan,
            created: new Date().toISOString()
        });

        return instance;
    }

    async setupSSHAccess(servers) {
        await this.initialize();
        
        for (const server of servers) {
            await sshManager.storeServerCredentials(server.name, {
                ip: server.ip,
                username: server.username || 'trading',
                port: server.port || 22
            });
        }

        const configPath = await sshManager.createTermiusConfig(servers);
        console.log(`📋 SSH config created: ${configPath}`);
        
        return configPath;
    }

    async getSecureCredentials(service) {
        await this.initialize();
        return await credentialManager.getCredentials(service);
    }

    async listSecuredServices() {
        await this.initialize();
        return await credentialManager.listServices();
    }

    async testVPSConnection(instanceId) {
        await this.initialize();
        
        const vpsInfo = await credentialManager.getCredentials(`vps-${instanceId}`);
        if (!vpsInfo) {
            throw new Error('VPS not found in secure storage');
        }

        return await sshManager.testConnection({
            ip: vpsInfo.ip,
            username: 'trading'
        });
    }

    async deployTradingSystem(instanceId, localPath) {
        await this.initialize();
        
        const vpsInfo = await credentialManager.getCredentials(`vps-${instanceId}`);
        if (!vpsInfo) {
            throw new Error('VPS not found in secure storage');
        }

        await sshManager.deployToServer({
            ip: vpsInfo.ip,
            username: 'trading'
        }, localPath, '/home/trading/trading-system');

        console.log('🚀 Trading system deployed securely');
    }
}

module.exports = new SecurityConfig();