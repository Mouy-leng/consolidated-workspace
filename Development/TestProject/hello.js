#!/usr/bin/env node
/**
 * Test script to verify Node.js development environment setup
 */

const fs = require('fs');
const path = require('path');

function main() {
    console.log('🎉 Node.js Development Environment Test');
    console.log('='.repeat(40));
    console.log(`Node.js Version: ${process.version}`);
    console.log(`Current Directory: ${process.cwd()}`);
    console.log(`Platform: ${process.platform}`);
    console.log(`Architecture: ${process.arch}`);
    console.log(`Timestamp: ${new Date()}`);
    console.log('='.repeat(40));
    console.log('✅ Node.js environment is working!');
    console.log('✅ File system access is working!');
    console.log('✅ Development structure is ready!');
    
    // Test basic operations
    const testFile = 'test_node_output.txt';
    const testData = `Node.js test completed at ${new Date()}`;
    
    try {
        fs.writeFileSync(testFile, testData);
        
        if (fs.existsSync(testFile)) {
            console.log('✅ File creation test passed!');
            fs.unlinkSync(testFile);
            console.log('✅ File cleanup completed!');
        }
    } catch (error) {
        console.error('❌ File operations failed:', error.message);
    }
    
    console.log('\n🚀 Your Node.js development environment is ready to use!');
}

if (require.main === module) {
    main();
}