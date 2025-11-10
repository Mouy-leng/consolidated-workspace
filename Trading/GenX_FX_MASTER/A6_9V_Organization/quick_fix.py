#!/usr/bin/env python3
"""
GenX FX Quick Fix - Minimal Working Trading Server
"""
from fastapi import FastAPI
from datetime import datetime
import uvicorn
import json
import os

app = FastAPI(title="GenX FX Live Trading")

# Sample trading signals
SAMPLE_SIGNALS = [
    {"symbol": "XAUUSD", "action": "BUY", "entry": 2020.50, "stop_loss": 2010.00, "take_profit": 2040.00},
    {"symbol": "EURUSD", "action": "SELL", "entry": 1.0850, "stop_loss": 1.0900, "take_profit": 1.0800},
    {"symbol": "GBPUSD", "action": "BUY", "entry": 1.2650, "stop_loss": 1.2600, "take_profit": 1.2750}
]

@app.get("/")
def root():
    return {
        "status": "GenX FX Working", 
        "timestamp": datetime.now().isoformat(), 
        "port": 8080,
        "trading_enabled": True
    }

@app.get("/MT4_Signals.csv")
def mt4_signals():
    csv_content = "Symbol,Action,Entry,StopLoss,TakeProfit\n"
    for signal in SAMPLE_SIGNALS:
        csv_content += f"{signal['symbol']},{signal['action']},{signal['entry']},{signal['stop_loss']},{signal['take_profit']}\n"
    return csv_content

@app.get("/MT5_Signals.csv")
def mt5_signals():
    return mt4_signals()  # Same format for now

@app.get("/signals/json")
def signals_json():
    return {"signals": SAMPLE_SIGNALS, "timestamp": datetime.now().isoformat()}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "genx-trading"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)