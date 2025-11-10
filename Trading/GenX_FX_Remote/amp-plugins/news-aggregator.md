# AMP Plugin: Multi-Source News Aggregator

## Description
Aggregates news from multiple financial news APIs for comprehensive market analysis.

## Command

```bash
amp plugin install news-aggregator \
  --source genx-trading \
  --add-dependency newsapi-python>=0.2.6 \
  --add-dependency alpha-vantage>=2.3.1 \
  --add-dependency finnhub-python>=2.4.0 \
  --add-dependency beautifulsoup4>=4.12.0 \
  --add-env NEWSDATA_API_KEY=$NEWSDATA_API_KEY \
  --add-env ALPHAVANTAGE_API_KEY=$ALPHAVANTAGE_API_KEY \
  --add-env NEWSAPI_ORG_KEY=$NEWSAPI_ORG_KEY \
  --add-env FINNHUB_API_KEY=$FINNHUB_API_KEY \
  --add-env FMP_API_KEY=$FMP_API_KEY \
  --enable-service news_service \
  --description "Multi-source news aggregation for market analysis"
```

## Features
- Multiple news source integration
- Real-time financial news monitoring
- Crypto-specific news filtering
- Stock market news aggregation
- Forex and currency news
- Duplicate article removal
- Sentiment-ready news preprocessing

## Supported News Sources
- NewsAPI.org
- Alpha Vantage News
- Finnhub Market News
- NewsData.io
- Financial Modeling Prep
- Custom RSS feeds

## Configuration
Set your API keys:
```bash
export NEWSDATA_API_KEY="your_newsdata_api_key"
export ALPHAVANTAGE_API_KEY="your_alphavantage_api_key"
export NEWSAPI_ORG_KEY="your_newsapi_org_key"
export FINNHUB_API_KEY="your_finnhub_api_key"
export FMP_API_KEY="your_fmp_api_key"
```

## Usage
```python
from api.services.news_service import NewsService

# Initialize service
news = NewsService()
await news.initialize()

# Get crypto news
crypto_news = await news.get_crypto_news(limit=50)

# Get stock news
stock_news = await news.get_stock_news(symbol="AAPL", limit=30)

# Get forex news
forex_news = await news.get_forex_news(limit=20)

# Get market sentiment news
sentiment_news = await news.get_market_sentiment_news()
```

## API Endpoints
- `GET /api/v1/news/crypto` - Get cryptocurrency news
- `GET /api/v1/news/stocks/{symbol}` - Get stock-specific news
- `GET /api/v1/news/forex` - Get forex and currency news
- `GET /api/v1/news/sentiment` - Get news for sentiment analysis
- `GET /api/v1/news/sources` - Get available news sources

## Dependencies
- newsapi-python>=0.2.6
- alpha-vantage>=2.3.1
- finnhub-python>=2.4.0
- beautifulsoup4>=4.12.0
- lxml>=4.9.0
- aiohttp>=3.9.0
