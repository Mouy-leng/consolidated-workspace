#!/usr/bin/env python3
"""
GenX FX Trading System - Main Entry Point
Advanced AI-powered Forex trading signal generator for MT4/5 EAs
Supports FBS Markets Inc. IO trading accounts
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.backtester import Backtester
from core.config import config
from core.data_sources.fxcm_provider import FXCMDataProvider, MockFXCMProvider
from core.ai_models.ensemble_predictor import EnsemblePredictor
from core.model_trainer import ModelTrainer
from core.trading_engine import TradingEngine
from utils.logger_setup import setup_logging

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check handler for Cloud Run"""

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = b'{"status": "healthy", ' b'"service": "genx-trading-system"}'
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default HTTP server logs
        pass


class GenXTradingSystem:
    """
    Main GenX Trading System Controller

    Modes:
    - live: Live trading signal generation
    - train: Train AI models with historical data
    - backtest: Backtest strategies
    - test: Test system components
    """

    def __init__(self):
        self.trading_engine = None
        self.is_running = False
        self.health_server = None

        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("GenX Trading System initialized")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.is_running = False
        if self.health_server:
            self.health_server.shutdown()

    def start_health_server(self, port=8080):
        """Start health check server for Cloud Run"""
        try:
            self.health_server = HTTPServer(("", port), HealthCheckHandler)
            health_thread = Thread(target=self.health_server.serve_forever, daemon=True)
            health_thread.start()
            logger.info(f"Health check server started on port {port}")
        except Exception as e:
            logger.warning(f"Could not start health server: {e}")

    async def run_live_trading(self):
        """Run live trading signal generation"""
        logger.info("🚀 Starting Live Trading Mode")

        try:
            # Initialize trading engine
            self.trading_engine = TradingEngine()

            # Start the engine
            await self.trading_engine.start()
            self.is_running = True

            logger.info("✅ Live trading started successfully")
            logger.info("📊 Signals will be output to: signal_output/")
            logger.info("📈 MT4 signals: signal_output/MT4_Signals.csv")
            logger.info("📈 MT5 signals: signal_output/MT5_Signals.csv")
            logger.info("📊 Excel dashboard: signal_output/genx_signals.xlsx")

            # Keep running until shutdown
            while self.is_running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in live trading mode: {e}")
        finally:
            if self.trading_engine:
                await self.trading_engine.stop()
            logger.info("Live trading stopped")

    async def run_training_mode(self, symbols: list = None, timeframes: list = None):
        """Run AI model training"""
        logger.info("🎯 Starting Training Mode")

        try:
            trainer = ModelTrainer(config)
            await trainer.initialize()

            symbols = symbols or config.get("trading.symbols", ["EURUSD", "GBPUSD"])
            timeframes = timeframes or config.get("trading.timeframes", ["H1", "H4"])

            logger.info(f"Training models for symbols: {symbols}")
            logger.info(f"Training timeframes: {timeframes}")

            results = await trainer.train_all_models(symbols, timeframes)

            # Display training results
            logger.info("🎓 Training Results:")
            for symbol, result in results.items():
                if result.get("status") == "success":
                    models_trained = result["models_trained"]
                    logger.info(f"  ✅ {symbol}: {models_trained} models trained")
                    model_scores = result.get("model_scores", {})
                    for model_name, scores in model_scores.items():
                        if "cv_mean" in scores:
                            cv_mean = scores["cv_mean"]
                            cv_std = scores["cv_std"]
                            logger.info(
                                f"    📊 {model_name}: {cv_mean:.3f} ± " f"{cv_std:.3f}"
                            )
                else:
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"  ❌ {symbol}: {error_msg}")

            logger.info("✅ Training completed")

        except Exception as e:
            logger.error(f"Error in training mode: {e}")

    async def run_backtesting(self, start_date: str = None, end_date: str = None):
        """Run backtesting"""
        logger.info("📈 Starting Backtesting Mode")

        try:
            backtester = Backtester(config)
            await backtester.initialize()

            start_date = start_date or config.get(
                "backtesting.default_start_date", "2023-01-01"
            )
            end_date = end_date or datetime.now().strftime("%Y-%m-%d")

            logger.info(f"Backtesting period: {start_date} to {end_date}")

            results = await backtester.run_backtest(
                start_date=start_date,
                end_date=end_date,
                symbols=config.get("trading.symbols", ["EURUSD"]),
            )

            # Display backtest results
            logger.info("📊 Backtest Results:")
            for symbol, result in results.items():
                stats = result.get("statistics", {})
                logger.info(f"  📈 {symbol}:")
                logger.info(f"    Total Trades: {stats.get('total_trades', 0)}")
                logger.info(f"    Win Rate: {stats.get('win_rate', 0):.2%}")
                logger.info(f"    Total Return: {stats.get('total_return', 0):.2%}")
                logger.info(f"    Sharpe Ratio: {stats.get('sharpe_ratio', 0):.3f}")
                logger.info(f"    Max Drawdown: {stats.get('max_drawdown', 0):.2%}")

            logger.info("✅ Backtesting completed")

        except Exception as e:
            logger.error(f"Error in backtesting mode: {e}")

    async def run_test_mode(self):
        """Run system tests"""
        logger.info("🧪 Starting Test Mode")

        try:
            # Test data provider connection
            logger.info("Testing data provider...")
            if config.get("fxcm.use_mock", True):
                data_provider = MockFXCMProvider(config.get("fxcm"))
            else:
                data_provider = FXCMDataProvider(config.get("fxcm"))

            connected = await data_provider.connect()
            if connected:
                logger.info("✅ Data provider connection successful")

                # Test data retrieval
                test_data = await data_provider.get_historical_data("EURUSD", "H1", 100)
                data_points = len(test_data)
                logger.info(f"✅ Retrieved {data_points} data points for EURUSD")

                await data_provider.disconnect()
            else:
                logger.error("❌ Data provider connection failed")
                return

            # Test AI predictor
            logger.info("Testing AI predictor...")
            predictor = EnsemblePredictor(config.get("ai_models"))
            await predictor.initialize()

            if len(test_data) > 50:
                prediction = await predictor.predict("EURUSD", test_data)
                confidence = prediction["confidence"]
                logger.info(f"✅ AI prediction generated: confidence={confidence:.3f}")

            # Test signal generation
            logger.info("Testing signal generation...")
            self.trading_engine = TradingEngine()
            test_signals = await self.trading_engine.force_signal_generation(["EURUSD"])

            if test_signals:
                signals_count = len(test_signals)
                logger.info(f"✅ Generated {signals_count} test signals")
                for test_signal in test_signals:
                    symbol = test_signal.symbol
                    signal_type = test_signal.signal_type.value
                    confidence = test_signal.confidence
                    logger.info(f"  📊 {symbol}: {signal_type} @ {confidence:.3f}")
            else:
                logger.warning("⚠️  No test signals generated")

            logger.info("✅ All tests completed successfully")

        except Exception as e:
            logger.error(f"Error in test mode: {e}")

    async def generate_sample_signals(self, count: int = 5):
        """Generate sample signals for testing MT4/5 integration"""
        logger.info(f"🎲 Generating {count} sample signals")

        try:
            self.trading_engine = TradingEngine()
            await self.trading_engine.data_provider.connect()
            await self.trading_engine.ensemble_predictor.initialize()
            await self.trading_engine.spreadsheet_manager.initialize()

            symbols = config.get("trading.symbols", ["EURUSD", "GBPUSD"])[:count]
            signals = await self.trading_engine.force_signal_generation(symbols)

            if signals:
                spreadsheet_manager = self.trading_engine.spreadsheet_manager
                await spreadsheet_manager.update_signals(signals)

                signals_count = len(signals)
                logger.info(f"✅ Generated {signals_count} sample signals")
                logger.info("📁 Output files created:")
                logger.info("  📊 signal_output/genx_signals.xlsx")
                logger.info("  📈 signal_output/MT4_Signals.csv")
                logger.info("  📈 signal_output/MT5_Signals.csv")

                # Display signal summary
                for sample_signal in signals:
                    symbol = sample_signal.symbol
                    signal_type = sample_signal.signal_type.value
                    entry_price = sample_signal.entry_price
                    confidence = sample_signal.confidence
                    logger.info(
                        f"  🎯 {symbol}: {signal_type} @ {entry_price:.5f} "
                        f"(confidence: {confidence:.3f})"
                    )
            else:
                logger.warning("⚠️  No signals could be generated")

            await self.trading_engine.data_provider.disconnect()

        except Exception as e:
            logger.error(f"Error generating sample signals: {e}")

    def print_system_info(self):
        """Print system information"""
        logger.info("=" * 60)
        logger.info(f"🚀 {config.get('system.name')}")
        logger.info("   Advanced AI-Powered Forex Signal Generator")
        logger.info("=" * 60)
        symbols = config.get("trading.symbols", [])
        logger.info(f"📊 Symbols: {', '.join(symbols)}")
        timeframes = config.get("trading.timeframes", [])
        logger.info(f"⏰ Timeframes: {', '.join(timeframes)}")
        primary_tf = config.get("trading.primary_timeframe", "H1")
        logger.info(f"🎯 Primary Timeframe: {primary_tf}")
        ensemble_size = config.get("ai_models.ensemble_size", 5)
        logger.info(f"🤖 AI Models: {ensemble_size} ensemble models")
        max_risk = config.get("risk_management.max_risk_per_trade", 0.02)
        logger.info(f"📈 Max Risk per Trade: {max_risk:.1%}")
        interval = config.get("trading.signal_generation_interval", 300)
        logger.info(f"⚡ Signal Generation: Every {interval} seconds")
        output_dir = config.get("spreadsheet.output_directory")
        logger.info(f"💾 Output Directory: {output_dir}")
        logger.info("=" * 60)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="GenX FX Trading System")
    parser.add_argument(
        "mode",
        choices=["live", "train", "backtest", "test", "sample"],
        help="System mode to run",
    )
    parser.add_argument(
        "--symbols", nargs="+", help="Symbols to trade (for training/backtesting)"
    )
    parser.add_argument(
        "--timeframes", nargs="+", help="Timeframes to use (for training)"
    )
    parser.add_argument(
        "--start-date", type=str, help="Start date for backtesting (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date", type=str, help="End date for backtesting (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--count", type=int, default=5, help="Number of sample signals to generate"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(level=args.log_level)

    # Initialize system
    system = GenXTradingSystem()
    system.print_system_info()

    # Start health check server for Cloud Run
    port = int(os.environ.get("PORT", 8080))
    system.start_health_server(port=port)

    try:
        if args.mode == "live":
            await system.run_live_trading()
        elif args.mode == "train":
            await system.run_training_mode(args.symbols, args.timeframes)
        elif args.mode == "backtest":
            await system.run_backtesting(args.start_date, args.end_date)
        elif args.mode == "test":
            await system.run_test_mode()
        elif args.mode == "sample":
            await system.generate_sample_signals(args.count)

    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 System error: {e}")
        sys.exit(1)

    logger.info("🏁 GenX Trading System stopped")


if __name__ == "__main__":
    asyncio.run(main())
