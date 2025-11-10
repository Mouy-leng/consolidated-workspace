#!/usr/bin/env node
// Security Setup Script for Trading System

const readline = require('readline');
const securityConfig = require('./security/security-config');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function question(prompt) {
    return new Promise(resolve => rl.question(prompt, resolve));
}

async function setupSecurity() {
    console.log('🔐 Trading System Security Setup');
    console.log('================================\n');

    try {
        // Initialize security system
        await securityConfig.initialize();

        // Setup MT5 credentials
        console.log('📊 MT5 Broker Credentials Setup');
        const mt5Login = await question('MT5 Login: ');
        const mt5Password = await question('MT5 Password: ');
        const mt5Server = await question('MT5 Server: ');
        const mt5ServerIP = await question('MT5 Server IP (optional): ');
        const mt5Company = await question('MT5 Company: ');

        await securityConfig.setupMT5Credentials({
            login: mt5Login,
            password: mt5Password,
            server: mt5Server,
            serverIP: mt5ServerIP,
            company: mt5Company
        });

        // Setup Vultr VPS
        console.log('\n🌐 Vultr VPS Setup');
        const vultrApiKey = await question('Vultr API Key: ');
        await securityConfig.setupVPSCredentials(vultrApiKey);

        const createVPS = await question('Create new VPS? (y/n): ');
        if (createVPS.toLowerCase() === 'y') {
            const region = await question('Region (default: ewr): ') || 'ewr';
            const plan = await question('Plan (default: vc2-1c-1gb): ') || 'vc2-1c-1gb';

            console.log('🚀 Creating VPS...');
            const instance = await securityConfig.createSecureVPS({ region, plan });
            console.log(`✅ VPS Created: ${instance.id} (${instance.main_ip})`);

            // Setup SSH access
            console.log('\n🔑 Setting up SSH access...');
            await securityConfig.setupSSHAccess([{
                name: 'trading-vps',
                ip: instance.main_ip,
                username: 'trading'
            }]);

            console.log('\n⏳ Waiting for VPS to boot (60 seconds)...');
            await new Promise(resolve => setTimeout(resolve, 60000));

            console.log('🔍 Testing connection...');
            const connected = await securityConfig.testVPSConnection(instance.id);
            if (connected) {
                console.log('✅ SSH connection successful');
            } else {
                console.log('⚠️  SSH connection failed - VPS may still be booting');
            }
        }

        console.log('\n📋 Security Setup Summary:');
        const services = await securityConfig.listSecuredServices();
        services.forEach(service => console.log(`  ✓ ${service}`));

        console.log('\n🎉 Security setup completed!');
        console.log('\nNext steps:');
        console.log('1. Import SSH config into Termius');
        console.log('2. Test VPS connection');
        console.log('3. Deploy trading system');

    } catch (error) {
        console.error('❌ Setup failed:', error.message);
    } finally {
        rl.close();
    }
}

if (require.main === module) {
    setupSecurity();
}

module.exports = { setupSecurity };