#!/usr/bin/env python3
"""
Quick setup script for trading bot
"""
import os
import shutil

def setup():
    """Setup the trading bot environment"""
    print("="*60)
    print("Trading Bot Setup - A6-9V")
    print("="*60)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n1. Creating .env file from template...")
        if os.path.exists('.env.template'):
            shutil.copy('.env.template', '.env')
            print("✓ .env file created")
            print("\n⚠️  IMPORTANT: Edit .env file and add your API keys!")
            print("   Get testnet keys from: https://testnet.binance.vision/")
        else:
            print("✗ .env.template not found")
    else:
        print("\n✓ .env file already exists")
    
    # Create __init__.py files for Python modules
    print("\n2. Setting up Python modules...")
    modules = [
        'src',
        'src/exchange',
        'src/execution', 
        'src/strategies'
    ]
    
    for module in modules:
        init_file = os.path.join(module, '__init__.py')
        if not os.path.exists(init_file):
            os.makedirs(module, exist_ok=True)
            open(init_file, 'a').close()
            print(f"✓ Created {init_file}")
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python src/main.py")
    print("\n⚠️  Make sure testnet is set to 'true' in config.yaml for paper trading!")
    print("="*60)

if __name__ == "__main__":
    setup()
