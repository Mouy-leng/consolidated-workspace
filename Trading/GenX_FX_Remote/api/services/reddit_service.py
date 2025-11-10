"""
Reddit Integration Service for GenX Trading Platform
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import praw
import os
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class RedditService:
    """Service for fetching and analyzing Reddit data"""
    
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "GenX-Trading-Bot/1.0")
        
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            raise ValueError("Reddit credentials are not properly configured")
        
        self.reddit = None
        self.initialized = False
        
        # Trading-related subreddits
        self.trading_subreddits = [
            "wallstreetbets",
            "investing",
            "stocks",
            "cryptocurrency",
            "Bitcoin",
            "ethereum",
            "CryptoMarkets",
            "SecurityAnalysis",
            "ValueInvesting",
            "options",
            "Forex",
            "pennystocks"
        ]
        
        # Keywords for filtering relevant posts
        self.crypto_keywords = [
            "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain",
            "defi", "nft", "altcoin", "hodl", "moon", "dip", "pump", "dump"
        ]
        
        self.stock_keywords = [
            "spy", "qqq", "tsla", "aapl", "msft", "nvda", "earnings",
            "bull", "bear", "calls", "puts", "options", "squeeze"
        ]
    
    async def initialize(self):
        """Initialize Reddit API connection"""
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                password=self.password,
                user_agent=self.user_agent
            )
            
            # Test connection
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.reddit.user.me()
            )
            
            logger.info("Reddit service initialized successfully")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Reddit service: {e}")
            return False
    
    async def get_trending_posts(self, subreddit_name: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get trending posts from a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            # Get hot posts
            hot_posts = await asyncio.get_event_loop().run_in_executor(
                None, lambda: list(subreddit.hot(limit=limit))
            )
            
            for post in hot_posts:
                post_data = {
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "created_utc": datetime.fromtimestamp(post.created_utc),
                    "author": str(post.author) if post.author else "deleted",
                    "subreddit": post.subreddit.display_name,
                    "url": post.url,
                    "flair": post.link_flair_text,
                    "awards": post.total_awards_received
                }
                posts.append(post_data)
            
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []
    
    async def get_crypto_sentiment(self) -> Dict[str, Any]:
        """Get cryptocurrency sentiment from Reddit"""
        try:
            crypto_subreddits = ["cryptocurrency", "Bitcoin", "ethereum", "CryptoMarkets"]
            all_posts = []
            
            for subreddit in crypto_subreddits:
                posts = await self.get_trending_posts(subreddit, limit=10)
                all_posts.extend(posts)
            
            # Filter for crypto-related posts
            crypto_posts = self._filter_posts_by_keywords(all_posts, self.crypto_keywords)
            
            # Analyze sentiment
            sentiment_data = self._analyze_post_sentiment(crypto_posts)
            
            return {
                "sentiment_score": sentiment_data["sentiment_score"],
                "post_count": len(crypto_posts),
                "avg_score": sentiment_data["avg_score"],
                "trending_topics": sentiment_data["trending_topics"],
                "top_posts": crypto_posts[:5],
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting crypto sentiment: {e}")
            return {
                "sentiment_score": 0,
                "post_count": 0,
                "avg_score": 0,
                "trending_topics": [],
                "top_posts": [],
                "timestamp": datetime.now()
            }
    
    async def get_stock_sentiment(self) -> Dict[str, Any]:
        """Get stock market sentiment from Reddit"""
        try:
            stock_subreddits = ["wallstreetbets", "investing", "stocks", "SecurityAnalysis"]
            all_posts = []
            
            for subreddit in stock_subreddits:
                posts = await self.get_trending_posts(subreddit, limit=10)
                all_posts.extend(posts)
            
            # Filter for stock-related posts
            stock_posts = self._filter_posts_by_keywords(all_posts, self.stock_keywords)
            
            # Analyze sentiment
            sentiment_data = self._analyze_post_sentiment(stock_posts)
            
            return {
                "sentiment_score": sentiment_data["sentiment_score"],
                "post_count": len(stock_posts),
                "avg_score": sentiment_data["avg_score"],
                "trending_topics": sentiment_data["trending_topics"],
                "top_posts": stock_posts[:5],
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting stock sentiment: {e}")
            return {
                "sentiment_score": 0,
                "post_count": 0,
                "avg_score": 0,
                "trending_topics": [],
                "top_posts": [],
                "timestamp": datetime.now()
            }
    
    async def get_wallstreetbets_sentiment(self) -> Dict[str, Any]:
        """Get specific WSB sentiment and trending tickers"""
        try:
            posts = await self.get_trending_posts("wallstreetbets", limit=50)
            
            # Extract ticker mentions
            tickers = self._extract_tickers(posts)
            
            # Analyze sentiment
            sentiment_data = self._analyze_post_sentiment(posts)
            
            return {
                "sentiment_score": sentiment_data["sentiment_score"],
                "trending_tickers": tickers,
                "post_count": len(posts),
                "avg_score": sentiment_data["avg_score"],
                "rocket_count": self._count_emojis(posts, "🚀"),
                "diamond_hands_count": self._count_emojis(posts, "💎"),
                "top_posts": posts[:5],
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting WSB sentiment: {e}")
            return {
                "sentiment_score": 0,
                "trending_tickers": {},
                "post_count": 0,
                "avg_score": 0,
                "rocket_count": 0,
                "diamond_hands_count": 0,
                "top_posts": [],
                "timestamp": datetime.now()
            }
    
    def _filter_posts_by_keywords(self, posts: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter posts by keywords"""
        filtered_posts = []
        
        for post in posts:
            text = f"{post['title']} {post['selftext']}".lower()
            
            if any(keyword in text for keyword in keywords):
                filtered_posts.append(post)
        
        return filtered_posts
    
    def _analyze_post_sentiment(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of posts"""
        if not posts:
            return {
                "sentiment_score": 0,
                "avg_score": 0,
                "trending_topics": []
            }
        
        # Simple sentiment based on score and upvote ratio
        total_sentiment = 0
        total_score = 0
        
        for post in posts:
            # Calculate sentiment based on score and upvote ratio
            score_weight = min(post["score"], 1000) / 1000  # Normalize score
            ratio_weight = post["upvote_ratio"]
            
            post_sentiment = (score_weight + ratio_weight) / 2
            total_sentiment += post_sentiment
            total_score += post["score"]
        
        avg_sentiment = total_sentiment / len(posts)
        avg_score = total_score / len(posts)
        
        # Extract trending topics (simplified)
        trending_topics = self._extract_trending_topics(posts)
        
        return {
            "sentiment_score": avg_sentiment,
            "avg_score": avg_score,
            "trending_topics": trending_topics
        }
    
    def _extract_tickers(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract ticker mentions from posts"""
        ticker_pattern = r'\b[A-Z]{2,5}\b'
        ticker_counts = {}
        
        # Common words to exclude
        exclude_words = {
            "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "HAD",
            "HAS", "HAVE", "HIS", "HOW", "ITS", "MAY", "NEW", "NOW", "OLD", "SEE", "TWO", "WAY", "WHO", "BOY",
            "DID", "GET", "HIM", "OWN", "SAY", "SHE", "TOO", "USE", "WSB", "CEO", "IPO", "SEC", "FDA", "USA"
        }
        
        for post in posts:
            text = f"{post['title']} {post['selftext']}"
            tickers = re.findall(ticker_pattern, text)
            
            for ticker in tickers:
                if ticker not in exclude_words and len(ticker) <= 5:
                    ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        
        # Sort by frequency and return top 10
        sorted_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_tickers[:10])
    
    def _extract_trending_topics(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extract trending topics from posts"""
        # Simple keyword extraction
        keywords = {}
        
        for post in posts:
            words = post["title"].lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    keywords[word] = keywords.get(word, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:5]]
    
    def _count_emojis(self, posts: List[Dict[str, Any]], emoji: str) -> int:
        """Count specific emoji occurrences"""
        count = 0
        for post in posts:
            text = f"{post['title']} {post['selftext']}"
            count += text.count(emoji)
        return count
    
    async def health_check(self) -> bool:
        """Check if Reddit service is healthy"""
        try:
            if not self.initialized:
                return False
            
            # Test by getting user info
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.reddit.user.me()
            )
            return True
            
        except Exception as e:
            logger.error(f"Reddit health check failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the Reddit service"""
        logger.info("Shutting down Reddit service...")
        self.initialized = False
