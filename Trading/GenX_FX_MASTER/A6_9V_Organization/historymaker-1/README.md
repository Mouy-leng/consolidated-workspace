# HistoryMaker-1 Package

A comprehensive trading history management package for the GenX Trading Platform.

## Overview

HistoryMaker-1 is a Node.js package designed to manage and process trading history data. It provides a robust API for storing, retrieving, and analyzing historical trading data with support for multiple symbols, timeframes, and data formats.

## Features

- **RESTful API**: Complete REST API for managing trading history
- **Multiple Timeframes**: Support for various trading timeframes (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
- **Data Export/Import**: Export and import data in CSV and JSON formats
- **Advanced Queries**: Filter by symbol, timeframe, date range, and more
- **Statistics**: Built-in statistical analysis and aggregation
- **Data Validation**: Comprehensive data validation and error handling
- **Logging**: Detailed logging with configurable levels
- **Backup/Restore**: Data backup and restore functionality

## Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
```

## Environment Variables

Create a `.env` file with the following variables:

```env
PORT=3001
MONGODB_URI=mongodb://localhost:27017/historymaker
LOG_LEVEL=info
NODE_ENV=development
```

## Usage

### Starting the Server

```bash
# Development mode
npm run dev

# Production mode
npm start
```

### API Endpoints

#### Health Check
```
GET /health
```

#### History Management
```
GET /api/history - Get trading history
GET /api/history/symbol/:symbol - Get history by symbol
GET /api/history/latest - Get latest history entry
GET /api/history/stats - Get history statistics
```

#### Data Management
```
GET /api/data/symbols - Get available symbols
GET /api/data/timeframes - Get available timeframes
GET /api/data/summary - Get data summary
POST /api/data/export - Export data
POST /api/data/import - Import data
```

### Example API Calls

#### Get History for EURUSD
```bash
curl "http://localhost:3001/api/history?symbol=EURUSD&timeframe=1h&limit=100"
```

#### Get Latest Entry
```bash
curl "http://localhost:3001/api/history/latest?symbol=EURUSD"
```

#### Export Data
```bash
curl -X POST "http://localhost:3001/api/data/export" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "EURUSD",
    "timeframe": "1h",
    "startDate": "2024-01-01",
    "endDate": "2024-01-31",
    "format": "csv"
  }'
```

## Data Model

### History Entry Schema

```javascript
{
  symbol: String,        // Trading symbol (e.g., "EURUSD")
  timeframe: String,     // Timeframe (e.g., "1h", "1d")
  timestamp: Date,       // Entry timestamp
  open: Number,          // Opening price
  high: Number,          // Highest price
  low: Number,           // Lowest price
  close: Number,         // Closing price
  volume: Number,        // Trading volume
  createdAt: Date,       // Record creation time
  updatedAt: Date        // Record update time
}
```

## Development

### Project Structure

```
historymaker-1/
├── src/
│   ├── controllers/     # Business logic controllers
│   ├── models/         # Database models
│   ├── routes/         # API routes
│   ├── utils/          # Utility functions
│   └── index.js        # Main application entry
├── tests/              # Test files
├── docs/               # Documentation
├── logs/               # Application logs
├── package.json        # Package configuration
└── README.md          # This file
```

### Running Tests

```bash
npm test
```

### Code Linting

```bash
npm run lint
```

## Database Setup

The package uses MongoDB for data storage. Make sure MongoDB is running and accessible.

### MongoDB Connection

The application automatically connects to MongoDB using the `MONGODB_URI` environment variable.

### Indexes

The following indexes are automatically created for optimal performance:

- Compound index on `(symbol, timeframe, timestamp)`
- Index on `timestamp` for date range queries
- Indexes on `symbol` and `timeframe` for filtering

## Error Handling

The package includes comprehensive error handling:

- Input validation
- Database connection errors
- Query errors
- File operation errors

All errors are logged and returned with appropriate HTTP status codes.

## Logging

Logging is configured with different levels:

- `error`: Error messages
- `warn`: Warning messages
- `info`: Information messages
- `debug`: Debug messages

Logs are written to both console and files in the `logs/` directory.

## Performance Considerations

- Use appropriate indexes for your query patterns
- Implement pagination for large datasets
- Consider data archiving for old records
- Monitor database performance

## Security

- Input validation and sanitization
- CORS configuration
- Environment variable management
- Error message sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support and questions, please contact the GenX Trading Platform team.