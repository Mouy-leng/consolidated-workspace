# GenX_FX Trading System

A comprehensive AI-powered foreign exchange trading system with advanced market analysis and automated trading capabilities.

## 🚀 Features

- **AI-Powered Analysis**: Advanced machine learning models for market prediction
- **Real-time Data**: Live market data integration from multiple sources
- **Automated Trading**: Intelligent trading algorithms with risk management
- **Multi-Platform Support**: Works with multiple brokers and exchanges
- **Web Interface**: Modern React-based dashboard
- **API Integration**: RESTful API for external integrations

## 📁 Project Structure

```
GenX_FX/
├── src/                    # Source code
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation
├── config/                 # Configuration files
├── scripts/                # Utility scripts
├── assets/                 # Static assets
├── data/                   # Data files and models
├── .vscode/                # VS Code configuration
├── requirements.txt        # Python dependencies
├── GenX_FX.code-workspace # VS Code workspace file
└── README.md              # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- VS Code or Cursor IDE

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd GenX_FX
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   python src/main.py
   ```

## 💻 Development

### VS Code Setup
1. Open the workspace file: `GenX_FX.code-workspace`
2. Install recommended extensions
3. Configure your Python interpreter

### Cursor Setup
1. Open the project folder in Cursor
2. Enable AI features for enhanced development
3. Use the integrated terminal for commands

### Code Formatting
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/
```

## 🧪 Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## 📊 Trading Features

- **Strategy Engine**: Multiple trading strategies
- **Risk Management**: Position sizing and stop-loss management
- **Backtesting**: Historical data analysis
- **Paper Trading**: Risk-free testing environment
- **Live Trading**: Real money trading capabilities

## 🔐 Security

- Encrypted API keys
- Secure authentication
- Rate limiting
- Audit logging

## 📈 Performance

- High-frequency trading support
- Low-latency data processing
- Scalable architecture
- Real-time monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, please contact:
- Email: support@genxfx.com
- Discord: [Join our community]
- Documentation: [docs.genxfx.com]

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves risk and you should never trade with money you cannot afford to lose.