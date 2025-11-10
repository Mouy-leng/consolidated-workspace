#!/usr/bin/env python3
"""
Migrate from AMP to Gemini AI for GenX_FX Trading System
"""
import os
import requests
import json
from datetime import datetime

class GeminiTrader:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        
    def analyze_market(self, symbol, timeframe="H1"):
        """Analyze market using Gemini AI"""
        prompt = f"""
        Analyze {symbol} for {timeframe} trading:
        1. Current market sentiment
        2. Technical indicators
        3. News impact
        4. Trading recommendation (BUY/SELL/HOLD)
        5. Risk level (1-10)
        
        Provide JSON response with: action, confidence, entry_price, stop_loss, take_profit
        """
        
        try:
            response = requests.post(
                self.base_url,
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1000
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return self.parse_gemini_response(result)
            else:
                print(f"Gemini API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None
    
    def parse_gemini_response(self, response):
        """Parse Gemini response into trading signal"""
        try:
            text = response['candidates'][0]['content']['parts'][0]['text']
            # Simple parsing - in production, use more robust JSON extraction
            if "BUY" in text.upper():
                return {
                    "action": "BUY",
                    "confidence": 0.75,
                    "timestamp": datetime.now().isoformat()
                }
            elif "SELL" in text.upper():
                return {
                    "action": "SELL", 
                    "confidence": 0.75,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "action": "HOLD",
                    "confidence": 0.5,
                    "timestamp": datetime.now().isoformat()
                }
        except:
            return None

def test_gemini_integration():
    """Test Gemini AI integration"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment")
        return False
    
    trader = GeminiTrader(api_key)
    
    # Test symbols
    symbols = ["EURUSD", "XAUUSD", "GBPUSD"]
    
    print("Testing Gemini AI Integration...")
    
    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        signal = trader.analyze_market(symbol)
        
        if signal:
            print(f"SUCCESS {symbol}: {signal['action']} (confidence: {signal['confidence']})")
        else:
            print(f"FAILED {symbol}: Failed to get signal")
    
    return True

if __name__ == "__main__":
    test_gemini_integration()