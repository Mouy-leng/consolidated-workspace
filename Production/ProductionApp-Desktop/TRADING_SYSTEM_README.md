# A6-9V Trading System

A comprehensive Java-based trading system that connects to MT4/MT5 and various brokers to execute automated and manual trades with advanced risk management.

## Features

### Core Trading Features
- **Multiple Broker Support**: MT4/MT5, OANDA (easily extensible)
- **Real-time Market Data**: WebSocket connections for live price feeds
- **Order Management**: Place, modify, cancel orders with full lifecycle tracking
- **Position Management**: Track and manage open positions
- **Risk Management**: Advanced risk controls with position sizing, stop losses, and drawdown protection

### Risk Management
- Maximum risk per trade (default: 2%)
- Total portfolio risk limit (default: 10%)
- Maximum drawdown protection (default: 15%)
- Position size constraints
- Emergency stop functionality
- Automated position sizing based on stop loss levels

### System Features
- **Configuration Management**: Flexible HOCON-based configuration
- **Comprehensive Logging**: SLF4J with Logback
- **Asynchronous Operations**: All broker operations are non-blocking
- **Health Monitoring**: System health checks and automatic reconnection
- **Graceful Shutdown**: Proper cleanup of resources and positions

## Project Structure

```
src/main/java/com/a69v/productionapp/trading/
├── TradingSystemManager.java           # Main orchestrator
├── connectors/
│   ├── MetaTraderConnector.java        # MT4/MT5 integration
│   └── OandaConnector.java             # OANDA broker integration
├── interfaces/
│   ├── TradingConnector.java           # Main connector interface
│   ├── MarketDataListener.java         # Market data events
│   └── OrderUpdateListener.java        # Order update events
├── model/
│   ├── Order.java                      # Order data model
│   ├── Position.java                   # Position data model
│   └── Account.java                    # Account data model
├── enums/
│   ├── OrderType.java                  # Order types (MARKET, LIMIT, etc.)
│   ├── OrderSide.java                  # BUY/SELL
│   └── OrderStatus.java                # Order lifecycle statuses
└── services/
    ├── OrderManagementService.java     # Order lifecycle management
    ├── RiskManagementService.java      # Risk controls and validation
    └── ConfigurationService.java       # Configuration management
```

## Setup

### 1. Prerequisites
- Java 17 or higher
- Maven 3.6+
- Access to MT4/MT5 or OANDA account with API credentials

### 2. Environment Configuration
1. Copy `.env.example` to `.env`
2. Update the configuration with your broker credentials:
   ```bash
   # For MetaTrader
   MT_API_KEY=your_actual_api_key
   
   # For OANDA
   OANDA_ACCOUNT_ID=your_account_id
   OANDA_API_KEY=your_api_token
   ```

### 3. Configuration
Edit `src/main/resources/application.conf` to customize:
- Risk management parameters
- Broker settings
- Market data symbols
- System behavior

### 4. Build and Run
```bash
# Build the project
mvn clean compile

# Run the trading system
mvn exec:java
```

## Configuration Options

### Risk Management
```hocon
trading.risk {
  maxRiskPerTrade = 0.02      # 2% per trade
  maxPortfolioRisk = 0.10     # 10% total portfolio risk
  maxDrawdown = 0.15          # 15% maximum drawdown
  maxPositionSize = 0.25      # 25% maximum position size
  maxOpenPositions = 10       # Maximum number of open positions
  minAccountBalance = 1000    # Minimum account balance to trade
}
```

### Broker Configuration
```hocon
trading.brokers {
  metatrader {
    enabled = true
    host = \"localhost\"
    port = 8080
    apiKey = \"${MT_API_KEY}\"
  }
  
  oanda {
    enabled = false
    accountId = \"${OANDA_ACCOUNT_ID}\"
    apiKey = \"${OANDA_API_KEY}\"
    isLive = false  # Set to true for live trading
  }
}
```

## Usage Examples

### Manual Order Placement
```java
// Get reference to trading system
TradingSystemManager tradingSystem = new TradingSystemManager();

// Place a buy order
CompletableFuture<Order> orderFuture = tradingSystem.placeOrder(
    \"EUR/USD\",                    // Symbol
    OrderSide.BUY,                 // Side
    OrderType.MARKET,              // Order type
    new BigDecimal(\"10000\"),       // Quantity (units)
    null                           // Price (null for market orders)
);

// Handle the result
orderFuture.whenComplete((order, throwable) -> {
    if (throwable == null) {
        System.out.println(\"Order placed: \" + order);
    } else {
        System.err.println(\"Failed to place order: \" + throwable.getMessage());
    }
});
```

### Risk Management Integration
The system automatically:
1. Validates orders against risk limits
2. Calculates appropriate position sizes
3. Applies stop losses and take profits
4. Monitors drawdown and triggers emergency stops

### Monitoring and Logging
The system provides comprehensive monitoring:
- Real-time account and position updates
- Risk metric tracking
- System health monitoring
- Automatic reconnection handling

## API Integration

### MetaTrader (MT4/MT5)
Requires a bridge/API server running on the MetaTrader platform. The connector communicates via:
- HTTP REST API for order management
- WebSocket for real-time data feeds

### OANDA
Direct integration with OANDA's REST API:
- Account management
- Order placement and management
- Position tracking
- Historical data access

## Risk Management Details

### Position Sizing
The system calculates position sizes based on:
- Account equity
- Risk per trade percentage
- Stop loss distance
- Maximum position size constraints

### Emergency Stop
Triggered when:
- Maximum drawdown is exceeded
- System detects anomalous behavior
- Manual intervention required

### Monitoring
Continuous monitoring of:
- Account balance and equity
- Open positions and P&L
- Risk exposure by symbol
- System connectivity and health

## Extending the System

### Adding New Brokers
1. Implement the `TradingConnector` interface
2. Add configuration options
3. Register in `TradingSystemManager`

### Custom Risk Rules
Extend `RiskManagementService` to add:
- Custom position sizing algorithms
- Symbol-specific risk limits
- Time-based trading restrictions
- Correlation-based risk management

### Trading Strategies
The system is designed to support automated trading strategies:
1. Implement market data analysis
2. Generate trading signals
3. Execute orders through the risk-managed pipeline

## Logging and Monitoring

### Log Levels
- ERROR: Critical errors and emergency stops
- WARN: Risk warnings and reconnection attempts  
- INFO: Order executions, system status
- DEBUG: Detailed operation traces

### Log Files
- Application logs: `logs/application.log`
- Trading logs: `logs/trading.log`
- Error logs: `logs/error.log`

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Network**: Use HTTPS/WSS for all broker communications
3. **Validation**: All inputs are validated before execution
4. **Limits**: Hard-coded maximum limits prevent runaway trading

## Support and Development

This trading system was developed by A6-9V for professional trading operations. The system includes:

- Comprehensive error handling
- Production-ready logging
- Extensive configuration options
- Professional risk management
- Clean, maintainable code architecture

For support or custom development, contact A6-9V development team.

## Disclaimer

This trading system is for educational and development purposes. Live trading involves substantial risk of loss. Always test thoroughly in a demo environment before using with real money. The developers are not responsible for any trading losses incurred through the use of this system.