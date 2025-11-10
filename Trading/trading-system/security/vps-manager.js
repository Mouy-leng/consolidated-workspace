// VPS Manager for Vultr Integration
const axios = require('axios');
const credentialManager = require('./credential-manager');

class VPSManager {
    constructor() {
        this.vultrAPI = 'https://api.vultr.com/v2';
        this.apiKey = null;
    }

    async initialize() {
        await credentialManager.initialize();
        const creds = await credentialManager.getCredentials('vultr');
        this.apiKey = creds?.apiKey;
    }

    async setCredentials(apiKey) {
        await credentialManager.storeCredentials('vultr', { apiKey });
        this.apiKey = apiKey;
    }

    getHeaders() {
        return {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async createVPS(config) {
        const payload = {
            region: config.region || 'ewr',
            plan: config.plan || 'vc2-1c-1gb',
            os_id: config.osId || 387, // Ubuntu 20.04
            label: config.label || 'trading-vps',
            hostname: config.hostname || 'trading-server',
            enable_ipv6: false,
            backups: 'enabled',
            ddos_protection: true,
            user_data: this.getUserData()
        };

        try {
            const response = await axios.post(`${this.vultrAPI}/instances`, payload, {
                headers: this.getHeaders()
            });
            
            console.log('🚀 VPS created:', response.data.instance.id);
            return response.data.instance;
        } catch (error) {
            console.error('VPS creation failed:', error.response?.data || error.message);
            throw error;
        }
    }

    async listVPS() {
        try {
            const response = await axios.get(`${this.vultrAPI}/instances`, {
                headers: this.getHeaders()
            });
            return response.data.instances;
        } catch (error) {
            console.error('Failed to list VPS:', error.response?.data || error.message);
            return [];
        }
    }

    async getVPSInfo(instanceId) {
        try {
            const response = await axios.get(`${this.vultrAPI}/instances/${instanceId}`, {
                headers: this.getHeaders()
            });
            return response.data.instance;
        } catch (error) {
            console.error('Failed to get VPS info:', error.response?.data || error.message);
            return null;
        }
    }

    getUserData() {
        return Buffer.from(`#!/bin/bash
# Trading VPS Setup Script
apt-get update
apt-get install -y nodejs npm docker.io ufw fail2ban

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 3000
ufw --force enable

# Configure fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Create trading user
useradd -m -s /bin/bash trading
usermod -aG docker trading

echo "VPS setup completed" > /var/log/trading-setup.log
`).toString('base64');
    }
}

module.exports = new VPSManager();