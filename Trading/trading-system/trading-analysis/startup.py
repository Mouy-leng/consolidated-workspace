#!/usr/bin/env python3
# Trading Analysis System Startup

import sys
import os
sys.path.append(os.path.dirname(__file__))

from analysis_engine.core_analysis import TradingAnalysisEngine
from strategies.strategy_framework import BacktestEngine
from ml_models.ml_framework import TradingMLModels

print("🚀 Trading Analysis System Starting...")
print("Configuration loaded from: config/analysis-config.json")

# Initialize components
analysis_engine = TradingAnalysisEngine('config/analysis-config.json')
backtest_engine = BacktestEngine()
ml_models = TradingMLModels()

print("✅ All components initialized successfully!")
print("📊 Access the dashboard at: http://localhost:8501")
