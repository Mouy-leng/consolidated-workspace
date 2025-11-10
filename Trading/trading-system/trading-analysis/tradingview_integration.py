#!/usr/bin/env python3
"""
TradingView Integration Module
Provides TradingView chart embedding and data integration
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd

class TradingViewIntegration:
    def __init__(self):
        self.base_url = "https://www.tradingview.com"
        self.session = requests.Session()
        
    def create_chart_widget(self, symbol="XAUUSD", interval="1h", theme="dark", width=800, height=500):
        """Create TradingView chart widget HTML"""
        widget_html = f"""
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div id="tradingview_chart"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
          "width": {width},
          "height": {height},
          "symbol": "{symbol}",
          "interval": "{interval}",
          "timezone": "Etc/UTC",
          "theme": "{theme}",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tradingview_chart"
          }});
          </script>
        </div>
        <!-- TradingView Widget END -->
        """
        return widget_html
    
    def create_advanced_chart(self, symbol="XAUUSD", width="100%", height="600"):
        """Create advanced TradingView chart with more features"""
        chart_html = f"""
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container" style="height:{height};width:{width}">
          <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
          {{
          "width": "{width}",
          "height": "{height}",
          "symbol": "{symbol}",
          "interval": "15",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "enable_publishing": false,
          "backgroundColor": "rgba(19, 23, 34, 1)",
          "gridColor": "rgba(42, 46, 57, 0.5)",
          "hide_top_toolbar": false,
          "hide_legend": false,
          "save_image": false,
          "container_id": "tradingview_advanced"
          }}
          </script>
        </div>
        <!-- TradingView Widget END -->
        """
        return chart_html
    
    def create_market_overview_widget(self):
        """Create market overview widget"""
        widget_html = """
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
          {
          "colorTheme": "dark",
          "dateRange": "12M",
          "showChart": true,
          "locale": "en",
          "width": "100%",
          "height": "400",
          "largeChartUrl": "",
          "isTransparent": false,
          "showSymbolLogo": true,
          "showFloatingTooltip": false,
          "plotLineColorGrowing": "rgba(41, 98, 255, 1)",
          "plotLineColorFalling": "rgba(41, 98, 255, 1)",
          "gridLineColor": "rgba(42, 46, 57, 1)",
          "scaleFontColor": "rgba(120, 123, 134, 1)",
          "belowLineFillColorGrowing": "rgba(41, 98, 255, 0.12)",
          "belowLineFillColorFalling": "rgba(41, 98, 255, 0.12)",
          "belowLineFillColorGrowingBottom": "rgba(41, 98, 255, 0)",
          "belowLineFillColorFallingBottom": "rgba(41, 98, 255, 0)",
          "symbolActiveColor": "rgba(41, 98, 255, 0.12)",
          "tabs": [
            {
              "title": "Forex",
              "symbols": [
                {
                  "s": "OANDA:XAUUSD",
                  "d": "Gold"
                },
                {
                  "s": "FX:EURUSD",
                  "d": "EUR/USD"
                },
                {
                  "s": "FX:GBPUSD",
                  "d": "GBP/USD"
                },
                {
                  "s": "FX:USDJPY",
                  "d": "USD/JPY"
                }
              ],
              "originalTitle": "Forex"
            }
          ]
        }
          </script>
        </div>
        <!-- TradingView Widget END -->
        """
        return widget_html
    
    def create_economic_calendar_widget(self):
        """Create economic calendar widget"""
        widget_html = """
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
          {
          "colorTheme": "dark",
          "isTransparent": false,
          "width": "100%",
          "height": "400",
          "locale": "en",
          "importanceFilter": "-1,0,1",
          "countryFilter": "us,gb,jp,de,fr,it,es,ca,au,nz,ch"
          }
          </script>
        </div>
        <!-- TradingView Widget END -->
        """
        return widget_html

def display_tradingview_dashboard():
    """Display TradingView integrated dashboard"""
    st.title("🔥 TradingView Integration Dashboard")
    
    tv = TradingViewIntegration()
    
    # Sidebar for settings
    st.sidebar.header("📊 Chart Settings")
    symbol = st.sidebar.selectbox("Symbol", ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCAD"])
    interval = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W"])
    chart_type = st.sidebar.selectbox("Chart Type", ["Advanced Chart", "Basic Widget", "Market Overview"])
    
    # Account Info
    st.sidebar.info("""
    📧 **Account**: Lengkundee01@gmail.com
    
    💡 **Tip**: You can manually log into TradingView 
    in a separate browser tab for full features.
    """)
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if chart_type == "Advanced Chart":
            st.subheader(f"📈 {symbol} - Advanced Chart")
            chart_html = tv.create_advanced_chart(symbol=f"OANDA:{symbol}")
            st.components.v1.html(chart_html, height=600)
            
        elif chart_type == "Basic Widget":
            st.subheader(f"📊 {symbol} - Basic Chart")
            widget_html = tv.create_chart_widget(symbol=f"OANDA:{symbol}", interval=interval)
            st.components.v1.html(widget_html, height=500)
            
        elif chart_type == "Market Overview":
            st.subheader("🌍 Market Overview")
            overview_html = tv.create_market_overview_widget()
            st.components.v1.html(overview_html, height=400)
    
    with col2:
        st.subheader("📅 Economic Calendar")
        calendar_html = tv.create_economic_calendar_widget()
        st.components.v1.html(calendar_html, height=400)
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        if st.button("🔗 Open TradingView"):
            st.info("Opening TradingView.com in new tab...")
            st.markdown("""
            <script>
            window.open('https://www.tradingview.com/chart/', '_blank');
            </script>
            """, unsafe_allow_html=True)
        
        if st.button("📱 Mobile App"):
            st.info("Download TradingView mobile app for on-the-go analysis!")
        
        if st.button("🎓 Education"):
            st.info("Access TradingView's educational resources!")

if __name__ == "__main__":
    display_tradingview_dashboard()