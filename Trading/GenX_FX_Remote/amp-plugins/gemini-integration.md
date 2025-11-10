# AMP Plugin: Gemini AI Integration

## Description
Integrates Google Gemini AI for advanced market analysis and trading signal generation.

## Command

```bash
amp plugin install gemini-integration \
  --source genx-trading \
  --add-dependency google-generativeai>=0.3.0 \
  --add-env GEMINI_API_KEY=$GEMINI_API_KEY \
  --add-env API_PROVIDER=gemini \
  --enable-service gemini_service \
  --description "Google Gemini AI integration for market analysis"
```

## Features
- Market sentiment analysis using Gemini AI
- Trading signal generation with natural language processing
- Advanced pattern recognition through AI
- Real-time market commentary and insights
- Multi-modal analysis (text, numerical data)

## Configuration
Set your Gemini API key:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

## Usage
```python
from api.services.gemini_service import GeminiService

# Initialize service
gemini = GeminiService()
await gemini.initialize()

# Analyze market sentiment
sentiment = await gemini.analyze_market_sentiment(news_data)

# Generate trading signals
signals = await gemini.analyze_trading_signals(market_data, news_data)
```

## API Endpoints
- `GET /api/v1/ai/sentiment` - Get market sentiment analysis
- `POST /api/v1/ai/signals` - Generate trading signals
- `GET /api/v1/ai/status` - Check AI service status

## Dependencies
- google-generativeai>=0.3.0
- aiohttp>=3.9.0
- python-dotenv>=1.0.0
