// Secure Credential Manager for Trading System
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

class CredentialManager {
    constructor() {
        this.algorithm = 'aes-256-gcm';
        this.keyPath = path.join(process.env.APPDATA, '.trading-keys');
        this.credentialsPath = path.join(process.env.APPDATA, '.trading-creds');
    }

    async initialize() {
        await this.ensureDirectories();
        await this.generateMasterKey();
    }

    async ensureDirectories() {
        try {
            await fs.mkdir(this.keyPath, { recursive: true });
            await fs.mkdir(this.credentialsPath, { recursive: true });
        } catch (error) {
            console.error('Failed to create security directories:', error);
        }
    }

    async generateMasterKey() {
        const keyFile = path.join(this.keyPath, 'master.key');
        try {
            await fs.access(keyFile);
        } catch {
            const key = crypto.randomBytes(32);
            await fs.writeFile(keyFile, key);
            console.log('🔐 Master key generated');
        }
    }

    async getMasterKey() {
        const keyFile = path.join(this.keyPath, 'master.key');
        return await fs.readFile(keyFile);
    }

    async encrypt(data) {
        const key = await this.getMasterKey();
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipher(this.algorithm, key);
        cipher.setAAD(Buffer.from('trading-system'));
        
        let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
        encrypted += cipher.final('hex');
        
        const authTag = cipher.getAuthTag();
        
        return {
            encrypted,
            iv: iv.toString('hex'),
            authTag: authTag.toString('hex')
        };
    }

    async decrypt(encryptedData) {
        const key = await this.getMasterKey();
        const decipher = crypto.createDecipher(this.algorithm, key);
        decipher.setAAD(Buffer.from('trading-system'));
        decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
        
        let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
        decrypted += decipher.final('utf8');
        
        return JSON.parse(decrypted);
    }

    async storeCredentials(service, credentials) {
        const encrypted = await this.encrypt(credentials);
        const credFile = path.join(this.credentialsPath, `${service}.cred`);
        await fs.writeFile(credFile, JSON.stringify(encrypted));
        console.log(`🔒 Credentials stored for ${service}`);
    }

    async getCredentials(service) {
        try {
            const credFile = path.join(this.credentialsPath, `${service}.cred`);
            const encryptedData = JSON.parse(await fs.readFile(credFile, 'utf8'));
            return await this.decrypt(encryptedData);
        } catch (error) {
            console.error(`Failed to retrieve credentials for ${service}:`, error);
            return null;
        }
    }

    async listServices() {
        try {
            const files = await fs.readdir(this.credentialsPath);
            return files.filter(f => f.endsWith('.cred')).map(f => f.replace('.cred', ''));
        } catch {
            return [];
        }
    }
}

module.exports = new CredentialManager();