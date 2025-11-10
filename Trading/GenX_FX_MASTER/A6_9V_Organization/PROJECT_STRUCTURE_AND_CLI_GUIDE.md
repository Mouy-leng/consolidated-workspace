# GenX Trading Platform - Complete Project Structure & CLI Integration Guide

## 🎯 Project Overview

The GenX Trading Platform is a comprehensive trading system that includes multiple components working together to provide a complete trading solution. This guide explains the project structure and how the CLI system integrates all components.

## 📁 Complete Project Structure

```
GenX Trading Platform Root
├── 📦 Core Application
│   ├── client/                    # React frontend application
│   ├── api/                       # Python FastAPI backend
│   ├── services/                  # TypeScript server services
│   └── shared/                    # Shared utilities and types
│
├── 🎯 HistoryMaker-1 Package
│   ├── src/                       # Node.js backend source
│   │   ├── controllers/           # Business logic controllers
│   │   ├── models/               # MongoDB schemas
│   │   ├── routes/               # API endpoints
│   │   ├── utils/                # Utility functions
│   │   └── index.js              # Main server entry
│   ├── package.json              # Package configuration
│   ├── .env.example              # Environment template
│   └── README.md                 # Package documentation
│
├── 🛠️ CLI System
│   ├── genx-cli/                 # Main CLI system
│   │   ├── cli.js                # Main CLI entry point
│   │   ├── historymaker-cli.js   # Dedicated HistoryMaker CLI
│   │   ├── plugins/              # Plugin system
│   │   │   ├── historymaker_plugin.js  # HistoryMaker plugin
│   │   │   ├── amp_adapter.js    # AMP AI Coder adapter
│   │   │   ├── jules_plugin.js   # Jules plugin
│   │   │   ├── codacy_plugin.js  # Codacy integration
│   │   │   ├── license_checker.py # License checking
│   │   │   └── utils/
│   │   │       └── pluginLoader.js # Plugin loader utility
│   │   └── CLI_INTEGRATION.md    # CLI integration documentation
│   └── .julenrc                  # CLI configuration
│
├── 🔧 Trading Components
│   ├── expert-advisors/          # MT4/MT5 Expert Advisors
│   ├── forexconnect_env_37/      # ForexConnect environment
│   ├── ta-lib/                   # Technical analysis library
│   └── signal_output/            # Trading signal outputs
│
├── 🚀 Deployment & Infrastructure
│   ├── deploy/                   # Deployment scripts
│   ├── docker-compose.yml        # Docker configuration
│   ├── aws/                      # AWS deployment resources
│   └── scripts/                  # Utility scripts
│
├── 📊 Data & Testing
│   ├── data/                     # Data files and samples
│   ├── tests/                    # Test files
│   └── logs/                     # Application logs
│
├── 📋 Configuration Files
│   ├── package.json              # Root package configuration
│   ├── setup.py                  # Python package setup
│   ├── requirements.txt          # Python dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── vite.config.ts            # Vite configuration
│   └── tailwind.config.ts        # Tailwind CSS configuration
│
└── 📚 Documentation
    ├── cursor-agent-instructions.md  # Cursor agent setup
    ├── CLI_INTEGRATION.md           # CLI integration guide
    └── PROJECT_STRUCTURE_AND_CLI_GUIDE.md  # This file
```

## 🎮 CLI Integration Architecture

### 1. Main GenX CLI System

The main CLI system (`genx-cli/cli.js`) provides a unified interface for all project components:

```bash
# List all available plugins
genx-cli --list-plugins

# Run specific plugins
genx-cli --run-plugin historymaker_plugin start
genx-cli --run-plugin amp_adapter
genx-cli --run-plugin license_checker.py

# Execute configured commands
genx-cli run test
```

### 2. HistoryMaker-1 Dedicated CLI

A standalone CLI specifically for HistoryMaker-1 operations:

```bash
# Direct access to HistoryMaker CLI
historymaker start
historymaker dev
historymaker history
historymaker export
historymaker health
```

### 3. Plugin System

The plugin system allows modular CLI functionality:

- **historymaker_plugin.js** - Complete HistoryMaker-1 integration
- **amp_adapter.js** - AMP AI Coder integration
- **jules_plugin.js** - Jules functionality
- **codacy_plugin.js** - Code quality integration
- **license_checker.py** - License validation

## 🚀 Getting Started

### 1. Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd GenX_FX

# Install root dependencies
npm install

# Install HistoryMaker-1 dependencies
npm run historymaker:install

# Setup environment
node genx-cli/historymaker-cli.js setup
```

### 2. Start Development Environment

```bash
# Start all services concurrently
npm run dev
```

This starts:
- **Client** (React) on port 5173
- **Server** (TypeScript) on port 3000
- **Python API** on port 8000
- **HistoryMaker-1** on port 3001

### 3. CLI Usage Examples

#### HistoryMaker-1 Operations

```bash
# Start HistoryMaker-1 server
genx-cli --run-plugin historymaker_plugin start
# or
historymaker start

# Get trading history
genx-cli --run-plugin historymaker_plugin history EURUSD
# or
historymaker history

