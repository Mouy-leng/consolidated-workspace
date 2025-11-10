// SSH Manager for Termius Integration
const { exec } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const credentialManager = require('./credential-manager');

class SSHManager {
    constructor() {
        this.sshDir = path.join(process.env.USERPROFILE, '.ssh');
        this.keyPath = path.join(this.sshDir, 'trading_rsa');
    }

    async initialize() {
        await credentialManager.initialize();
        await this.ensureSSHDirectory();
        await this.generateSSHKey();
    }

    async ensureSSHDirectory() {
        try {
            await fs.mkdir(this.sshDir, { recursive: true });
        } catch (error) {
            console.error('Failed to create SSH directory:', error);
        }
    }

    async generateSSHKey() {
        try {
            await fs.access(this.keyPath);
            console.log('🔑 SSH key already exists');
        } catch {
            return new Promise((resolve, reject) => {
                exec(`ssh-keygen -t rsa -b 4096 -f "${this.keyPath}" -N "" -C "trading-system"`, (error, stdout, stderr) => {
                    if (error) {
                        console.error('SSH key generation failed:', error);
                        reject(error);
                    } else {
                        console.log('🔑 SSH key generated');
                        resolve();
                    }
                });
            });
        }
    }

    async getPublicKey() {
        try {
            return await fs.readFile(`${this.keyPath}.pub`, 'utf8');
        } catch (error) {
            console.error('Failed to read public key:', error);
            return null;
        }
    }

    async createTermiusConfig(servers) {
        const config = {
            version: "1.0",
            hosts: servers.map(server => ({
                alias: server.name,
                hostname: server.ip,
                port: server.port || 22,
                username: server.username || 'trading',
                keyFile: this.keyPath,
                tags: ['trading', 'vps']
            }))
        };

        const configPath = path.join(this.sshDir, 'termius-config.json');
        await fs.writeFile(configPath, JSON.stringify(config, null, 2));
        console.log('📋 Termius config created');
        return configPath;
    }

    async storeServerCredentials(serverName, credentials) {
        await credentialManager.storeCredentials(`ssh-${serverName}`, credentials);
    }

    async getServerCredentials(serverName) {
        return await credentialManager.getCredentials(`ssh-${serverName}`);
    }

    async testConnection(server) {
        return new Promise((resolve) => {
            const cmd = `ssh -i "${this.keyPath}" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${server.username}@${server.ip} "echo 'Connection successful'"`;
            
            exec(cmd, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Connection failed to ${server.ip}:`, error.message);
                    resolve(false);
                } else {
                    console.log(`✅ Connected to ${server.ip}`);
                    resolve(true);
                }
            });
        });
    }

    async deployToServer(server, localPath, remotePath) {
        return new Promise((resolve, reject) => {
            const cmd = `scp -i "${this.keyPath}" -r "${localPath}" ${server.username}@${server.ip}:${remotePath}`;
            
            exec(cmd, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Deployment failed to ${server.ip}:`, error);
                    reject(error);
                } else {
                    console.log(`📦 Deployed to ${server.ip}:${remotePath}`);
                    resolve();
                }
            });
        });
    }
}

module.exports = new SSHManager();