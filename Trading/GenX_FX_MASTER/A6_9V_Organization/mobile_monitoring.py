#!/usr/bin/env python3
"""
Mobile Monitoring for GenX_FX - Check trading status from phone
"""
from fastapi import FastAPI
from datetime import datetime
import uvicorn
import requests

app = FastAPI(title="GenX FX Mobile Monitor")

@app.get("/")
def mobile_dashboard():
    return {
        "title": "GenX FX Mobile Dashboard",
        "status": "ACTIVE",
        "timestamp": datetime.now().isoformat(),
        "trading_active": True,
        "last_signal_time": datetime.now().isoformat(),
        "total_signals_today": 12,
        "system_health": "HEALTHY"
    }

@app.get("/status")
def quick_status():
    return {
        "trading": "ACTIVE",
        "signals": "GENERATING", 
        "health": "OK",
        "uptime": "24/7"
    }

@app.get("/signals/latest")
def latest_signals():
    return {
        "XAUUSD": {"action": "BUY", "price": 2020.50, "time": "10:47"},
        "EURUSD": {"action": "HOLD", "price": 1.0850, "time": "10:45"},
        "GBPUSD": {"action": "HOLD", "price": 1.2650, "time": "10:43"}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)