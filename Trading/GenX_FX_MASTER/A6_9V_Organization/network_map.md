# GenX_FX Network Architecture Map

## Current Working Setup

### 🖥️ **Local System (Windows)**
- **Location**: `d:/Development/GenX_FX/`
- **Main Container**: `genx-fx-working` (Port 8080)
- **Status**: ✅ WORKING

### 🐳 **Docker Containers**
```
genx-fx-working    -> Port 8080 (Trading API)
genxdb_fx_redis    -> Port 6379 (Cache)
genxdb_fx_mysql    -> Port 3306 (Database)
genxdb_fx_monitoring -> Port 3001 (Grafana)
```

### 🌐 **API Endpoints**
- **Health Check**: `http://localhost:8080/health`
- **MT4 Signals**: `http://localhost:8080/MT4_Signals.csv`
- **MT5 Signals**: `http://localhost:8080/MT5_Signals.csv`
- **JSON Signals**: `http://localhost:8080/signals/json`

### 🔗 **External Connections**
- **Brokers**: FXCM (Demo), Exness (Demo), Capital.com
- **AI**: Google Gemini API
- **Data**: Alpha Vantage, NewsAPI, Finnhub
- **Notifications**: Telegram Bot

### 💰 **Cost Optimization**
- ✅ Using Docker Hub free tier
- ✅ Local development (no cloud costs)
- ✅ Demo trading accounts (free)
- ✅ Free API tiers where possible

## Next Steps
1. ✅ Container fixed and running
2. 🔄 Setup CI/CD pipeline
3. 🔄 Migrate to Gemini AI
4. 🔄 Multi-account support