# Export data
genx-cli --run-plugin historymaker_plugin export
# or
historymaker export

# Check health
genx-cli --run-plugin historymaker_plugin health
# or
historymaker health
```

#### Interactive Mode

```bash
# Interactive history query
historymaker history

# Interactive data export
historymaker export
```

## 🔧 Configuration

### Environment Variables

Create `.env` files for each component:

#### Root Environment
```env
NODE_ENV=development
PORT=3000
```

#### HistoryMaker-1 Environment
```env
PORT=3001
MONGODB_URI=mongodb://localhost:27017/historymaker
LOG_LEVEL=info
CORS_ORIGIN=http://localhost:3000
```

### CLI Configuration (.julenrc)

```json
{
  "commands": {
    "test": "PYTHONPATH=. pytest tests/ -v --cov=. --cov-report=xml"
  },
  "plugins": [
    "jules_plugin",
    "codacy_plugin",
    "license_checker.py",
    "amp_adapter",
    "historymaker_plugin"
  ]
}
```

## 📊 HistoryMaker-1 API Endpoints

The HistoryMaker-1 package provides a complete REST API:

### Health & Status
- `GET /health` - Health check

### History Management
- `GET /api/history` - Get trading history
- `GET /api/history/symbol/:symbol` - Get history by symbol
- `GET /api/history/latest` - Get latest entry
- `GET /api/history/stats` - Get statistics

### Data Management
- `GET /api/data/symbols` - Get available symbols
- `GET /api/data/timeframes` - Get available timeframes
- `GET /api/data/summary` - Get data summary
- `POST /api/data/export` - Export data
- `POST /api/data/import` - Import data

## 🔄 Development Workflow

### 1. Development Mode

```bash
# Start all services in development mode
npm run dev
```

### 2. Individual Service Development

```bash
# Start only the client
npm run client

# Start only the server
npm run server

# Start only the Python API
npm run python:dev

# Start only HistoryMaker-1
npm run historymaker
```

### 3. Testing

```bash
# Run all tests
npm test

# Run HistoryMaker-1 tests
npm run historymaker:test
# or
historymaker test
```

### 4. Database Operations

```bash
# Generate database migrations
npm run db:generate

# Run database migrations
npm run db:migrate

# Open database studio
npm run db:studio
```

## 🛠️ CLI Commands Reference

### Main GenX CLI

```bash
genx-cli --help                    # Show help
genx-cli --list-plugins           # List all plugins
genx-cli --run-plugin <name>      # Run specific plugin
genx-cli run <command>            # Run configured command
```

### HistoryMaker CLI

```bash
historymaker help                 # Show help
historymaker start                # Start server
historymaker dev                  # Start in development mode
historymaker install              # Install dependencies
historymaker setup                # Setup environment
historymaker test                 # Run tests
historymaker health               # Check health
historymaker history              # Interactive history query
historymaker symbols              # Get available symbols
historymaker export               # Interactive data export
historymaker backup               # Create data backup
```

### NPM Scripts

```bash
npm run dev                       # Start all services
npm run client                    # Start client only
npm run server                    # Start server only
npm run python:dev               # Start Python API only
npm run historymaker             # Start HistoryMaker-1 only
npm run build                    # Build application
npm run test                     # Run tests
npm run lint                     # Run linting
npm run historymaker:install     # Install HistoryMaker-1 deps
npm run historymaker:start       # Start HistoryMaker-1 service
npm run historymaker:test        # Run HistoryMaker-1 tests
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using a port
   lsof -i :3001
   
   # Kill process using port
   kill -9 <PID>
   ```

2. **Dependencies Issues**
   ```bash
   # Clean install
   rm -rf node_modules package-lock.json
   npm install
   
   # Install HistoryMaker-1 deps
   npm run historymaker:install
   ```

3. **Environment Issues**
   ```bash
   # Setup environment
   historymaker setup
   
   # Check configuration
   historymaker health
   ```

4. **Database Issues**
   ```bash
   # Check MongoDB connection
   mongosh mongodb://localhost:27017/historymaker
   
   # Reset database
   mongosh --eval "use historymaker; db.dropDatabase()"
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
historymaker start

# Check logs
tail -f logs/combined.log
```

## 🚀 Deployment

### Local Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm start
```

### Docker Deployment
```bash
docker-compose up -d
```

### AWS Deployment
```bash
# Use deployment scripts
./deploy/deploy_aws.sh
```

## 📚 Additional Resources

- [HistoryMaker-1 Package Documentation](./historymaker-1/README.md)
- [CLI Integration Guide](./genx-cli/CLI_INTEGRATION.md)
- [Cursor Agent Instructions](./cursor-agent-instructions.md)

## 🤝 Contributing

1. Follow the existing code structure
2. Add comprehensive error handling
3. Include interactive modes for complex operations
4. Update documentation for new features
5. Add tests for new functionality

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review component-specific documentation
3. Check the main project documentation
4. Create an issue in the project repository

---

**🎯 The GenX Trading Platform provides a complete, integrated solution for trading operations with comprehensive CLI management and modular architecture.**