const mongoose = require('mongoose');
const config = require('./config');

class Database {
  constructor() {
    this.isConnected = false;
  }

  async connect() {
    try {
      if (this.isConnected) {
        console.log('Database already connected');
        return;
      }

      try {
        await mongoose.connect(config.mongodb.uri, config.mongodb.options);
        this.isConnected = true;
        console.log('✅ MongoDB connected successfully');
      } catch (dbError) {
        console.warn('⚠️  MongoDB not available, running in no-database mode');
        console.warn('   Start MongoDB to enable full functionality');
        this.isConnected = false;
        return; // Don't throw, just continue without DB
      }
      
      // Handle connection events - use 'once' to prevent duplicate listeners
      mongoose.connection.once('error', (err) => {
        console.error('❌ MongoDB connection error:', err);
        this.isConnected = false;
      });

      mongoose.connection.once('disconnected', () => {
        console.log('⚠️  MongoDB disconnected');
        this.isConnected = false;
      });

      // Graceful shutdown - use 'once' to prevent duplicate listeners
      process.once('SIGINT', async () => {
        await this.disconnect();
        process.exit(0);
      });

    } catch (error) {
      console.error('❌ Database connection failed:', error);
      this.isConnected = false;
      throw error;
    }
  }

  async disconnect() {
    try {
      if (!this.isConnected) {
        console.log('Database not connected');
        return;
      }

      await mongoose.connection.close();
      this.isConnected = false;
      console.log('🔌 MongoDB disconnected gracefully');
    } catch (error) {
      console.error('❌ Error disconnecting from database:', error);
      throw error;
    }
  }

  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      readyState: mongoose.connection.readyState,
      host: mongoose.connection.host,
      port: mongoose.connection.port,
      name: mongoose.connection.name
    };
  }
}

module.exports = new Database();