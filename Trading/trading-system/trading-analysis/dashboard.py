#!/usr/bin/env python3
"""
Trading Analysis Dashboard
Real-time trading analysis with web interface using Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os

# Add analysis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'analysis-engine'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'strategies'))

try:
    from core_analysis import TradingAnalysisEngine, TechnicalIndicators, PatternRecognition, SmartMoneyAnalysis
    from strategy_framework import RSIStrategy, MACDStrategy, MovingAverageCrossStrategy, BacktestEngine
except ImportError as e:
    st.error(f"Error importing analysis modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Trading Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .bullish { color: #00ff00; }
    .bearish { color: #ff0000; }
    .neutral { color: #888888; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_engine' not in st.session_state:
    st.session_state.analysis_engine = TradingAnalysisEngine()
    st.session_state.pattern_recognition = PatternRecognition()
    st.session_state.smart_money = SmartMoneyAnalysis()

def load_forex_data(symbol: str, period: str = "1d", interval: str = "1h"):
    """Load forex data using yfinance"""
    try:
        # Convert forex symbol to Yahoo Finance format
        yahoo_symbol = f"{symbol}=X"
        
        # Define period mapping
        period_map = {
            "1d": "1d",
            "5d": "5d", 
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "2y": "2y"
        }
        
        ticker = yf.Ticker(yahoo_symbol)
        data = ticker.history(period=period_map.get(period, "1mo"), interval=interval)
        
        if data.empty:
            st.error(f"No data available for {symbol}")
            return None
            
        return data
        
    except Exception as e:
        st.error(f"Error loading data for {symbol}: {e}")
        return None

def create_candlestick_chart(data: pd.DataFrame, title: str = "Price Chart"):
    """Create candlestick chart with technical indicators"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price', 'Volume', 'RSI'),
        row_width=[0.2, 0.1, 0.1]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Price"
        ),
        row=1, col=1
    )
    
    # Moving averages
    ma_20 = data['Close'].rolling(window=20).mean()
    ma_50 = data['Close'].rolling(window=50).mean()
    
    fig.add_trace(
        go.Scatter(x=data.index, y=ma_20, line=dict(color='orange', width=1), name='MA(20)'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=data.index, y=ma_50, line=dict(color='blue', width=1), name='MA(50)'),
        row=1, col=1
    )
    
    # Volume
    fig.add_trace(
        go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='rgba(158,202,225,0.8)'),
        row=2, col=1
    )
    
    # RSI
    rsi = TechnicalIndicators.calculate_rsi(data['Close'])
    fig.add_trace(
        go.Scatter(x=data.index, y=rsi, line=dict(color='purple', width=2), name='RSI'),
        row=3, col=1
    )
    
    # RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True
    )
    
    return fig

