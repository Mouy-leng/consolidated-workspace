"""
Gemini AI Service for GenX Trading Platform
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
import os
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Chat model for conversational analysis
        self.chat_model = genai.GenerativeModel('gemini-pro')
        
        self.initialized = False
        
    async def initialize(self):
        """Initialize the Gemini service"""
        try:
            # Test connection
            response = await self.generate_text("Hello, testing connection")
            logger.info("Gemini AI service initialized successfully")
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            return False
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using Gemini"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.model.generate_content, prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini text generation error: {e}")
            return ""
    
    async def analyze_market_sentiment(self, text_data: List[str]) -> Dict[str, Any]:
        """Analyze market sentiment from text data"""
        try:
            combined_text = "\n".join(text_data[:10])  # Limit to prevent token overflow
            
            prompt = f"""
            Analyze the market sentiment from the following financial news and social media posts.
            
            Text Data:
            {combined_text}
            
            Please provide:
            1. Overall sentiment score (-1 to 1, where -1 is very bearish, 1 is very bullish)
            2. Key themes mentioned
            3. Confidence level (0-1)
            4. Recommended trading action (buy/sell/hold)
            
            Return response in JSON format:
            {{
                "sentiment_score": float,
                "themes": [list of key themes],
                "confidence": float,
                "action": "buy/sell/hold",
                "reasoning": "brief explanation"
            }}
            """
            
            response = await self.generate_text(prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                return {
                    "sentiment_score": result.get("sentiment_score", 0),
                    "themes": result.get("themes", []),
                    "confidence": result.get("confidence", 0),
                    "action": result.get("action", "hold"),
                    "reasoning": result.get("reasoning", ""),
                    "timestamp": datetime.now()
                }
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "sentiment_score": 0,
                    "themes": [],
                    "confidence": 0,
                    "action": "hold",
                    "reasoning": response[:200],
                    "timestamp": datetime.now()
                }
                
        except Exception as e:
            logger.error(f"Market sentiment analysis error: {e}")
            return {
                "sentiment_score": 0,
                "themes": [],
                "confidence": 0,
                "action": "hold",
                "reasoning": f"Error: {str(e)}",
                "timestamp": datetime.now()
            }
    
    async def analyze_trading_signals(self, market_data: Dict[str, Any], news_data: List[str]) -> Dict[str, Any]:
        """Analyze trading signals using market data and news"""
        try:
            prompt = f"""
            As an expert trading analyst, analyze the following market data and news to generate trading signals.
            
            Market Data:
            - Symbol: {market_data.get('symbol', 'BTCUSDT')}
            - Current Price: {market_data.get('price', 'N/A')}
            - Volume: {market_data.get('volume', 'N/A')}
            - Technical Indicators: {market_data.get('indicators', {})}
            
            Recent News:
            {chr(10).join(news_data[:5])}
            
            Please provide:
            1. Signal strength (0-1)
            2. Direction (long/short/neutral)
            3. Entry price suggestion
            4. Stop loss level
            5. Take profit level
            6. Risk assessment
            
            Return response in JSON format:
            {{
                "signal_strength": float,
                "direction": "long/short/neutral",
                "entry_price": float,
                "stop_loss": float,
                "take_profit": float,
                "risk_level": "low/medium/high",
                "reasoning": "detailed explanation"
            }}
            """
            
            response = await self.generate_text(prompt)
            
            try:
                result = json.loads(response)
                return {
                    "signal_strength": result.get("signal_strength", 0),
                    "direction": result.get("direction", "neutral"),
                    "entry_price": result.get("entry_price", 0),
                    "stop_loss": result.get("stop_loss", 0),
                    "take_profit": result.get("take_profit", 0),
                    "risk_level": result.get("risk_level", "medium"),
                    "reasoning": result.get("reasoning", ""),
                    "timestamp": datetime.now()
                }
            except json.JSONDecodeError:
                return {
                    "signal_strength": 0,
                    "direction": "neutral",
                    "entry_price": 0,
                    "stop_loss": 0,
                    "take_profit": 0,
                    "risk_level": "medium",
                    "reasoning": response[:200],
                    "timestamp": datetime.now()
                }
                
        except Exception as e:
            logger.error(f"Trading signal analysis error: {e}")
            return {
                "signal_strength": 0,
                "direction": "neutral",
                "entry_price": 0,
                "stop_loss": 0,
                "take_profit": 0,
                "risk_level": "high",
                "reasoning": f"Error: {str(e)}",
                "timestamp": datetime.now()
            }
    
    async def chat_analysis(self, messages: List[Dict[str, str]]) -> str:
        """Interactive chat analysis for complex queries"""
        try:
            # Format messages for Gemini
            conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            response = await self.generate_text(conversation)
            return response
            
        except Exception as e:
            logger.error(f"Chat analysis error: {e}")
            return f"Error in chat analysis: {str(e)}"
    
    async def health_check(self) -> bool:
        """Check if Gemini service is healthy"""
        try:
            test_response = await self.generate_text("Health check test")
            return len(test_response) > 0
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the Gemini service"""
        logger.info("Shutting down Gemini service...")
        self.initialized = False
