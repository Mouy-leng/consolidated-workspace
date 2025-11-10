from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from datetime import datetime, timedelta
from api.services.ml_service import MLService
from api.routers import communication

app = FastAPI(
    title="GenX-FX Trading Platform API",
    description="Trading platform with ML-powered predictions and multi-agent communication",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include the communication router
app.include_router(communication.router, prefix="/communication", tags=["communication"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.get("/")
async def root():
    return {
        "message": "GenX-FX Trading Platform API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "github": "Mouy-leng",
        "repository": "https://github.com/Mouy-leng/GenX_FX.git"
    }

@app.get("/health")
async def health_check():
    db_connected = False
    try:
        # Test database connection
        conn = sqlite3.connect("genxdb_fx.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        db_connected = True
    except Exception:
        db_connected = False

    return {
        "status": "healthy" if db_connected else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ml_service": "active",
            "data_service": "active" if db_connected else "inactive",
            "database": "connected" if db_connected else "disconnected"
        }
    }

@app.get("/api/v1/health")
async def api_health_check():
    return {
        "status": "healthy",
        "services": {
            "ml_service": "active",
            "data_service": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/predictions")
async def get_predictions():
    return {
        "predictions": [],
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/predictions/")
async def post_predictions(request: Request):
    try:
        data = await request.json()
        if not data:
            return JSONResponse(status_code=400, content={"detail": "Empty JSON body received"})
        return {"status": "received", "data": data}
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Malformed JSON"})

@app.post("/api/v1/predictions/predict")
async def predict(request: Request):
    data = await request.json()
    service = MLService()
    await service.initialize()
    symbol = data.get("symbol", "")
    prediction = await service.predict(symbol, data)
    await service.shutdown()
    return JSONResponse(status_code=200, content=prediction)


@app.post("/api/v1/market-data/")
async def market_data(request: Request):
    data = await request.json()
    # Basic security check for SQL injection keywords
    payload_str = str(data).lower()
    if "drop table" in payload_str or "' or '" in payload_str or "delete from" in payload_str:
        return JSONResponse(status_code=400, content={"error": "Malicious payload detected"})
    return {"status": "received", "data": data}


def get_db_connection():
    conn = sqlite3.connect("genxdb_fx.db")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_market_data_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        open_price REAL,
        high_price REAL,
        low_price REAL,
        close_price REAL,
        volume REAL
    );
    """)

    # Check if there's any data
    cursor.execute("SELECT COUNT(*) FROM market_data")
    count = cursor.fetchone()[0]

    # Insert sample data if the table is empty
    if count == 0:
        sample_data = [
            ('EUR/USD', datetime.now() - timedelta(minutes=10), 1.0550, 1.0560, 1.0540, 1.0555, 1000),
            ('EUR/USD', datetime.now() - timedelta(hours=1), 1.0555, 1.0575, 1.0550, 1.0570, 1200),
            ('EUR/USD', datetime.now() - timedelta(hours=2), 1.0570, 1.0580, 1.0565, 1.0575, 1100),
            ('EUR/USD', datetime.now() - timedelta(days=1), 1.0500, 1.0520, 1.0490, 1.0510, 2500),
            ('GBP/USD', datetime.now() - timedelta(minutes=30), 1.2150, 1.2160, 1.2140, 1.2155, 800)
        ]
        cursor.executemany("""
        INSERT INTO market_data (symbol, timestamp, open_price, high_price, low_price, close_price, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_data)

    conn.commit()
    conn.close()

# Initialize the table on startup
initialize_market_data_table()

@app.get("/api/v1/market-data/{symbol:path}/{timeframe}")
async def get_historical_market_data(symbol: str, timeframe: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    time_delta = None
    if timeframe.upper() == '1H':
        time_delta = timedelta(hours=1)
    elif timeframe.upper() == '4H':
        time_delta = timedelta(hours=4)
    elif timeframe.upper() == '1D':
        time_delta = timedelta(days=1)

    if not time_delta:
        return JSONResponse(status_code=400, content={"error": "Invalid timeframe. Use '1H', '4H', or '1D'."})

    start_time = datetime.now() - time_delta

    cursor.execute("""
        SELECT timestamp, open_price, high_price, low_price, close_price, volume
        FROM market_data
        WHERE symbol = ? AND timestamp >= ?
        ORDER BY timestamp DESC
    """, (symbol, start_time))

    data = cursor.fetchall()
    conn.close()

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "data": [dict(row) for row in data]
    }

@app.get("/trading-pairs")
async def get_trading_pairs():
    try:
        conn = sqlite3.connect("genxdb_fx.db")
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, base_currency, quote_currency FROM trading_pairs WHERE is_active = 1")
        pairs = cursor.fetchall()
        conn.close()
        
        return {
            "trading_pairs": [
                {
                    "symbol": pair[0],
                    "base_currency": pair[1],
                    "quote_currency": pair[2]
                }
                for pair in pairs
            ]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/users")
async def get_users():
    try:
        conn = sqlite3.connect("genxdb_fx.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, is_active FROM users")
        users = cursor.fetchall()
        conn.close()
        
        return {
            "users": [
                {
                    "username": user[0],
                    "email": user[1],
                    "is_active": bool(user[2])
                }
                for user in users
            ]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/mt5-info")
async def get_mt5_info():
    return {
        "login": "279023502",
        "server": "Exness-MT5Trial8",
        "status": "configured"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
