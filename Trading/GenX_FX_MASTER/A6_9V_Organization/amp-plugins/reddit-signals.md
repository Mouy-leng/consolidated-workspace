# AMP Plugin: Reddit Signal Integration

## Description
Integrates Reddit API to fetch and analyze trending posts for trading signals.

## Command

```bash
amp plugin install reddit-signals \
  --source genx-trading \
  --add-dependency praw>=7.7.0 \
  --add-env REDDIT_CLIENT_ID=$REDDIT_CLIENT_ID \
  --add-env REDDIT_CLIENT_SECRET=$REDDIT_CLIENT_SECRET \
  --add-env REDDIT_USERNAME=$REDDIT_USERNAME \
  --add-env REDDIT_PASSWORD=$REDDIT_PASSWORD \
  --add-env REDDIT_USER_AGENT="GenX-Trading-Bot/1.0" \
  --enable-service reddit_service \
  --description "Reddit integration for social sentiment analysis"
```

## Features
- Real-time monitoring of trading subreddits
- Wallstreetbets sentiment analysis
- Trending ticker extraction
- Social sentiment scoring
- Emoji-based sentiment indicators (🚀, 💎, 📈)
- Multi-subreddit analysis

## Configuration
Set your Reddit API credentials:
```bash
export REDDIT_CLIENT_ID="your_reddit_client_id"
export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
export REDDIT_USERNAME="your_reddit_username"
export REDDIT_PASSWORD="your_reddit_password"
```

## Monitored Subreddits
- r/wallstreetbets
- r/investing
- r/stocks
- r/cryptocurrency
- r/Bitcoin
- r/ethereum
- r/CryptoMarkets
- r/SecurityAnalysis
- r/ValueInvesting
- r/options
- r/Forex
- r/pennystocks

## Usage
```python
from api.services.reddit_service import RedditService

# Initialize service
reddit = RedditService()
await reddit.initialize()

# Get crypto sentiment
crypto_sentiment = await reddit.get_crypto_sentiment()

# Get WSB sentiment
wsb_sentiment = await reddit.get_wallstreetbets_sentiment()

# Get trending tickers
trending = wsb_sentiment['trending_tickers']
```

## API Endpoints
- `GET /api/v1/reddit/crypto-sentiment` - Get crypto sentiment from Reddit
- `GET /api/v1/reddit/stock-sentiment` - Get stock sentiment from Reddit
- `GET /api/v1/reddit/wsb-sentiment` - Get WSB-specific sentiment
- `GET /api/v1/reddit/trending-tickers` - Get trending tickers

## Dependencies
- praw>=7.7.0
- asyncio
- datetime
- re (for ticker extraction)
