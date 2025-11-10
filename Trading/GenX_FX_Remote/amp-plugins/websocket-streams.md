# AMP Plugin: Multi-Exchange WebSocket Streams

## Description
Real-time WebSocket connections to multiple cryptocurrency exchanges for live market data.

## Command

```bash
amp plugin install websocket-streams \
  --source genx-trading \
  --add-dependency websockets>=11.0 \
  --add-dependency aiohttp>=3.9.0 \
  --add-env ENABLE_WEBSOCKET_FEED=true \
  --add-env WEBSOCKET_RECONNECT_INTERVAL=5 \
  --add-env MAX_WEBSOCKET_RETRIES=10 \
  --enable-service websocket_service \
  --description "Multi-exchange WebSocket streams for real-time data"
```

## Features
- Multi-exchange support (Bybit, Binance, Coinbase)
- Real-time trade data streaming
- Automatic reconnection with retry logic
- Configurable subscription management
- Data normalization across exchanges
- Callback system for data processing
- Connection health monitoring

## Supported Exchanges
- **Bybit**: Spot and derivatives markets
- **Binance**: Comprehensive crypto markets
- **Coinbase**: Professional crypto trading
- **Extensible**: Easy to add new exchanges

## Configuration
```bash
export ENABLE_WEBSOCKET_FEED=true
export WEBSOCKET_RECONNECT_INTERVAL=5
export MAX_WEBSOCKET_RETRIES=10
```

## Usage
```python
from api.services.websocket_service import WebSocketService

# Initialize service
ws_service = WebSocketService()
await ws_service.initialize()

# Subscribe to symbols
await ws_service.subscribe_to_symbol("bybit", "BTCUSDT")
await ws_service.subscribe_to_symbol("binance", "ETHUSDT")

# Add data callback
async def process_market_data(data):
    print(f"New data: {data.symbol} - {data.price}")

ws_service.add_data_callback(process_market_data)

# Check connection status
status = await ws_service.get_connection_status()
```

## Real-time Data Structure
```python
@dataclass
class MarketData:
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    bid: float = None
    ask: float = None
    high_24h: float = None
    low_24h: float = None
    change_24h: float = None
```

## API Endpoints
- `GET /api/v1/websocket/status` - Get connection status
- `POST /api/v1/websocket/subscribe` - Subscribe to symbol
- `DELETE /api/v1/websocket/unsubscribe` - Unsubscribe from symbol
- `GET /api/v1/websocket/subscriptions` - List active subscriptions

## Advanced Features
- **Auto-reconnection**: Automatic reconnection with exponential backoff
- **Data validation**: Real-time data validation and filtering
- **Rate limiting**: Built-in rate limiting per exchange
- **Error handling**: Comprehensive error handling and logging
- **Metrics**: Connection and data flow metrics

## Dependencies
- websockets>=11.0
- aiohttp>=3.9.0
- asyncio
- json
- datetime
