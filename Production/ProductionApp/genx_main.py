from fastapi import FastAPI
import os
import uvicorn

app = FastAPI(
    title="GenX Service",
    description="GenX Trading System API",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "GenX Service Running",
        "service": os.getenv("GENX_SERVICE", "unknown"),
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": os.getenv("GENX_SERVICE", "unknown")}

@app.get("/trading/status")
async def trading_status():
    return {"trading": "active", "pairs": ["EUR/USD", "GBP/USD"], "status": "monitoring"}

@app.get("/database/status")
async def database_status():
    return {"database": "connected", "tables": ["users", "trades", "logs"], "status": "healthy"}

@app.get("/fx/rates")
async def fx_rates():
    return {
        "rates": {
            "EUR/USD": 1.0845,
            "GBP/USD": 1.2965,
            "USD/JPY": 149.85
        },
        "timestamp": "2025-10-21T17:57:00Z",
        "source": "GenX-FX"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)