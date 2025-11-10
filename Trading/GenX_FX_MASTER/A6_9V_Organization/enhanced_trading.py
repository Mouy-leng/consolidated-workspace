#!/usr/bin/env python3
"""
Enhanced GenX_FX Trading System with Gemini AI
"""
from fastapi import FastAPI
from datetime import datetime
import uvicorn
import requests
import os
import json

app = FastAPI(title="GenX FX Enhanced Trading")

class GeminiTrader:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDnjcaXnDpm1TzmIAV7EnoluI6w7wGBagM")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    
    def get_signal(self, symbol):
        prompt = f"Analyze {symbol} forex pair. Return JSON: {{\"action\":\"BUY/SELL/HOLD\",\"confidence\":0.8,\"entry\":1.2345}}"
        
        try:
            response = requests.post(
                self.base_url,
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Simple signal generation based on AI response
                if "BUY" in text.upper():
                    return {"action": "BUY", "confidence": 0.8}
                elif "SELL" in text.upper():
                    return {"action": "SELL", "confidence": 0.7}
                else:
                    return {"action": "HOLD", "confidence": 0.5}
        except:
            pass
        
        # Fallback signals
        return {"action": "BUY", "confidence": 0.6}

trader = GeminiTrader()

@app.get("/")
def root():
    return {
        "status": "GenX FX Enhanced - Gemini AI Powered",
        "timestamp": datetime.now().isoformat(),
        "ai_engine": "Google Gemini",
        "version": "2.0"
    }

@app.get("/MT4_Signals.csv")
def mt4_signals():
    symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
    prices = {"XAUUSD": 2020.50, "EURUSD": 1.0850, "GBPUSD": 1.2650, "USDJPY": 149.50}
    
    csv_content = "Symbol,Action,Entry,StopLoss,TakeProfit,Confidence\n"
    
    for symbol in symbols:
        signal = trader.get_signal(symbol)
        entry = prices.get(symbol, 1.0000)
        
        if signal["action"] == "BUY":
            stop_loss = entry * 0.995
            take_profit = entry * 1.015
        else:
            stop_loss = entry * 1.005
            take_profit = entry * 0.985
        
        csv_content += f"{symbol},{signal['action']},{entry:.5f},{stop_loss:.5f},{take_profit:.5f},{signal['confidence']:.2f}\n"
    
    return csv_content

@app.get("/signals/live")
def live_signals():
    symbols = ["XAUUSD", "EURUSD", "GBPUSD"]
    signals = []
    
    for symbol in symbols:
        signal = trader.get_signal(symbol)
        signals.append({
            "symbol": symbol,
            "action": signal["action"],
            "confidence": signal["confidence"],
            "timestamp": datetime.now().isoformat(),
            "ai_engine": "gemini"
        })
    
    return {"signals": signals, "count": len(signals)}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "genx-enhanced", "ai": "gemini"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)