def create_indicators_chart(data: pd.DataFrame):
    """Create technical indicators chart"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('MACD', 'Bollinger Bands', 'RSI', 'Volume Profile'),
        vertical_spacing=0.08,
        horizontal_spacing=0.08
    )
    
    # MACD
    macd_data = TechnicalIndicators.calculate_macd(data['Close'])
    fig.add_trace(
        go.Scatter(x=data.index, y=macd_data['macd'], name='MACD', line=dict(color='blue')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=macd_data['signal'], name='Signal', line=dict(color='red')),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=data.index, y=macd_data['histogram'], name='Histogram', marker_color='gray'),
        row=1, col=1
    )
    
    # Bollinger Bands
    bb_data = TechnicalIndicators.calculate_bollinger_bands(data['Close'])
    fig.add_trace(
        go.Scatter(x=data.index, y=data['Close'], name='Close', line=dict(color='black')),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=bb_data['upper'], name='BB Upper', line=dict(color='red', dash='dash')),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=bb_data['lower'], name='BB Lower', line=dict(color='green', dash='dash')),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=bb_data['middle'], name='BB Middle', line=dict(color='blue')),
        row=1, col=2
    )
    
    # RSI
    rsi = TechnicalIndicators.calculate_rsi(data['Close'])
    fig.add_trace(
        go.Scatter(x=data.index, y=rsi, name='RSI', line=dict(color='purple')),
        row=2, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)
    
    # Volume Profile (simplified)
    volume_profile = data['Volume'].rolling(window=20).mean()
    fig.add_trace(
        go.Scatter(x=data.index, y=volume_profile, name='Volume MA(20)', line=dict(color='orange')),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Technical Indicators Analysis")
    
    return fig

def main():
    """Main dashboard function"""
    
    # Sidebar
    st.sidebar.title("📊 Trading Analysis")
    st.sidebar.markdown("---")
    
    # Page navigation
    page = st.sidebar.radio(
        "Select Page",
        ["📈 Technical Analysis", "🔥 TradingView Charts", "🎯 Strategy Testing"],
        index=0
    )
    
    if page == "🔥 TradingView Charts":
        # Import and run TradingView integration
        try:
            from tradingview_integration import display_tradingview_dashboard
            display_tradingview_dashboard()
            return
        except ImportError:
            st.error("TradingView integration module not found")
            return
    
    # Symbol selection
    symbol = st.sidebar.selectbox(
        "Select Currency Pair",
        ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF", "XAUUSD"],
        index=7  # Default to XAUUSD
    )
    
    # Time period selection
    period = st.sidebar.selectbox(
        "Time Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
        index=2
    )
    
    # Interval selection
    interval = st.sidebar.selectbox(
        "Interval", 
        ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        index=4
    )
    
    # Analysis options
    st.sidebar.markdown("### Analysis Options")
    show_patterns = st.sidebar.checkbox("Pattern Recognition", value=True)
    show_smart_money = st.sidebar.checkbox("Smart Money Analysis", value=True)
    show_indicators = st.sidebar.checkbox("Technical Indicators", value=True)
    
    # Load data
    if st.sidebar.button("Load Data") or 'current_data' not in st.session_state:
        with st.spinner(f"Loading {symbol} data..."):
            data = load_forex_data(symbol, period, interval)
            if data is not None:
                st.session_state.current_data = data
                st.session_state.current_symbol = symbol
                st.success(f"Loaded {len(data)} bars for {symbol}")
    
    # Main content
    st.title(f"📈 Trading Analysis Dashboard - {symbol}")
    
    if 'current_data' not in st.session_state:
        st.info("Please load data using the sidebar")
        return
    
    data = st.session_state.current_data
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100
        
        st.metric(
            "Current Price",
            f"{current_price:.5f}",
            f"{price_change:+.5f} ({price_change_pct:+.2f}%)"
        )
    
    with col2:
        high_24h = data['High'].iloc[-24:].max() if len(data) >= 24 else data['High'].max()
        low_24h = data['Low'].iloc[-24:].min() if len(data) >= 24 else data['Low'].min()
        st.metric("24H High", f"{high_24h:.5f}")
        st.metric("24H Low", f"{low_24h:.5f}")
    
    with col3:
        volume_24h = data['Volume'].iloc[-24:].sum() if len(data) >= 24 else data['Volume'].sum()
        avg_volume = data['Volume'].mean()
        volume_change = ((volume_24h / avg_volume) - 1) * 100
        st.metric("24H Volume", f"{volume_24h:,.0f}", f"{volume_change:+.1f}%")
    
    with col4:
        rsi_current = TechnicalIndicators.calculate_rsi(data['Close']).iloc[-1]
        rsi_status = "Overbought" if rsi_current > 70 else "Oversold" if rsi_current < 30 else "Neutral"
        st.metric("RSI(14)", f"{rsi_current:.1f}", rsi_status)
    
    with col5:
        # Trend analysis
        ma_20 = data['Close'].rolling(20).mean().iloc[-1]
        ma_50 = data['Close'].rolling(50).mean().iloc[-1]
        trend = "Bullish" if ma_20 > ma_50 else "Bearish"
        st.metric("Trend (MA20 vs MA50)", trend)
    
    # Price chart
    st.markdown("### 📊 Price Chart")
    price_chart = create_candlestick_chart(data, f"{symbol} Price Chart")
    st.plotly_chart(price_chart, use_container_width=True)
    
    # Technical indicators
    if show_indicators:
        st.markdown("### 🔧 Technical Indicators")
        indicators_chart = create_indicators_chart(data)
        st.plotly_chart(indicators_chart, use_container_width=True)
        
        # Indicator values table
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Current Indicator Values")
            rsi = TechnicalIndicators.calculate_rsi(data['Close']).iloc[-1]
            macd_data = TechnicalIndicators.calculate_macd(data['Close'])
            macd_current = macd_data['macd'].iloc[-1]
            signal_current = macd_data['signal'].iloc[-1]
            
            indicators_df = pd.DataFrame({
                'Indicator': ['RSI(14)', 'MACD', 'MACD Signal', 'MA(20)', 'MA(50)', 'MA(200)'],
                'Value': [
                    f"{rsi:.2f}",
                    f"{macd_current:.5f}",
                    f"{signal_current:.5f}",
                    f"{data['Close'].rolling(20).mean().iloc[-1]:.5f}",
                    f"{data['Close'].rolling(50).mean().iloc[-1]:.5f}",
                    f"{data['Close'].rolling(200).mean().iloc[-1]:.5f}" if len(data) >= 200 else "N/A"
                ],
                'Status': [
                    "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral",
                    "Bullish" if macd_current > signal_current else "Bearish",
                    "",
                    "Above" if current_price > data['Close'].rolling(20).mean().iloc[-1] else "Below",
                    "Above" if current_price > data['Close'].rolling(50).mean().iloc[-1] else "Below",
                    "Above" if len(data) >= 200 and current_price > data['Close'].rolling(200).mean().iloc[-1] else "Below" if len(data) >= 200 else "N/A"
                ]
            })
            
            st.dataframe(indicators_df, hide_index=True)
        
        with col2:
            st.markdown("#### Signal Summary")
            
            # Generate signals
            signals = []
            
            # RSI signals
            if rsi > 70:
                signals.append({"Signal": "RSI Overbought", "Action": "Consider Sell", "Strength": "⚠️"})
            elif rsi < 30:
                signals.append({"Signal": "RSI Oversold", "Action": "Consider Buy", "Strength": "⚠️"})
            
            # MACD signals
            if macd_current > signal_current:
                signals.append({"Signal": "MACD Bullish", "Action": "Buy Bias", "Strength": "🟢"})
            else:
                signals.append({"Signal": "MACD Bearish", "Action": "Sell Bias", "Strength": "🔴"})
            
            # MA signals
            ma_20 = data['Close'].rolling(20).mean().iloc[-1]
            ma_50 = data['Close'].rolling(50).mean().iloc[-1]
            
            if ma_20 > ma_50:
                signals.append({"Signal": "MA(20) > MA(50)", "Action": "Bullish Trend", "Strength": "🟢"})
            else:
                signals.append({"Signal": "MA(20) < MA(50)", "Action": "Bearish Trend", "Strength": "🔴"})
            
            if signals:
                signals_df = pd.DataFrame(signals)
                st.dataframe(signals_df, hide_index=True)
            else:
                st.info("No clear signals at the moment")
    
    # Pattern recognition
    if show_patterns:
        st.markdown("### 🔍 Pattern Recognition")
        
        try:
            patterns = st.session_state.pattern_recognition.detect_patterns(data)
            
            if patterns:
                for pattern_type, pattern_list in patterns.items():
                    if pattern_list:
                        st.markdown(f"#### {pattern_type.replace('_', ' ').title()} Patterns")
                        
                        for i, pattern in enumerate(pattern_list[:3]):  # Show top 3 patterns
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**Pattern {i+1}**")
                                st.write(f"Type: {pattern['type']}")
                                st.write(f"Strength: {pattern.get('strength', 0):.2f}")
                            
                            with col2:
                                st.write(f"Start: {data.index[pattern['start_index']].strftime('%Y-%m-%d %H:%M')}")
                                st.write(f"End: {data.index[pattern['end_index']].strftime('%Y-%m-%d %H:%M')}")
                            
                            with col3:
                                if pattern_type == 'double_top':
                                    st.write("📉 Bearish Pattern")
                                    st.write("Potential reversal signal")
                                elif pattern_type == 'double_bottom':
                                    st.write("📈 Bullish Pattern") 
                                    st.write("Potential reversal signal")
                                else:
                                    st.write("📊 Continuation Pattern")
            else:
                st.info("No patterns detected in current data")
                
        except Exception as e:
            st.error(f"Error in pattern recognition: {e}")
    
    # Smart money analysis
    if show_smart_money:
        st.markdown("### 🧠 Smart Money Analysis")
        
        try:
            # Market structure analysis
            market_structure = st.session_state.smart_money.analyze_market_structure(data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Market Structure")
                trend_color = "🟢" if market_structure['trend'] == 'uptrend' else "🔴" if market_structure['trend'] == 'downtrend' else "🟡"
                st.write(f"**Current Trend:** {trend_color} {market_structure['trend'].title()}")
                
                if market_structure['swing_highs']:
                    st.write("**Recent Swing Highs:**")
                    for swing in market_structure['swing_highs'][-3:]:
                        st.write(f"  • {swing['price']:.5f} at {swing['timestamp'].strftime('%m-%d %H:%M')}")
                
                if market_structure['swing_lows']:
                    st.write("**Recent Swing Lows:**")
                    for swing in market_structure['swing_lows'][-3:]:
                        st.write(f"  • {swing['price']:.5f} at {swing['timestamp'].strftime('%m-%d %H:%M')}")
            
            with col2:
                st.markdown("#### Order Blocks & Liquidity")
                
                # Order blocks
                order_blocks = st.session_state.smart_money.identify_order_blocks(data)
                if order_blocks:
                    st.write("**Order Blocks Found:**")
                    for ob in order_blocks[-3:]:  # Show last 3
                        block_type = "🟢 Bullish" if ob['type'] == 'bullish_order_block' else "🔴 Bearish"
                        st.write(f"  • {block_type} OB")
                        st.write(f"    Zone: {ob['zone_low']:.5f} - {ob['zone_high']:.5f}")
                        st.write(f"    Strength: {ob['strength']:.2f}")
                else:
                    st.info("No order blocks detected")
                
                # Liquidity zones
                liquidity_zones = st.session_state.smart_money.identify_liquidity_zones(data)
                if liquidity_zones:
                    st.write("**Liquidity Zones:**")
                    for lz in liquidity_zones[-3:]:  # Show top 3
                        zone_type = "🔴 Resistance" if lz['zone_type'] == 'resistance' else "🟢 Support"
                        st.write(f"  • {zone_type} at {lz['level']:.5f}")
                        st.write(f"    Touches: {lz['touches']}, Strength: {lz['strength']:.2f}")
                else:
                    st.info("No significant liquidity zones found")
                    
        except Exception as e:
            st.error(f"Error in smart money analysis: {e}")
    
    # Strategy backtesting section
    with st.expander("📈 Strategy Backtesting"):
        st.markdown("### Strategy Backtesting")
        
        strategy_type = st.selectbox(
            "Select Strategy",
            ["RSI Strategy", "MACD Strategy", "MA Cross Strategy"]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if strategy_type == "RSI Strategy":
                rsi_period = st.slider("RSI Period", 5, 30, 14)
                oversold = st.slider("Oversold Level", 20, 40, 30)
                overbought = st.slider("Overbought Level", 60, 80, 70)
                strategy = RSIStrategy(rsi_period, oversold, overbought)
            
            elif strategy_type == "MACD Strategy":
                fast_period = st.slider("MACD Fast Period", 5, 20, 12)
                slow_period = st.slider("MACD Slow Period", 20, 40, 26)
                signal_period = st.slider("MACD Signal Period", 5, 15, 9)
                strategy = MACDStrategy(fast_period, slow_period, signal_period)
            
            else:  # MA Cross Strategy
                fast_ma = st.slider("Fast MA Period", 5, 50, 20)
                slow_ma = st.slider("Slow MA Period", 20, 200, 50)
                strategy = MovingAverageCrossStrategy(fast_ma, slow_ma)
        
        with col2:
            if st.button("Run Backtest"):
                with st.spinner("Running backtest..."):
                    try:
                        backtest_engine = BacktestEngine()
                        
                        # Use subset of data for backtesting
                        backtest_data = data.iloc[-500:] if len(data) > 500 else data
                        
                        performance = backtest_engine.run_backtest(strategy, backtest_data)
                        
                        # Display results
                        st.success("Backtest completed!")
                        
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        
                        with metrics_col1:
                            st.metric("Total Trades", performance.total_trades)
                            st.metric("Win Rate", f"{performance.win_rate:.2%}")
                            st.metric("Total PnL", f"${performance.total_pnl:.2f}")
                        
                        with metrics_col2:
                            st.metric("Profit Factor", f"{performance.profit_factor:.2f}")
                            st.metric("Max Drawdown", f"{performance.max_drawdown:.2%}")
                            st.metric("Sharpe Ratio", f"{performance.sharpe_ratio:.2f}")
                        
                        with metrics_col3:
                            st.metric("Avg Win", f"${performance.avg_win:.2f}")
                            st.metric("Avg Loss", f"${performance.avg_loss:.2f}")
                            st.metric("Max Consecutive Wins", performance.max_consecutive_wins)
                        
                        # Trade history
                        if strategy.trades:
                            st.markdown("#### Recent Trades")
                            trades_data = []
                            for trade in strategy.trades[-10:]:  # Last 10 trades
                                trades_data.append({
                                    'Time': trade.entry_time.strftime('%Y-%m-%d %H:%M'),
                                    'Side': trade.side.value,
                                    'Entry': f"{trade.entry_price:.5f}",
                                    'Exit': f"{trade.exit_price:.5f}" if trade.exit_price else "Open",
                                    'PnL': f"${trade.pnl:.2f}" if not trade.is_open else "Open",
                                    'Status': "Closed" if not trade.is_open else "Open"
                                })
                            
                            trades_df = pd.DataFrame(trades_data)
                            st.dataframe(trades_df, hide_index=True)
                    
                    except Exception as e:
                        st.error(f"Backtest error: {e}")

    # Footer
    st.markdown("---")
    st.markdown("📊 **Trading Analysis Dashboard** | Real-time market analysis and strategy development")

if __name__ == "__main__":
    main()