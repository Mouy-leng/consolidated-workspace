"""
Enhanced Google Gemini AI integration for advanced market analysis, sentiment processing, and signal validation.
Provides contextual intelligence for trading decisions and market understanding.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import google.generativeai as genai
from ..config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class SentimentAnalysis:
    """Structured sentiment analysis result"""
    overall_sentiment: str  # "bullish", "bearish", "neutral"
    confidence: float      # 0.0 to 1.0
    emotional_tone: str    # "fear", "greed", "uncertainty", "optimism", etc.
    market_impact: str     # "high", "medium", "low"
    key_themes: List[str]
    risk_factors: List[str]
    opportunity_indicators: List[str]
    temporal_context: str  # "short-term", "medium-term", "long-term"
    source_reliability: float  # 0.0 to 1.0


@dataclass
class SignalValidation:
    """Signal validation result from Gemini AI"""
    is_valid: bool
    confidence_adjustment: float  # Multiplier for original confidence (0.5 - 2.0)
    risk_assessment: str  # "low", "medium", "high", "extreme"
    market_context_score: float  # 0.0 to 1.0
    reasoning: str
    supporting_factors: List[str]
    warning_factors: List[str]
    recommended_position_size: float  # 0.0 to 1.0 (percentage of normal size)


@dataclass
class MarketRegimeAnalysis:
    """Market regime and condition analysis"""
    regime_type: str  # "trending", "ranging", "volatile", "calm", "crisis"
    trend_direction: str  # "up", "down", "sideways"
    volatility_level: str  # "low", "normal", "high", "extreme"
    market_phase: str  # "accumulation", "distribution", "markup", "markdown"
    institutional_sentiment: str  # "risk-on", "risk-off", "neutral"
    retail_sentiment: str
    news_flow_intensity: str  # "light", "normal", "heavy", "overwhelming"


class EnhancedGeminiService:
    """Enhanced Gemini AI service for comprehensive market intelligence"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')  # Use the more advanced model
        self.conversation_history = []
        self.market_context = {}
        
    async def analyze_market_sentiment(
        self, 
        news_articles: List[str], 
        social_media_posts: List[str],
        instrument: str = "EUR/USD"
    ) -> SentimentAnalysis:
        """
        Comprehensive sentiment analysis combining news and social media
        
        Args:
            news_articles: List of news article texts
            social_media_posts: List of social media posts/comments
            instrument: Trading instrument to focus analysis on
        """
        try:
            # Prepare the analysis prompt
            prompt = self._build_sentiment_prompt(news_articles, social_media_posts, instrument)
            
            response = await self.model.generate_content_async(prompt)
            
            # Parse the structured response
            sentiment_data = self._parse_sentiment_response(response.text)
            
            return SentimentAnalysis(**sentiment_data)
            
        except Exception as e:
            logger.error(f"Error in market sentiment analysis: {e}")
            return self._get_default_sentiment()
    
    def _build_sentiment_prompt(
        self, 
        news_articles: List[str], 
        social_media_posts: List[str], 
        instrument: str
    ) -> str:
        """Build comprehensive sentiment analysis prompt"""
        
        news_text = "\n\n".join(news_articles[:10])  # Limit to avoid token limits
        social_text = "\n\n".join(social_media_posts[:20])
        
        return f"""
        As an expert financial market analyst, analyze the sentiment around {instrument} and the broader forex market based on the following information:

        NEWS ARTICLES:
        {news_text}

        SOCIAL MEDIA/FORUM POSTS:
        {social_text}

        Please provide a comprehensive analysis in the following JSON format:

        {{
            "overall_sentiment": "bullish|bearish|neutral",
            "confidence": 0.85,
            "emotional_tone": "fear|greed|uncertainty|optimism|panic|euphoria|caution",
            "market_impact": "high|medium|low",
            "key_themes": ["inflation concerns", "central bank policy", "geopolitical tensions"],
            "risk_factors": ["potential black swan events", "correlation breakdowns"],
            "opportunity_indicators": ["oversold conditions", "policy divergence"],
            "temporal_context": "short-term|medium-term|long-term",
            "source_reliability": 0.75
        }}

        Consider:
        1. The credibility and bias of sources
        2. The recency and relevance of information
        3. Correlation with historical market patterns
        4. Institutional vs retail sentiment divergence
        5. Potential market-moving events on the horizon
        6. Cross-asset implications (bonds, equities, commodities)
        7. Technical analysis context if mentioned
        8. Central bank communications and policy implications

        Provide only the JSON response without additional commentary.
        """
    
    async def validate_trading_signal(
        self,
        signal_data: Dict[str, Any],
        market_context: Dict[str, Any],
        current_sentiment: SentimentAnalysis,
        recent_news: List[str]
    ) -> SignalValidation:
        """
        Validate a trading signal using advanced AI reasoning
        
        Args:
            signal_data: Original trading signal information
            market_context: Current market conditions (price, volatility, etc.)
            current_sentiment: Latest sentiment analysis
            recent_news: Recent relevant news headlines
        """
        try:
            prompt = self._build_signal_validation_prompt(
                signal_data, market_context, current_sentiment, recent_news
            )
            
            response = await self.model.generate_content_async(prompt)
            validation_data = self._parse_validation_response(response.text)
            
            return SignalValidation(**validation_data)
            
        except Exception as e:
            logger.error(f"Error in signal validation: {e}")
            return self._get_default_validation()
    
    def _build_signal_validation_prompt(
        self,
        signal_data: Dict[str, Any],
        market_context: Dict[str, Any],
        sentiment: SentimentAnalysis,
        recent_news: List[str]
    ) -> str:
        """Build signal validation prompt"""
        
        news_summary = "\n".join(recent_news[:5])
        
        return f"""
        As an expert quantitative analyst and risk manager, evaluate this trading signal:

        SIGNAL DETAILS:
        - Instrument: {signal_data.get('instrument', 'Unknown')}
        - Action: {signal_data.get('action', 'Unknown')}
        - Confidence: {signal_data.get('confidence', 0)}
        - Generated by: {signal_data.get('model_type', 'AI Ensemble')}

        CURRENT MARKET CONTEXT:
        - Current Price: {market_context.get('current_price', 'N/A')}
        - Recent Volatility: {market_context.get('volatility', 'N/A')}
        - Volume: {market_context.get('volume', 'N/A')}
        - RSI: {market_context.get('rsi', 'N/A')}

        SENTIMENT ANALYSIS:
        - Overall Sentiment: {sentiment.overall_sentiment}
        - Confidence: {sentiment.confidence}
        - Market Impact: {sentiment.market_impact}
        - Key Themes: {', '.join(sentiment.key_themes)}

        RECENT NEWS HEADLINES:
        {news_summary}

        Evaluate this signal and provide your assessment in JSON format:

        {{
            "is_valid": true,
            "confidence_adjustment": 1.2,
            "risk_assessment": "low|medium|high|extreme",
            "market_context_score": 0.8,
            "reasoning": "Detailed explanation of your assessment",
            "supporting_factors": ["factor1", "factor2"],
            "warning_factors": ["warning1", "warning2"],
            "recommended_position_size": 0.75
        }}

        Consider:
        1. Signal-sentiment alignment
        2. Market regime appropriateness
        3. Risk-reward context
        4. Timing considerations
        5. Correlation with other assets
        6. News flow impact potential
        7. Technical vs fundamental divergence
        8. Liquidity conditions
        9. Volatility environment suitability
        10. Historical pattern recognition

        Provide only the JSON response.
        """
    
    async def analyze_market_regime(
        self,
        market_data: Dict[str, Any],
        economic_calendar: List[Dict],
        cross_asset_data: Dict[str, Any]
    ) -> MarketRegimeAnalysis:
        """
        Analyze current market regime and conditions
        
        Args:
            market_data: Price, volume, volatility data
            economic_calendar: Upcoming economic events
            cross_asset_data: Bonds, equities, commodities data
        """
        try:
            prompt = self._build_regime_analysis_prompt(
                market_data, economic_calendar, cross_asset_data
            )
            
            response = await self.model.generate_content_async(prompt)
            regime_data = self._parse_regime_response(response.text)
            
            return MarketRegimeAnalysis(**regime_data)
            
        except Exception as e:
            logger.error(f"Error in market regime analysis: {e}")
            return self._get_default_regime()
    
    async def generate_adaptive_strategy_suggestions(
        self,
        current_performance: Dict[str, Any],
        market_conditions: MarketRegimeAnalysis,
        risk_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate adaptive strategy suggestions based on current conditions
        
        Args:
            current_performance: Recent trading performance metrics
            market_conditions: Current market regime analysis
            risk_metrics: Current risk exposure and metrics
        """
        try:
            prompt = f"""
            As an expert algorithmic trading strategist, analyze the current situation and provide adaptive strategy recommendations:

            CURRENT PERFORMANCE:
            - Win Rate: {current_performance.get('win_rate', 'N/A')}%
            - Profit Factor: {current_performance.get('profit_factor', 'N/A')}
            - Max Drawdown: {current_performance.get('max_drawdown', 'N/A')}%
            - Recent P&L: {current_performance.get('recent_pnl', 'N/A')}

            MARKET CONDITIONS:
            - Regime: {market_conditions.regime_type}
            - Trend: {market_conditions.trend_direction}
            - Volatility: {market_conditions.volatility_level}
            - Phase: {market_conditions.market_phase}

            RISK METRICS:
            - Current Exposure: {risk_metrics.get('current_exposure', 'N/A')}
            - VaR: {risk_metrics.get('var', 'N/A')}
            - Correlation Risk: {risk_metrics.get('correlation_risk', 'N/A')}

            Provide strategy recommendations in JSON format:

            {{
                "overall_recommendation": "increase_aggression|maintain_current|reduce_risk|defensive_mode",
                "position_sizing_adjustment": 1.2,
                "timeframe_optimization": "focus_on_shorter|current_ok|focus_on_longer",
                "instrument_preferences": ["EUR_USD", "GBP_USD"],
                "avoid_instruments": ["USD_JPY"],
                "risk_adjustments": {{
                    "max_risk_per_trade": 0.015,
                    "max_correlation": 0.6,
                    "stop_loss_multiplier": 1.1
                }},
                "strategy_modifications": [
                    "Increase momentum filter sensitivity",
                    "Add volatility breakout component"
                ],
                "market_timing_suggestions": [
                    "Avoid trading during first hour after major news",
                    "Increase position size during London-NY overlap"
                ],
                "reasoning": "Detailed explanation of recommendations"
            }}

            Focus on:
            1. Current market regime appropriateness
            2. Performance-based adjustments
            3. Risk-adjusted optimization
            4. Market microstructure considerations
            5. Behavioral finance insights

            Provide only the JSON response.
            """
            
            response = await self.model.generate_content_async(prompt)
            return self._parse_json_response(response.text)
            
        except Exception as e:
            logger.error(f"Error generating strategy suggestions: {e}")
            return {"overall_recommendation": "maintain_current", "reasoning": "Analysis unavailable"}
    
    async def analyze_economic_event_impact(
        self,
        event_details: Dict[str, Any],
        historical_patterns: List[Dict],
        current_positions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze potential impact of upcoming economic events
        
        Args:
            event_details: Details of the economic event
            historical_patterns: Historical market reactions to similar events
            current_positions: Current trading positions
        """
        try:
            prompt = f"""
            As an expert in economic event analysis and market impact assessment, analyze this upcoming event:

            EVENT DETAILS:
            - Event: {event_details.get('name', 'Unknown')}
            - Time: {event_details.get('time', 'Unknown')}
            - Importance: {event_details.get('importance', 'Unknown')}
            - Forecast: {event_details.get('forecast', 'Unknown')}
            - Previous: {event_details.get('previous', 'Unknown')}
            - Currency: {event_details.get('currency', 'Unknown')}

            HISTORICAL PATTERNS:
            {json.dumps(historical_patterns[:3], indent=2)}

            CURRENT POSITIONS:
            {json.dumps(current_positions, indent=2)}

            Provide impact analysis in JSON format:

            {{
                "expected_volatility_increase": 1.5,
                "primary_affected_pairs": ["EUR_USD", "GBP_USD"],
                "secondary_affected_pairs": ["USD_JPY"],
                "time_horizon": "15_minutes|1_hour|4_hours|1_day",
                "directional_bias": "bullish_usd|bearish_usd|neutral",
                "confidence": 0.75,
                "position_recommendations": {{
                    "reduce_exposure": ["EUR_USD"],
                    "increase_stops": ["GBP_USD"],
                    "close_before_event": [],
                    "hedge_positions": []
                }},
                "trading_opportunities": [
                    "Volatility breakout strategy on EUR_USD",
                    "Mean reversion on initial spike"
                ],
                "risk_warnings": [
                    "Potential for multiple-standard-deviation moves",
                    "Increased slippage expected"
                ],
                "optimal_entry_timing": "pre_event|during_release|post_settlement",
                "reasoning": "Detailed analysis explanation"
            }}

            Consider:
            1. Historical precedent and patterns
            2. Current market positioning
            3. Cross-asset implications
            4. Volatility term structure impact
            5. Liquidity considerations
            6. Risk management requirements

            Provide only the JSON response.
            """
            
            response = await self.model.generate_content_async(prompt)
            return self._parse_json_response(response.text)
            
        except Exception as e:
            logger.error(f"Error analyzing economic event impact: {e}")
            return {"expected_volatility_increase": 1.0, "reasoning": "Analysis unavailable"}
    
    def _parse_sentiment_response(self, response_text: str) -> Dict[str, Any]:
        """Parse sentiment analysis response"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing sentiment response: {e}")
            return self._get_default_sentiment_data()
    
    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse signal validation response"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing validation response: {e}")
            return self._get_default_validation_data()
    
    def _parse_regime_response(self, response_text: str) -> Dict[str, Any]:
        """Parse market regime response"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing regime response: {e}")
            return self._get_default_regime_data()
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Generic JSON response parser"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
            return {}
    
    def _get_default_sentiment(self) -> SentimentAnalysis:
        """Get default sentiment analysis"""
        return SentimentAnalysis(
            overall_sentiment="neutral",
            confidence=0.5,
            emotional_tone="uncertainty",
            market_impact="low",
            key_themes=[],
            risk_factors=[],
            opportunity_indicators=[],
            temporal_context="short-term",
            source_reliability=0.5
        )
    
    def _get_default_sentiment_data(self) -> Dict[str, Any]:
        """Get default sentiment data"""
        return {
            "overall_sentiment": "neutral",
            "confidence": 0.5,
            "emotional_tone": "uncertainty",
            "market_impact": "low",
            "key_themes": [],
            "risk_factors": [],
            "opportunity_indicators": [],
            "temporal_context": "short-term",
            "source_reliability": 0.5
        }
    
    def _get_default_validation(self) -> SignalValidation:
        """Get default signal validation"""
        return SignalValidation(
            is_valid=True,
            confidence_adjustment=1.0,
            risk_assessment="medium",
            market_context_score=0.5,
            reasoning="Analysis unavailable",
            supporting_factors=[],
            warning_factors=[],
            recommended_position_size=0.5
        )
    
    def _get_default_validation_data(self) -> Dict[str, Any]:
        """Get default validation data"""
        return {
            "is_valid": True,
            "confidence_adjustment": 1.0,
            "risk_assessment": "medium",
            "market_context_score": 0.5,
            "reasoning": "Analysis unavailable",
            "supporting_factors": [],
            "warning_factors": [],
            "recommended_position_size": 0.5
        }
    
    def _get_default_regime(self) -> MarketRegimeAnalysis:
        """Get default market regime"""
        return MarketRegimeAnalysis(
            regime_type="ranging",
            trend_direction="sideways",
            volatility_level="normal",
            market_phase="accumulation",
            institutional_sentiment="neutral",
            retail_sentiment="neutral",
            news_flow_intensity="normal"
        )
    
    def _get_default_regime_data(self) -> Dict[str, Any]:
        """Get default regime data"""
        return {
            "regime_type": "ranging",
            "trend_direction": "sideways",
            "volatility_level": "normal",
            "market_phase": "accumulation",
            "institutional_sentiment": "neutral",
            "retail_sentiment": "neutral",
            "news_flow_intensity": "normal"
        }
    
    def _build_regime_analysis_prompt(
        self,
        market_data: Dict[str, Any],
        economic_calendar: List[Dict],
        cross_asset_data: Dict[str, Any]
    ) -> str:
        """Build market regime analysis prompt"""
        
        events_summary = "\n".join([
            f"- {event.get('name', 'Unknown')} at {event.get('time', 'Unknown')}"
            for event in economic_calendar[:5]
        ])
        
        return f"""
        As an expert macro analyst, analyze the current market regime based on this comprehensive data:

        FOREX MARKET DATA:
        {json.dumps(market_data, indent=2)}

        UPCOMING ECONOMIC EVENTS:
        {events_summary}

        CROSS-ASSET DATA:
        {json.dumps(cross_asset_data, indent=2)}

        Provide regime analysis in JSON format:

        {{
            "regime_type": "trending|ranging|volatile|calm|crisis",
            "trend_direction": "up|down|sideways",
            "volatility_level": "low|normal|high|extreme",
            "market_phase": "accumulation|distribution|markup|markdown",
            "institutional_sentiment": "risk_on|risk_off|neutral",
            "retail_sentiment": "risk_on|risk_off|neutral",
            "news_flow_intensity": "light|normal|heavy|overwhelming"
        }}

        Consider all available information to determine the current market environment.
        Provide only the JSON response.
        """


# Factory function
def create_enhanced_gemini_service() -> EnhancedGeminiService:
    """Create enhanced Gemini service instance"""
    return EnhancedGeminiService()
