#!/usr/bin/env python3
"""
Demo script to test the trading bot with paper trading
This creates a simulated environment for testing
"""
import asyncio
import os
import sys

# Set demo environment variables if not present
if not os.getenv('BINANCE_API_KEY'):
    print("⚠️  No API keys found in environment")
    print("Setting up DEMO mode with simulated trading...")
    print("\nFor real trading:")
    print("1. Get API keys from https://testnet.binance.vision/")
    print("2. Add them to .env file")
    print("3. Run: python src/main.py\n")
    
    # Set placeholder keys for demo
    os.environ['BINANCE_API_KEY'] = 'DEMO_KEY'
    os.environ['BINANCE_API_SECRET'] = 'DEMO_SECRET'
    os.environ['ORGANIZATION'] = 'A6-9V'
    os.environ['USER'] = 'mouy-leng'

# Import after setting environment
sys.path.insert(0, 'src')

async def demo():
    """Run demo"""
    print("="*60)
    print("AUTONOMOUS TRADING BOT - DEMO MODE")
    print("A6-9V Organization")
    print("="*60)
    print("\nThis demo shows how the bot works.")
    print("To trade for real:")
    print("1. Get Binance testnet API keys")
    print("2. Add keys to .env file")
    print("3. Run: python src/main.py")
    print("\n" + "="*60 + "\n")
    
    # Show what would happen
    print("Bot initialization sequence:")
    print("✓ Load configuration from config.yaml")
    print("✓ Connect to exchange (Binance)")
    print("✓ Initialize order manager")
    print("✓ Load trading strategy (Momentum)")
    print("✓ Check account balance")
    print("\nTrading cycle would:")
    print("✓ Analyze market data every 60 seconds")
    print("✓ Generate BUY/SELL/HOLD signals")
    print("✓ Execute orders based on momentum strategy")
    print("✓ Monitor order execution")
    print("✓ Track performance statistics")
    
    print("\n" + "="*60)
    print("Ready to start real trading? Follow the setup steps above!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(demo())
